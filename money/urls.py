# coding=utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import FixedAmountDetailsView

urlpatterns = [
    # Book Views
    url(r'^fixed-amounts/$', FixedAmountDetailsView.as_view(), name='fixed_amounts')
]