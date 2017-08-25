# coding=utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import FixedAmountsView, TransactionCreateView

urlpatterns = [
    url(r'^transactions/add/$', TransactionCreateView.as_view(), name='transactions'),
    url(r'^fixed-amounts/$', FixedAmountsView.as_view(), name='fixed_amounts')
]