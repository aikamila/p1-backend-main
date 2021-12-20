from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'name',
                  'surname', 'bio', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        super().save(**kwargs)








