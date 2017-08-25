# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from money.models import DailyLedger


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        ledger = DailyLedger.objects.today() or DailyLedger.start_day()
        ctx['today'] = {'balance': ledger.balance, 'transactions': ledger.transactions.count()}
        return ctx
