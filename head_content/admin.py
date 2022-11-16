from django.contrib import admin

from .models import HeadContent
from .models import Banner
from .models import Usl
from .models import Article
from .models import VizCart
from .models import Osv


class BannerInline(admin.TabularInline):
    model = Banner
    extra = 0


class UslInline(admin.TabularInline):
    model = Usl
    extra = 0


@admin.register(HeadContent)
class HeadContentAdmin(admin.ModelAdmin):
    inlines = (BannerInline, UslInline,)
    list_display = ("name", )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("head", )
    search_fields = ("head", )


@admin.register(VizCart)
class VizCartAdmin(admin.ModelAdmin):
    list_display = ("adr", )


@admin.register(Osv)
class OsvAdmin(admin.ModelAdmin):
    list_display = ("name", )

