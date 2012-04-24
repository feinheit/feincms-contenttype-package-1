from django.db import models


class ChildrenContent(models.Model):
    """Renders all the Children of a given FeinCMS Page. Usefull for SEO and overviews """

    parent_page = models.ForeignKey(Page, blank=True, null=True,
                                    related_name="%(app_label)s_%(class)s_related")

    class Meta:
        abstract = True

    def render(self, request, context, **kwargs):
        if self.parent_page:
            parent_page = self.parent_page
        else:
            parent_page = self.parent

        return render_to_string('content/children/default.html',
                                {'parent_page' : parent_page},
                                RequestContext(request))