from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class NewsIndex(Page):
    "The index page for news"
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL, blank=True, null=True)
    news_per_page = models.IntegerField(default=10)

    content_panels = Page.content_panels + [
        FieldPanel('news_per_page'),
        MultiFieldPanel([
            ImageChooserPanel('image'),
        ], heading="News Logo Image"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        all_news = self.get_children().live()
        paginator = Paginator(all_news, self.news_per_page)
        page_requested = request.GET.get('page')
        try:
            news_on_page = paginator.page(page_requested)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            news_on_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            news_on_page = paginator.page(paginator.num_pages)
        context['news_on_page'] = news_on_page
        return context

class HomePage(Page):
    "A blank page for the home page"
    
    def get_context(self, request):
        # Update context to return only news or only fixed sections
        context = super().get_context(request)
        # newspages = NewsIndex.get_children().live().order_by('-first_published_at')
        newsindex = self.get_children().type(NewsIndex).first()
        context['newsindex'] = newsindex
        if newsindex is not None:
            newspages = InfoPage.objects.child_of(newsindex)[:3]
        else:
            newspages = None
        context['newspages'] = newspages
        columnsection = InfoPage.objects.filter(featuredInColumnSection=True)[:3]
        context['columnsection'] = columnsection
        rowsection = InfoPage.objects.filter(featuredInRowSection=True)
        context['rowsection'] = rowsection
        return context

class InfoPage(Page):
    date = models.DateField("Post date")
    body = RichTextField(blank=True)
    lead = models.CharField(max_length=250, blank=True)
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL, blank=True, null=True)
    caption = models.CharField(blank=True, max_length=250)
    featuredInColumnSection = models.BooleanField(default=False)
    featuredInRowSection = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('body', classname="full"),
        FieldPanel('lead'),
        MultiFieldPanel([
            FieldPanel('featuredInColumnSection'),
            FieldPanel('featuredInRowSection'),
        ], heading="Featured"),
        MultiFieldPanel([
            ImageChooserPanel('image'),
            FieldPanel('caption'),
        ], heading="Image Information"),
    ]
