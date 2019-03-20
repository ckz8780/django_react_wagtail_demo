"""
blog URL Configuration
"""

from django.urls import path, re_path, include
from wagtail.core import urls as wagtail_urls

urlpatterns = [
    path('', include(wagtail_urls)),
]