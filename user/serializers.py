from django.contrib.auth import get_user_model
from .emails.verification.emails import InitialVerificationEmail
import re
from rest_framework import serializers
from .emails.emails import EmailDispatcher


class BasicInfoUserSerializer(serializers.ModelSerializer):
    """Basic information about a user"""
    class Meta:
        model = get_user_model()
        fields = ('username', "id")


class UserSerializer(BasicInfoUserSerializer):
    """
    Extended information about the user. Class responsible for user creation, validation
    of data and sending verification emails.
    """
    class Meta(BasicInfoUserSerializer.Meta):
        fields = BasicInfoUserSerializer.Meta.fields + ('email', 'name', 'surname', 'bio', 'password')
        extra_kwargs = {'password': {'write_only': True}, "id": {'read_only': True}}

    def validate_name(self, value):
        pattern = re.compile(r'^[A-Za-z]+ {1}[A-Za-z]+$|^[A-Za-z]+$')
        if pattern.fullmatch(value.strip()) is None:
            raise serializers.ValidationError("Invalid format of the name")
        return value

    def validate_surname(self, value):
        pattern = re.compile(r'^[A-Za-z]+[ -]{1}[A-Za-z]+$|^[A-Za-z]+$')
        if pattern.fullmatch(value.strip()) is None:
            raise serializers.ValidationError("Invalid format of the surname")
        return value

    def validate_username(self, value):
        pattern = re.compile(r'^[a-zA-Z0-9_.-]{3,30}$')
        if pattern.fullmatch(value) is None:
            raise serializers.ValidationError("Invalid format of the username")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")

        result = 1
        for char in value:
            if char.isupper():
                result = result * 0
        if result == 1:
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        return value

    def create(self, validated_data):
        # you cant just use super bc normal save doesnt save passwords in a proper way
        # you must remember that [] notation on a dictionary will raise KeyError if a given key doesn't exist
        # it is better to use get in case of fields that are not required
        # or just use **validated_data
        model = get_user_model()
        user = model.objects.create_user(email=self.validated_data['email'],
                                         name=self.validated_data['name'],
                                         surname=self.validated_data['surname'],
                                         username=self.validated_data['username'],
                                         password=self.validated_data['password'],
                                         bio=self.validated_data.get('bio', ''))
        # email = InitialVerificationEmail(user)
        # dispatcher = EmailDispatcher(email)
        # dispatcher.send()
        return user
