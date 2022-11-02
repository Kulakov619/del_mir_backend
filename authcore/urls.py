from django.urls import path, include
from authcore import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'user', views.UserView)
router.register(r'user_dm', views.DmView)
router.register(r'user_adr', views.AddressView)

urlpatterns = [
    path("otp/", views.OTPView.as_view(), name="login"),
    path("registration/", views.OTPLoginView.as_view(), name="registration"),
    path("isunique/", views.CheckUniqueView.as_view(), name="check unique"),
    path("", include(router.urls)),
    path(
        "refresh-token/", views.CustomTokenRefreshView.as_view(), name="refresh_token"
    ),
]
