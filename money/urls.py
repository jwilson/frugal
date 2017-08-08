# coding=utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from .views import ExpenseDetailsView

urlpatterns = [
    # Book Views
    url(r'^expenses/$', ExpenseDetailsView.as_view(), name='expenses')
]