""" This module requires FeinCMS 1.7 """
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from feincms.module.medialibrary.models import MediaFile
from feincms.admin.item_editor import FeinCMSInline


class TwinInline(FeinCMSInline):
    fieldsets = (
        (None, {'fields': ('region', 'ordering')}),
        ('first box', {'fields': ('image1', 'title1', 'text1', ('link_text1', 'url1'))}),
        ('second box', {'fields': ('image2', 'title2', 'text2', ('link_text2', 'url2'))}),
    )
    raw_id_fields = ['image1', 'image2']


class TwinContent(models.Model):
    """ This content type displays two images with text and optional links.
        It breaks up the grid so the images are distributed evenly,
        while still being responsive.
    """
    image1 = models.ForeignKey(MediaFile, related_name='+')
    image2 = models.ForeignKey(MediaFile, related_name='+')
    title1 = models.CharField(_('title'), max_length=40, blank=True)
    title2 = models.CharField(_('title'), max_length=40, blank=True)
    text1 = models.TextField(_('text'))
    text2 = models.TextField(_('text'))
    link_text1 = models.CharField(_('link text'), max_length=40, blank=True)
    link_text2 = models.CharField(_('link text'), max_length=40, blank=True)
    url1 = models.URLField(_('URL'), blank=True)
    url2 = models.URLField(_('URL'), blank=True)

    feincms_item_editor_inline = TwinInline

    class Meta:
        abstract = True
        verbose_name = _('infobox twin')
        verbose_name_plural = _('infobox twins')


    def render(self, **kwargs):
        request = kwargs['request']
        return render_to_string('content/infobox/twin.html',
                                {'content': self}, RequestContext(request))


class TripletInline(FeinCMSInline):
    fieldsets = (
        (None, {'fields': ('region', 'ordering')}),
        ('first box', {'fields': ('image1', 'title1', 'text1', ('link_text1', 'url1'))}),
        ('second box', {'fields': ('image2', 'title2', 'text2', ('link_text2', 'url2'))}),
        ('third box', {'fields': ('image3', 'title3', 'text3', ('link_text3', 'url3'))}),
    )
    raw_id_fields = ['image1', 'image2', 'image3']


class TripletContent(models.Model):
    """ This content type displays three images with text and optional links.
        It breaks up the grid so the images are distributed evenly,
        while still being responsive.
    """
    image1 = models.ForeignKey(MediaFile, related_name='+')
    image2 = models.ForeignKey(MediaFile, related_name='+')
    image3 = models.ForeignKey(MediaFile, related_name='+')
    title1 = models.CharField(_('title'), max_length=40, blank=True)
    title2 = models.CharField(_('title'), max_length=40, blank=True)
    title3 = models.CharField(_('title'), max_length=40, blank=True)
    text1 = models.TextField(_('text'))
    text2 = models.TextField(_('text'))
    text3 = models.TextField(_('text'))
    link_text1 = models.CharField(_('link text'), max_length=40, blank=True)
    link_text2 = models.CharField(_('link text'), max_length=40, blank=True)
    link_text3 = models.CharField(_('link text'), max_length=40, blank=True)
    url1 = models.URLField(_('URL'), blank=True)
    url2 = models.URLField(_('URL'), blank=True)
    url3 = models.URLField(_('URL'), blank=True)

    feincms_item_editor_inline = TripletInline

    class Meta:
        abstract = True
        verbose_name = _('infobox triplet')
        verbose_name_plural = _('infobox triplets')


    def render(self, **kwargs):
        request = kwargs['request']
        return render_to_string('content/infobox/triplet.html',
                                {'content': self}, RequestContext(request))


