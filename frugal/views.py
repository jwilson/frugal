# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import views as auth_views
from django.utils import timezone
from django.views.generic import TemplateView

from money.models import DailyLedger


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        today = DailyLedger.objects.today() or DailyLedger.start_day()
        this_week = DailyLedger.objects.this_week(self.request.user)
        ctx['today'] = {
            'balance': today.balance,
            'transactions': today.transactions.count(),
            'date': timezone.now().strftime("%l, %F the %j%S, %o")
        }
        ctx['this_week'] = {
            'balance': sum([l.balance for l in this_week]),
            'transactions': sum([l.transactions.count() for l in this_week]),
            'date': ''
        }
        return ctx


class LoginView(auth_views.LoginView):
    template_name = 'home.html'
