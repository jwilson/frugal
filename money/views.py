# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy

from .models import DailyLedger, FixedAmount, Transaction
from .forms import TransactionForm


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
        return ctx


class ThisMonthsTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return DailyLedger.objects.this_month(self.request.user)


class ThisWeeksTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return DailyLedger.objects.this_week(self.request.user)


class TodaysTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return [DailyLedger.objects.today()]


class TransactionCreateView(CreateView):
    model = Transaction
    form = TransactionForm
    fields = ('type', 'amount')
    success_url = reverse_lazy('home')
    template_name = 'money/transactions_create.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.ledger = DailyLedger.objects.today() or DailyLedger.start_day(self.request.user)
        instance.owner = self.request.user
        instance.save()
        return super(TransactionCreateView, self).form_valid(form)
