from ..emails import Email
from django.conf import settings
from django.template.loader import render_to_string
from .utils import initial_email_verification_token_generator, EmailVerificationUtils
from django.core.mail import send_mail


class InitialVerificationEmail(Email):
    """
    This class derives from the SingleEmail abstract class
    Its responsibility is sending initial verification emails
    """
    def send(self):
        domain = settings.FRONT_END
        message = render_to_string('verification_email_template.html', {
                                'user': self.target,
                                'domain': domain,
                                'uid': EmailVerificationUtils.encode_user(self.target),
                                'token': initial_email_verification_token_generator.make_token(self.target),
        })
        to_email = self.target.email
        send_mail('Verify your account and start your journey!', message, settings.EMAIL_HOST_USER, [to_email],
                  fail_silently=False)
