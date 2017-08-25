# coding=utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import FixedAmountsView, TransactionCreateView

urlpatterns = [
    url(r'^transactions/new/$', TransactionCreateView.as_view(), name='transaction_create'),
    url(r'^fixed-amounts/$', FixedAmountsView.as_view(), name='fixed_amounts')
]