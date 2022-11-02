from django.conf import settings
from django.utils import timezone
from django.utils.text import gettext_lazy as _
import json
from django.http import HttpResponse
from rest_framework import status, generics, mixins
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.views import TokenRefreshView

from .models import AuthTransaction
from .models import User
from .models import DopMobile, Address
from .serializers import CheckUniqueSerializer
from .serializers import CustomTokenObtainPairSerializer
from .serializers import OTPLoginRegisterSerializer
from .serializers import OTPSerializer
from .serializers import PasswordResetSerializer
from .serializers import UserSerializer, DopMobileSerializer, AddressSerializer
from .utils import check_unique
from .utils import generate_otp
from .utils import get_client_ip
from .utils import login_user
from .utils import send_otp
from .utils import validate_otp, json_serial
from .variables import EMAIL
from .variables import MOBILE
from .permission import IsUserUpdate, IsUserChUpdate


class JsonResponse(HttpResponse):

    def __init__(self, content, status=None, content_type='application/json'):
        data = dict()
        data['data'] = content
        data['status_code'] = status
        json_text = json.dumps(data, default=json_serial)
        super(JsonResponse, self).__init__(
            content=json_text,
            status=status,
            content_type=content_type)


class CheckUniqueView(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (AllowAny,)
    serializer_class = CheckUniqueSerializer

    def validated(self, serialized_data, *args, **kwargs):

        return (
            {
                "unique": check_unique(
                    serialized_data.validated_data["prop"],
                    serialized_data.validated_data["value"],
                )
            },
            status.HTTP_200_OK,
        )

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid():
            return JsonResponse(self.validated(serialized_data=serialized_data))
        else:
            return JsonResponse(
                serialized_data.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


class OTPView(APIView):

    permission_classes = (AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        destination = serializer.validated_data.get("destination")
        prop = serializer.validated_data.get("prop")
        user = serializer.validated_data.get("user")
        email = serializer.validated_data.get("email")
        is_login = serializer.validated_data.get("is_login")
        id_mob = serializer.validated_data.get("id_mob")

        if "verify_otp" in request.data.keys():
            if validate_otp(destination, request.data.get("verify_otp")):
                if is_login:
                    return Response(
                        login_user(user, self.request), status=status.HTTP_202_ACCEPTED
                    )
                elif id_mob:
                    dm = DopMobile.objects.get(pk=id_mob)
                    dm.confirmed = True
                    dm.save()
                    return Response(
                        data={
                            "Одноразовый пароль": [
                                _("Код успешно принят!"),
                            ]
                        },
                        status=status.HTTP_202_ACCEPTED,
                    )
                else:
                    return Response(
                        data={
                            "Одноразовый пароль": [
                                _("Код успешно принят!"),
                            ]
                        },
                        status=status.HTTP_202_ACCEPTED,
                    )
        else:
            otp_obj = generate_otp(prop, destination)
            sentotp = send_otp(destination, otp_obj, email)

            if sentotp["success"]:
                otp_obj.send_counter += 1
                otp_obj.save()

                return Response(sentotp, status=status.HTTP_201_CREATED)
            else:
                raise APIException(
                    detail=_("A Server Error occurred: " + sentotp["message"])
                )


class OTPLoginView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)
    serializer_class = OTPLoginRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        verify_otp = serializer.validated_data.get("verify_otp", None)
        lastname = serializer.validated_data.get("lastname")
        name = serializer.validated_data.get("name")
        mobile = serializer.validated_data.get("mobile")
        email = serializer.validated_data.get("email")
        user = serializer.validated_data.get("user", None)

        message = {}

        if verify_otp:
            if validate_otp(email, verify_otp) and not user:
                user = User.objects.create_user(
                    name=name,
                    mobile=mobile,
                    email=email,
                    username=mobile,
                    password=User.objects.make_random_password(),
                )
                user.is_active = True
                user.last_name = lastname
                user.save()
            return Response(
                login_user(user, self.request), status=status.HTTP_202_ACCEPTED
            )

        else:
            otp_obj_email = generate_otp(EMAIL, email)
            otp_obj_mobile = generate_otp(MOBILE, mobile)

            # Set same OTP for both Email & Mobile
            otp_obj_mobile.otp = otp_obj_email.otp
            otp_obj_mobile.save()

            # Send OTP to Email & Mobile
            sentotp_email = send_otp(email, otp_obj_email, email)
            sentotp_mobile = send_otp(mobile, otp_obj_mobile, email)

            if sentotp_email["success"]:
                otp_obj_email.send_counter += 1
                otp_obj_email.save()
                message["email"] = {"КОД": _("Проверочный код успешно отправлен на почту.")}
            else:
                message["email"] = {
                    "otp": _(f'Код не отпрален: {sentotp_email["message"]}')
                }

            if sentotp_mobile["success"]:
                otp_obj_mobile.send_counter += 1
                otp_obj_mobile.save()
                message["mobile"] = {"КОД": _("Проверочный код успешно отправлен по СМС.")}
            else:
                message["mobile"] = {
                    "Пароль": _(f'Код не отпрален: {sentotp_mobile["message"]}')
                }

            if sentotp_email["success"] or sentotp_mobile["success"]:
                curr_status = status.HTTP_201_CREATED
            else:
                raise APIException(
                    detail=_("Сервер не доступен: " + sentotp_mobile["message"])
                )

            return Response(data=message, status=curr_status)


class UploadImageView(APIView):
    from .models import User
    from .serializers import ImageSerializer
    from rest_framework.permissions import IsAuthenticated
    from rest_framework.parsers import MultiPartParser

    queryset = User.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticated,)
    parser_class = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        from .serializers import ImageSerializer
        from rest_framework.response import Response
        from rest_framework import status

        image_serializer = ImageSerializer(data=request.data)

        if not image_serializer.is_valid():
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image_serializer.update(
            instance=request.user, validated_data=image_serializer.validated_data
        )
        return Response(
            {"detail": "Profile Image Uploaded."}, status=status.HTTP_201_CREATED
        )


class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token = serializer.validated_data.get("access")

        auth_transaction = AuthTransaction.objects.get(
            refresh_token=request.data["refresh"]
        )
        auth_transaction.token = token
        auth_transaction.expires_at = (
            timezone.now() + api_settings.ACCESS_TOKEN_LIFETIME
        )
        auth_transaction.save(update_fields=["token", "expires_at"])

        return Response({"token": str(token)}, status=status.HTTP_200_OK)


class UserView(mixins.RetrieveModelMixin,
               mixins.UpdateModelMixin,
               GenericViewSet
               ):
    permission_classes = (IsUserUpdate,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DmView(mixins.RetrieveModelMixin,
             mixins.CreateModelMixin,
             mixins.DestroyModelMixin,
             GenericViewSet):
    permission_classes = (IsUserChUpdate, )
    queryset = DopMobile.objects.all()
    serializer_class = DopMobileSerializer


class AddressView(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    permission_classes = (IsUserChUpdate, )
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

