from feincms.module.page.models import Page

def page_list_lookup_related(entry_qs):
    entry_dict = dict((e.pk, e) for e in entry_qs)

    if hasattr(Page, 'teasercontent_set'):
        for content in Page.teasercontent_set.related.model.objects.filter(
                parent__in=entry_dict.keys()).reverse():
            entry_dict[content.parent_id].first_teaser = content

#    if hasattr(Page, 'richtextcontent_set'):
#        for content in Page.richtextcontent_set.related.model.objects.filter(
#                parent__in=entry_dict.keys()).reverse():
#            entry_dict[content.parent_id].first_richtext = content
