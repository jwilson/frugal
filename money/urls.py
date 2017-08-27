# coding=utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import FixedAmountsView, ThisMonthsTransactionsListView, ThisWeeksTransactionsListView, \
    TodaysTransactionsListView, TransactionCreateView

urlpatterns = [
    url(r'^transactions/new/$', TransactionCreateView.as_view(), name='transactions_create'),
    url(r'^transactions/monthly/$', ThisMonthsTransactionsListView.as_view(), name='transactions_monthly'),
    url(r'^transactions/weekly/$', ThisWeeksTransactionsListView.as_view(), name='transactions_weekly'),
    url(r'^transactions/today/$', TodaysTransactionsListView.as_view(), name='transactions_today'),
    url(r'^transactions/$', TodaysTransactionsListView.as_view(), name='transactions_today'),
    url(r'^fixed-amounts/$', FixedAmountsView.as_view(), name='fixed_amounts')
]