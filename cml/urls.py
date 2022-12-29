from __future__ import absolute_import
from django.urls import path, include
from . import views

app_urlpatterns = [
    path(r'^1c_exchange.php$', views.front_view, name='front_view'),
    path(r'^exchange$', views.front_view, name='front_view'),
]

urlpatterns = [
    path(r'^', include((app_urlpatterns, 'cml'), namespace='cml')),
]
