from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.text import gettext_lazy as _

from authcore.models import TimeStampedMixin


class HeadContent(TimeStampedMixin):
    name = models.CharField(_('название'), max_length=32)
    r_type_1 = models.CharField(_('тип радиаторов 1'), max_length=32)
    r_type_2 = models.CharField(_('тип радиаторов 2'), max_length=32)
    r_type_3 = models.CharField(_('тип радиаторов 3'), max_length=32)
    r_type_4 = models.CharField(_('тип радиаторов 4'), max_length=32)
    r_type_5 = models.CharField(_('тип радиаторов 5'), max_length=32)
    r_type_6 = models.CharField(_('тип радиаторов 6'), max_length=32)
    r_acc = models.CharField(_('аксессуары'), max_length=32)
    tpt = models.CharField(_('теплотехника'), max_length=32)
    pok = models.CharField(_('покраска'), max_length=32)
    tit_1 = models.CharField(_('заголовок 1'), max_length=255)
    tex_1 = models.TextField(_("текст 1"))
    img_1 = models.ImageField(
        verbose_name=_("картинка 1"),
        upload_to="img/gl",
    )
    tit_2 = models.CharField(_('заголовок 2'), max_length=255)
    tex_2 = models.TextField(_("текст 2"))
    img_2 = models.ImageField(
        verbose_name=_("картинка 2"),
        upload_to="img/gl",
    )
    tit_3 = models.CharField(_('заголовок 3'), max_length=255)
    tex_3 = models.TextField(_("текст 3"))
    img_3 = models.ImageField(
        verbose_name=_("картинка 3"),
        upload_to="img/gl", blank=True
    )
    tit_4 = models.CharField(_('заголовок 4'), max_length=255)
    tex_4 = models.TextField(_("текст 4"))
    img_4 = models.ImageField(
        verbose_name=_("картинка 4"),
        upload_to="img/gl", blank=True
    )

    class Meta:
        verbose_name = _('главная страница')
        verbose_name_plural = _('главная страница')


class Banner(TimeStampedMixin):
    hc = models.ForeignKey(HeadContent, on_delete=models.CASCADE)
    por = models.IntegerField(verbose_name=_("порядок (целое число)"), blank=True)
    img = models.ImageField(
        verbose_name=_("баннер"),
        upload_to="img/banners",
    )
    is_active = models.BooleanField(verbose_name=_("опубликован"), default=True)

    class Meta:
        verbose_name = _("баннер")
        verbose_name_plural = _("баннеры")
        ordering = ['por', ]


class Usl(TimeStampedMixin):
    hc = models.ForeignKey(HeadContent, on_delete=models.CASCADE)
    por = models.IntegerField(verbose_name=_("порядок (целое число)"), blank=True)
    img = models.ImageField(
        verbose_name=_("фото"),
        upload_to="img/usl",
    )
    head = models.CharField(_('заголовок'), max_length=255)
    text = models.TextField(_("описание"))
    is_active = models.BooleanField(verbose_name=_("опубликован"), default=True)

    class Meta:
        verbose_name = _("услуга")
        verbose_name_plural = _("услуги")
        ordering = ['por', ]


class Article(TimeStampedMixin):
    head = models.CharField(_('заголовок'), max_length=255)
    text = models.TextField(_("текст cтатьи"))

    class Meta:
        verbose_name = _("статьи")
        verbose_name_plural = _("статьи")
        ordering = ['created', ]


class VizCart(TimeStampedMixin):
    time_call = models.CharField(_('время работы call-центра'), max_length=64)
    time_shop = models.CharField(_('время работы магазина'), max_length=64)
    text = models.TextField(_("дополнительная информация"))
    inst = models.CharField(_('инстаграмм'), max_length=255)
    vk = models.CharField(_('вк'), max_length=255)
    wa = models.CharField(_('whatsapp'), max_length=255)
    tg = models.CharField(_('telegram'), max_length=255)
    em = models.EmailField(_('электронная почта'))
    tp = models.CharField(_('телефон'), max_length=255)
    adr = models.CharField(_('адрес офиса'), max_length=255)

    class Meta:
        verbose_name = _("контакты")
        verbose_name_plural = _("контакты")


class Osv(TimeStampedMixin):
    name = models.CharField(_('имя'), max_length=64)
    tp = models.CharField(_('телефон'), max_length=32)
    is_used = models.BooleanField(verbose_name=_("отработан"), default=False)

    class Meta:
        verbose_name = _("обратный звонок")
        verbose_name_plural = _("обратные звонки")
        ordering = ['created', ]