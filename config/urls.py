from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('', lambda request: redirect('docs/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authcore.urls')),
]
