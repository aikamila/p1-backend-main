from rest_framework.serializers import ModelSerializer, Serializer
from django.contrib.auth import get_user_model
from .emails.verification.emails import InitialVerificationEmail
import re
from rest_framework import serializers


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
        pattern = re.compile(r'^[a-zA-Z0-9_.-]+$')
        if pattern.fullmatch(value) is None:
            raise serializers.ValidationError("Invalid format of the username")
        return value

    # should bio and password be validated in any way?

    def save(self, **kwargs):
        # you cant just use super bc normal save doesnt save passwords in a normal way
        model = get_user_model()
        user = model.objects.create_user(email=self.validated_data['email'],
                                         name=self.validated_data['name'],
                                         surname=self.validated_data['surname'],
                                         username=self.validated_data['username'],
                                         password=self.validated_data['password'])
        if user:
            # not really necessary but i prefer to be cautious
            email = InitialVerificationEmail(user)
            email.send()

