# coding=utf-8

from django import forms
from django.db import models
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from feincms import settings as feincms_settings
from feincms.admin.editor import ItemEditorForm
from feincms.content.medialibrary.models import MediaFileWidget
from feincms.content.richtext.models import RichTextContentAdminForm
from feincms.module.medialibrary.models import MediaFile
from feincms.module.page.models import Page
from feincms.admin.item_editor import FeinCMSInline
from django.contrib import admin
from django.db.utils import DatabaseError

class PageTeaserContent(models.Model):
    """ 
        This Content Type extracts the first Richtext element and the first image and 
        displays them. You can configure it to use a different template directory i.e.
        when you would like to use the same templates as the section content type.
        
        Page.create_content_type(PageTeaserContent, regions='main', 
                                template_dir='section', type='page', region='main')
    """
    
    @classmethod
    def initialize_type(cls, template_dir='pageteaser', type='teaser', media_types=['image'], region='main', PAGE_CLASS=Page):
        cls.template_dir = template_dir
        cls.type = type
        cls.media_types = media_types
        cls.region = region
        class PageTeaserContentAdminForm(ItemEditorForm):
            try:
                # FIXME: ForeignKeyRawIdWidget still displays inactive pages. At least there is an error when you try to save.
                page = forms.ModelChoiceField(queryset=PAGE_CLASS.objects.tree_active(),
                    widget=ForeignKeyRawIdWidget(PageTeaserContent._meta.get_field('page').rel),
                    label=_('Page'))
            except (AttributeError, DatabaseError):
                page = forms.ModelChoiceField(queryset=PAGE_CLASS.objects.active(),
                    widget=ForeignKeyRawIdWidget(PageTeaserContent._meta.get_field('page').rel),
                    label=_('Page'))
        
        cls.feincms_item_editor_form = PageTeaserContentAdminForm
    
    page = models.ForeignKey(Page, related_name="%(app_label)s_%(class)s_related")
    
    class Meta:
        verbose_name = _('Page Teaser')
        verbose_name_plural = _('Page Teasers')
        abstract = True
        
    def __unicode___(self):
        return self.page 
    
    def render(self, **kwargs):
        if not self.page.is_active():
            return ''
        request = kwargs.get('request')
        self.title = self.page.title
        try:
            self.richtext = self.page.richtextcontent_set.filter(region=self.region)[0].render
        except IndexError:
            pass
        try:
            for mediafilecontent in self.page.mediafilecontent_set.all():
                if mediafilecontent.mediafile.type in self.media_types:
                    self.mediafile = mediafilecontent.mediafile
                    mediafile_type = mediafilecontent.mediafile.type
                    break
            else: #No image found
                self.mediafile = None
                mediafile_type = 'nomedia'
        except IndexError:
                self.mediafile = None
                mediafile_type = 'nomedia'
        return render_to_string(['content/%s/%s_%s.html' %(self.template_dir, self.type, mediafile_type),
                                 'content/%s/%s.html' %(self.template_dir, self.type),
                                 'content/%s/teaser.html' %self.template_dir],
                                {'content': self, 'page':self.page }, context_instance=RequestContext(request))


class CustomPageTeaserContent(models.Model):
    """Creates a Page Teaser, but with customizable fields: MediaFile (Image, Video), TextField, Title, Target """
    
    feincms_item_editor_context_processors = (
        lambda x: feincms_settings.FEINCMS_RICHTEXT_INIT_CONTEXT,
    )
    
    title = models.CharField(max_length=60, blank=True)
    text = models.TextField(_('text'), blank=True)
    url = models.CharField(_('url'), max_length=200, blank=True, null=True)
    
    class Meta:
        abstract = True
        verbose_name = _('custom page teaser')
        verbose_name_plural = _('custom page teasers')
    
    @property
    def media(self):
        media = forms.Media()
        media.add_css({'all':('lib/fancybox/jquery.fancybox-1.3.1.css',)})
        media.add_js(('lib/fancybox/jquery.fancybox-1.3.1.pack.js',))
        return media
    
    @classmethod
    def initialize_type(cls, TYPES=(('default', 'default'),), PAGE_CLASS=Page):
        cls.add_to_class('mediafile', models.ForeignKey(MediaFile, blank=True, null=True, related_name='%s_%s_set' % (cls._meta.app_label, cls._meta.module_name)))
        cls.add_to_class('page', models.ForeignKey(PAGE_CLASS, blank=True, null=True, related_name='%s_%s_set' % (cls._meta.app_label, cls._meta.module_name)))
        cls.add_to_class('type', models.CharField(max_length=10, choices=TYPES, blank=False))
                    
        class RichTextContentAdminForm(ItemEditorForm):           
            def __init__(self, *args, **kwargs):
                super(RichTextContentAdminForm, self).__init__(*args, **kwargs)
                self.fields['text'].widget.attrs.update({'class': 'item-richtext'})

        class CustomPageTeaserContentInline(FeinCMSInline):           
            raw_id_fields = ('mediafile', 'page')
            radio_fields = {'type': admin.VERTICAL }
            form = RichTextContentAdminForm
        
        cls.feincms_item_editor_inline = CustomPageTeaserContentInline
        
    def clean(self):
        super(CustomPageTeaserContent, self).clean()
        if not self.url and not self.page:
            raise ValidationError('You need to set a link url or page.')
        
        
    def render(self, request, context, **kwargs):
        self.link = self.url if self.url else self.page.get_absolute_url()
        return render_to_string(['content/pageteaser/%s.html' % self.type, 'content/pageteaser/default.html'], 
                                {'content': self,}, context_instance=RequestContext(request))
        

