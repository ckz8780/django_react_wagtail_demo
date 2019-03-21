from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

import datetime

class BlogIndexPage(Page):
    '''
    Blog index page - lists all posts in reverse chron order
    '''
    
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

class BlogPostTag(TaggedItemBase):
    '''
    Tag objects - linked to a blog post
    '''

    content_object = ParentalKey(
        'BlogPost',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogPost(Page):
    '''
    Blog posts - normally a child of the blog index
    '''

    class Meta:
        verbose_name = ('Blog Post')
        verbose_name_plural = ('Blog Posts')

    date = models.DateField("Post date", default=datetime.date.today)
    intro = models.CharField(max_length=250, blank=True)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
        ], heading="Post Info"),
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
    '''
    Image gallery objects - linked to a BlogPost as parent
    but can be used elsewhere as they are unique DB items
    '''

    page = ParentalKey(BlogPost, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]

class BlogTagIndexPage(Page):
    '''
    Tag index page - for displaying posts by tag name
    '''

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        posts = BlogPost.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['posts'] = posts
        return context