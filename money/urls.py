# coding=utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import FixedAmountsView, TodaysTransactionsListView, TransactionCreateView

urlpatterns = [
    url(r'^transactions/new/$', TransactionCreateView.as_view(), name='transactions_create'),
    url(r'^transactions/$', TodaysTransactionsListView.as_view(), name='transactions'),
    url(r'^fixed-amounts/$', FixedAmountsView.as_view(), name='fixed_amounts')
]