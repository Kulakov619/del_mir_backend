from rest_framework import serializers

from .models import HeadContent
from .models import Banner
from .models import Usl
from .models import Article
from .models import VizCart
from .models import Osv


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = (
            'id',
            'por',
            'img'
        )


class UslSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usl
        fields = (
            'id',
            'por',
            'img',
            'head',
            'text'
        )


class HeadContentSerializer(serializers.ModelSerializer):
    banner = serializers.SerializerMethodField()
    usl = serializers.SerializerMethodField()


    def get_banner(self, obj):
        q = Banner.objects.filter(is_active=True)
        serializer = BannerSerializer(q, many=True)

        return serializer.data

    def get_usl(self, obj):
        q = Usl.objects.filter(is_active=True)
        serializer = UslSerializer(q, many=True)

        return serializer.data

    class Meta:
        model = HeadContent
        fields = (
            'r_type_1',
            'r_type_2',
            'r_type_3',
            'r_type_4',
            'r_type_5',
            'r_type_6',
            'r_acc',
            'tpt',
            'pok',
            'tit_1',
            'tex_1',
            'img_1',
            'tit_2',
            'tex_2',
            'img_2',
            'tit_3',
            'tex_3',
            'img_3',
            'tit_4',
            'tex_4',
            'img_4',
            'banner',
            'usl'
        )


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = (
            'id',
            'head',
            'text',
            'created',
        )


class VizCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = VizCart
        exclude = ['created', 'updated']


class OsvSerializer(serializers.ModelSerializer):

    class Meta:
        model = Osv
        fields = (
            'name',
            'tp',
        )
