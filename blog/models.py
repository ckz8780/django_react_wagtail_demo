from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

import datetime

class BlogIndexPage(Page):
    class Meta:
        verbose_name = ('Blog Index Page')
        verbose_name_plural = ('Blog Index Pages')

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    # Update context to include only published posts, ordered by reverse-chron
    def get_context(self, request):
        context = super().get_context(request)
        posts = self.get_children().live().order_by('-first_published_at')
        context['posts'] = posts
        return context

class BlogPost(Page):

    class Meta:
        verbose_name = ('Blog Post')
        verbose_name_plural = ('Blog Posts')

    date = models.DateField("Post date", default=datetime.date.today)
    intro = models.CharField(max_length=250, blank=True)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    # Get the first gallery item and use it as the main image
    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

class BlogPostGalleryImage(Orderable):
    page = ParentalKey(BlogPost, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]