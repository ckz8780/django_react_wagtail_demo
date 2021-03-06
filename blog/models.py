from django.db import models
from django import forms
from django.shortcuts import render
from django.contrib.auth.models import User

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from streams import blocks

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

    # Allow filtering by tag
    def serve(self, request):
        # Get posts and order by reverse chron
        posts = BlogPost.objects.child_of(self).live().order_by('-first_published_at')
        advanced_posts = AdvancedBlogPost.objects.child_of(self).live().order_by('-first_published_at')

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            posts = posts.filter(tags__name=tag)
            advanced_posts = advanced_posts.filter(tags__name=tag)

        # Filter by author
        author = request.GET.get('author')
        if author:
            posts = posts.filter(author=User.objects.get(username=author))
            advanced_posts = advanced_posts.filter(author=User.objects.get(username=author))

        return render(request, self.template, {
            'page': self,
            'posts': posts,
            'advanced_posts': advanced_posts,
        })

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

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField("Post date", default=datetime.date.today)
    intro = models.CharField(max_length=250, blank=True)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    categories = ParentalManyToManyField('blog.PostCategory', blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('author', widget=forms.Select),
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
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

@register_snippet
class PostCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Post Categories'

class AdvancedBlogPost(Page):
    '''
    Advanced blog posts - a child of the blog index
    using streamfields and blocks
    '''

    class Meta:
        verbose_name = ('Advanced Blog Post')
        verbose_name_plural = ('Advanced Blog Posts')

    content = StreamField([
        ("title_and_text", blocks.TitleAndTextBlock())
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel("content")
    ]