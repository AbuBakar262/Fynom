from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from user.models import *
from . utils import *
import functools
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.response import Response


class AdminForgetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get('email')
            request_for = request.data.get('request_for')
            if email:
                email_validation = email_validator(request.data.get('email'))
                if email_validation:
                    admin = User.objects.filter(email=request.data.get('email'), is_superuser=True)
                    if admin.exists():
                        hyperlink_format = '<a href="{link}">{text}</a>'
                        link_text = functools.partial(hyperlink_format.format)
                        if request_for:
                            if request_for == 'staging':
                                reset_link = 'https://master.dg345xpwq3nha.amplifyapp.com/resetPassword/' + \
                                             urlsafe_base64_encode(force_bytes(admin.first().pk)) + '/' + \
                                             PasswordResetTokenGenerator().make_token(admin.first()) + '/'
                                url = link_text(link=reset_link, text='here')
                                admin_send_email(url, admin.first())
                            elif request_for == 'master':
                                reset_link = 'master.dwezdsatdorjo.amplifyapp.com/auth/reset/' + urlsafe_base64_encode(
                                    force_bytes(admin.first().pk)) + '/' + PasswordResetTokenGenerator().make_token(
                                    admin.first()) + '/'
                                url = link_text(link=reset_link, text='here')
                                admin_send_email(url, admin.first())
                        else:
                            return Response({"status": False,
                                             "msg": "request_for is required"})

                        return Response({"status": True, "Response": "Password reset URL has been sent to your Email",
                                         "msg": "Password reset URL has been sent to your Email"})

                    else:
                        return Response(
                            {"status": False, "Response": "Email Does not exists", "msg": "Email Does not exists"})
                else:
                    return Response(
                        {"status": False, "msg":
                            "Please enter valid admin email"})
            else:
                return Response({"status": False, "msg": "Please enter your email"
                                 })

        except Exception as e:
            return Response({"status": False, "msg": "details are not correct",
                             "server_msg": e.args[-1]
                             })


class AdminResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        try:

            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid, is_superuser=True)
            except():
                user = None

            if user is not None and PasswordResetTokenGenerator().check_token(user, token):

                if request.data.get('new_password'):
                    password = request.data.get('new_password')

                    if not user:
                        return Response({"status": False, "msg": "Email does not exist"})
                    elif user.check_password(request.data.get('new_password')):
                        return Response({"status": False, "msg": "You cannot use an old password"})
                    elif request.data.get('confirm_password') != request.data.get('new_password'):
                        return Response({"status": False, "msg": "Passwords are not same"})
                    else:
                        pass_res = password_check(password)
                        if pass_res == "Password updated successfully!":
                            user.set_password(str(request.data.get('confirm_password')))
                            user.save()
                            return Response(
                                {"status": True, "msg": pass_res})
                        else:
                            return Response(
                                {"status": True, "msg": pass_res})
                else:
                    return Response({"status": False, "msg": "Please enter new_Password"})
            else:
                return Response({"status": False, "msg": "Link has been expired"})

        except Exception as e:
            return Response({"status": False, "msg": "details are not correct",
                             "server_msg": e.args[-1]
                             })
