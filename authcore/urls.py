from django.urls import path
from authcore import views

urlpatterns = [
    path("otp/", views.OTPView.as_view(), name="OTP"),
    path("registration/", views.OTPLoginView.as_view(), name="OTP-Register-LogIn"),
    path("isunique/", views.CheckUniqueView.as_view(), name="Check Unique"),
    path(
        "account/",
        views.RetrieveUpdateUserAccountView.as_view(),
        name="Retrieve Update Profile",
    ),
    path(
        "refresh-token/", views.CustomTokenRefreshView.as_view(), name="refresh_token"
    ),
]
