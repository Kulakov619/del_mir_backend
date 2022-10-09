from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('openapi', get_schema_view(
            title="dm_backend",
            authentication_classes=[],
            permission_classes=[],
            version="1.0"
        ), name='openapi-schema'),
    path('', lambda request: redirect('docs/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authcore.urls')),
    re_path(r'^docs/', include_docs_urls(title='dm_backend', public=True)),

]
