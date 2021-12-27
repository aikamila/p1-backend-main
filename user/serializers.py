from rest_framework.serializers import ModelSerializer, Serializer
from django.contrib.auth import get_user_model
from .emails.verification.emails import InitialVerificationEmail
import re
from rest_framework import serializers
from .emails.emails import EmailDispatcher


class CreateUserSerializer(ModelSerializer):
    """
    User creation and sending verification emails
    """
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'name',
                  'surname', 'bio', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_name(self, value):
        pattern = re.compile(r'^[A-Z]{1}[a-z]+ ?[A-Z]?[a-z]*$')
        if pattern.fullmatch(value) is None:
            raise serializers.ValidationError("Invalid format of the name")
        return value

    def validate_surname(self, value):
        pattern = re.compile(r'^[A-Z]{1}[a-z]+[- ]?[A-Z]?[a-z]*$')
        if pattern.fullmatch(value) is None:
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

        def check_alnum(ch):
            return ch.isalnum()

        result = map(check_alnum, value)
        if not all(list(result)):
            raise serializers.ValidationError("Password must contain only letters, numbers and *, &, @")
        result = 1
        for char in value:
            if char.isupper():
                result = result * 0
        if result == 1:
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        return value

    def save(self, **kwargs):
        # you cant just use super bc normal save doesnt save passwords in a normal way
        model = get_user_model()
        user = model.objects.create_user(email=self.validated_data['email'],
                                         name=self.validated_data['name'],
                                         surname=self.validated_data['surname'],
                                         username=self.validated_data['username'],
                                         password=self.validated_data['password'])
        if user:
            # not really necessary but I prefer to be cautious
            email = InitialVerificationEmail(user)
            dispatcher = EmailDispatcher(email)
            dispatcher.send()