class TeaserContent(models.Model):
    """ Creates a Teaser for the current page. Use a separate region and the featured extension.
    
        Page.create_content_type(TeaserContent, TYPES=TEASE_LAYOUT_CHOICES, regions=('teaser',))
        Entry.create_content_type(TeaserContent, TYPES=TEASE_LAYOUT_CHOICES, regions=('teaser',))
       
        Add feinheit.pageteaser to your INSTALLED_APPS or copy the template tag file.
       
        Add the blog reigons to your settings file if you use elephantblog:
        BLOG_REGIONS = (('main', ugettext_lazy('Main content area')),
                       ('teaser', ugettext_lazy('Teaser content area'))
        )                         
    """
    
    feincms_item_editor_context_processors = (
        lambda x: feincms_settings.FEINCMS_RICHTEXT_INIT_CONTEXT,
    )
    feincms_item_editor_includes = {
        'head': ['admin/pageteaser/include.html'],
    }
    
    text = models.TextField(_('text'), blank=True)
    
    class Meta:
        abstract = True
        verbose_name = _('Teaser')
        verbose_name_plural = _('Teasers')
    
    @property
    def media(self):
        media = forms.Media()
        media.add_css({'all':('lib/fancybox/jquery.fancybox-1.3.1.css',)})
        media.add_js(('lib/fancybox/jquery.fancybox-1.3.1.pack.js',))
        return media
    
    @classmethod
    def initialize_type(cls, TYPES=(('default', 'default'),), PAGE_CLASS=Page):
        
        cls.add_to_class('mediafile', models.ForeignKey(MediaFile, blank=True, null=True, 
                    related_name='%s_%s_set' % (cls._meta.app_label, cls._meta.module_name),
                    verbose_name=_('Teaser image')))
        cls.add_to_class('type', models.CharField(max_length=10, choices=TYPES, blank=False))
                    
        class RichTextContentAdminForm(ItemEditorForm):           
            def __init__(self, *args, **kwargs):
                super(RichTextContentAdminForm, self).__init__(*args, **kwargs)
                self.fields['text'].widget.attrs.update({'class': 'item-richtext'})

        class CustomPageTeaserContentInline(FeinCMSInline):           
            raw_id_fields = ('mediafile',)
            radio_fields = {'type': admin.VERTICAL }
            form = RichTextContentAdminForm
        
        cls.feincms_item_editor_inline = CustomPageTeaserContentInline
        
        
    def render(self, request, context, **kwargs):
        self.title = self.parent.title
        self.link = self.parent.get_absolute_url()
        return render_to_string(['content/pageteaser/%s.html' % self.type, 'content/pageteaser/default.html'], 
                                {'content': self,}, context_instance=RequestContext(request))

        
class ChildrenTeaserContent(models.Model):
    """ renders the teaser region of ALL children elements. """
    class Meta:
        abstract = True
        verbose_name = _('Unterseiten-Teaser')
        verbose_name_plural = _('Unterseiten-Teaser')
    
    def __unicode__(self):
        return unicode(self.parent.title)
    
    def render(self, request, **kwargs):
        children = self.parent.children.active()
        return render_to_string('content/pageteaser/children.html', {'children': children },
                                context_instance=RequestContext(request))

