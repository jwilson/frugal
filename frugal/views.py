# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from money.models import DailyLedger


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        ledger = DailyLedger.objects.today() or DailyLedger.start_day()
        ctx['today'] = {'balance': ledger.balance, 'transactions': ledger.transactions.count()}
        return ctx


class LoginView(auth_views.LoginView):
    template_name = 'home.html'
