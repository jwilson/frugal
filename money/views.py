# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from datetime import timedelta

from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import DailyLedger, FixedAmount, Transaction
from .forms import TransactionForm
from .utils import week_range


class FixedAmountsView(ListView):
    model = FixedAmount
    template_name = 'money/fixed_amount_list.html'


class TransactionsListBaseView(ListView):
    model = Transaction

    def get_transaction_data(self):
        return {
            'deposits': sum([dl.deposits for dl in self.get_queryset()]),
            'withdraws': sum([dl.withdraws for dl in self.get_queryset()]),
            'payments': sum([dl.payments for dl in self.get_queryset()]),
            'purchases': sum([dl.purchases for dl in self.get_queryset()]),
            'balance': sum([dl.balance for dl in self.get_queryset()]),
            'difference': sum([dl.difference for dl in self.get_queryset()]),
            'transactions': [dl.transactions.all() for dl in self.get_queryset()]
        }

    def get_context_data(self, **kwargs):
        ctx = super(TransactionsListBaseView, self).get_context_data(**kwargs)
        ctx['ledger'] = self.get_transaction_data()
        ctx['id'] = str.replace(str(uuid.uuid4()), '-', '')
        return ctx

    def get_ledger_data(self, ledgers):
        return [{'created_on': l.created_on, 'ending_balance': l.ending_balance} for l in ledgers]


class ThisMonthsTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return DailyLedger.objects.this_month(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(ThisMonthsTransactionsListView, self).get_context_data(**kwargs)
        ctx['chart_label'] = _('Previous 7 Months')
        return ctx


class ThisWeeksTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return DailyLedger.objects.this_week(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(ThisWeeksTransactionsListView, self).get_context_data(**kwargs)
        ctx['chart_label'] = _('Previous 7 Weeks')
        return ctx


class TodaysTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return [DailyLedger.objects.today()]

    def get_context_data(self, **kwargs):
        ctx = super(TodaysTransactionsListView, self).get_context_data(**kwargs)
        now = timezone.now()
        start, end = week_range(now)
        delta = timedelta(days=7 - (now.weekday() + 1))
        start = start - delta
        end = end - delta
        ledgers = (DailyLedger
                   .objects
                   .filter(created_on__range=(start, end), owner=self.request.user)
                   .order_by('created_on'))
        ctx['ledgers'] = self.get_ledger_data(ledgers)
        ctx['chart_label'] = _('Previous 7 Days')
        return ctx


class TransactionCreateView(CreateView):
    model = Transaction
    form = TransactionForm
    fields = ('type', 'currency', 'amount')
    success_url = reverse_lazy('home')
    template_name = 'money/transactions_create.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.ledger = DailyLedger.objects.today() or DailyLedger.start_day(self.request.user)
        instance.owner = self.request.user
        instance.save()
        return super(TransactionCreateView, self).form_valid(form)
