from rest_framework import status, generics, mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import HeadContent
from .models import Article
from .models import VizCart
from .models import Osv
from .serializers import HeadContentSerializer
from .serializers import ArticleSerializer
from .serializers import VizCartSerializer
from .serializers import OsvSerializer


class HeadContentView(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = HeadContent.objects.all()
    serializer_class = HeadContentSerializer


class ArticleView(mixins.ListModelMixin, GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class VizCartView(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = VizCart.objects.all()
    serializer_class = VizCartSerializer


class OsvView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Osv.objects.all()
    serializer_class = OsvSerializer

