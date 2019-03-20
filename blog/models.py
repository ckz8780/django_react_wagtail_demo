from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
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
    ]