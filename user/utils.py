import email
from django.core.mail import EmailMessage
import os
class Utill:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body= data['body'],
            # from_email=os.environ.get('EMAIL_FROM'),
            from_email="faisalmaqbool.spyresync@gmail.com",
            to = [data['to_email']]
        )
        email.send()