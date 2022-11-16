from django.urls import path, include
from head_content import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'head_content', views.HeadContentView)
router.register(r'article', views.ArticleView)
router.register(r'contact', views.VizCartView)
router.register(r'call_back', views.OsvView)

urlpatterns = [
    path("", include(router.urls)),
]