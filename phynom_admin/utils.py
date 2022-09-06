import re
from backend.settings import *
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework import status

def email_validator(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    email_validation = re.search(regex, email)
    return email_validation


def admin_send_email(url, users):
    email_from = DEFAULT_FROM_EMAIL
    message_body = "Please click {} to update your password".format(url)
    email1 = EmailMessage("Email ",
                          message_body, email_from, [users.email])
    email1.content_subtype = 'html'
    email1.send()


def password_check(passwd):
    SpecialSym = ['$', '@', '#', '%']
    val_string = "Password updated successfully!"
    if len(passwd) < 8:
        val_string = 'length should be at least 8'
        return val_string

    elif len(passwd) > 20:
        val_string = 'length should be not be greater than 20'
        return val_string
    elif not any(char.isdigit() for char in passwd):
        val_string = 'Password should have at least one numeral'
        return val_string

    elif not any(char.isupper() for char in passwd):
        val_string = 'Password should have at least one uppercase letter'
        return val_string

    elif not any(char.islower() for char in passwd):
        return val_string

    elif not any(char in SpecialSym for char in passwd):
        val_string = 'Password should have at least one of the symbols like "$@#%"'
        return val_string
    else:
        return val_string


def True_Response(msg, serializer):
    return Response({
        "status": True, "status_code": 200, 'msg': msg,
        "data": serializer.data}, status=status.HTTP_200_OK)

def Exception_Response(e):
    return Response({
        "status": False, "status_code": 400, 'msg': e.args[0],
        "data": []}, status=status.HTTP_400_BAD_REQUEST)