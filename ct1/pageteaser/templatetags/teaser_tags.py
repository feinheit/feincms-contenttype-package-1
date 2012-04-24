#coding=utf-8
from django import template
from feincms.module.page.models import Page
from django.conf import settings


register = template.Library()

@register.simple_tag(takes_context=True)
def collect_featured(context):
    items = []
    if 'elephantblog' in settings.INSTALLED_APPS:
        from elephantblog.models import Entry
        items.extend([e for e in Entry.objects.featured()])
    items.extend([p for p in Page.objects.filter(featured=True).order_by('-modification_date')])
    context['featured'] = items
    return ''
