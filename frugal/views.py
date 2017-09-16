# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from money.models import DailyLedger
from money.utils import  week_range


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            now = timezone.now()
            today = DailyLedger.objects.today() or DailyLedger.start_day(self.request.user)
            this_week = DailyLedger.objects.this_week(self.request.user)
            this_month = DailyLedger.objects.this_week(self.request.user)
            ctx['today'] = {
                'balance': today.balance,
                'transactions': today.transactions.count(),
                'date': now.strftime("%B %d, %Y")
            }
            start, end = week_range(now)
            ctx['this_week'] = {
                'balance': sum([l.balance for l in this_week]),
                'transactions': sum([l.transactions.count() for l in this_week]),
                'date': '{} - {}'.format(start.strftime('%B %d'), end.strftime('%B %d'))
            }
            ctx['this_month'] = {
                'balance': sum([l.balance for l in this_month]),
                'transactions': sum([l.transactions.count() for l in this_month]),
                'date': now.strftime('%B')
            }
        return ctx


class LoginView(auth_views.LoginView):
    template_name = 'home.html'


class LogoutView(auth_views.LogoutView):
    next_page = '/login/'
