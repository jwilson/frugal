# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from datetime import datetime
from dateutils import relativedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import DailyLedger, FixedAmount, Transaction
from .forms import FixedAmountForm, TransactionForm


class FixedAmountsView(ListView):
    model = FixedAmount
    template_name = 'money/fixedamounts.html'


class FixedAmountCreateView(CreateView):
    model = FixedAmount
    form = FixedAmountForm
    fields = ['label', 'frequency', 'type', 'amount']
    success_url = reverse_lazy('home')
    template_name = 'money/fixedamounts_create.html'


class TransactionsListBaseView(LoginRequiredMixin, ListView):
    model = Transaction
    login_url = '/login/'
    redirect_field_name = 'goto'

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


class ThisMonthsTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return DailyLedger.objects.this_month(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(ThisMonthsTransactionsListView, self).get_context_data(**kwargs)
        ctx['chart_label'] = _('Previous 5 Months')
        ctx['period_label'] = _('This Month')
        ctx['ledgers'] = []
        for i in reversed(range(1, 6)):
            now = timezone.now()
            start = now - relativedelta(months=i)
            ledgers = (DailyLedger
                       .objects
                       .filter(created_on__month=start.month, owner=self.request.user))
            ctx['ledgers'].append({'start': start.strftime('%B'),
                                   'balance': ledgers.aggregate(total=Sum('ending_balance'))['total'] or 0})
        return ctx


class ThisWeeksTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return DailyLedger.objects.this_week(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(ThisWeeksTransactionsListView, self).get_context_data(**kwargs)
        ctx['chart_label'] = _('Previous 5 Weeks')
        ctx['period_label'] = _('This Week')
        ctx['ledgers'] = []
        for i in reversed(range(1, 6)):
            now = timezone.now()
            start = now - relativedelta(days=now.weekday() + 1, weeks=i)
            end = start + relativedelta(days=6)
            ledgers = (DailyLedger
                       .objects
                       .filter(created_on__range=(start, end), owner=self.request.user))
            ctx['ledgers'].append({'start': start.strftime('%b %d'),
                                   'balance': ledgers.aggregate(total=Sum('ending_balance'))['total'] or 0})
        return ctx


class TodaysTransactionsListView(TransactionsListBaseView):
    template_name = 'money/transactions.html'

    def get_queryset(self):
        return [DailyLedger.objects.today()]

    def get_context_data(self, **kwargs):
        ctx = super(TodaysTransactionsListView, self).get_context_data(**kwargs)
        ctx['chart_label'] = _('Previous 5 Days')
        end = timezone.now() - relativedelta(days=1)
        start = end - relativedelta(days=5)
        ledgers = (DailyLedger
                   .objects
                   .filter(created_on__range=(start, end), owner=self.request.user)
                   .order_by('created_on'))
        ctx['ledgers'] = [{'start': l.created_on.strftime('%b %d'), 'balance': l.ending_balance or 0} for l in ledgers]
        return ctx


class TransactionCreateView(CreateView):
    model = Transaction
    form = TransactionForm
    fields = ('type', 'currency', 'amount')
    success_url = reverse_lazy('home')
    template_name = 'money/transactions_create.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        if self.request.POST.get('occurred_at', '') != timezone.now().date().strftime('%d/%m/%Y'):
            date = datetime.strptime(self.request.POST.get('occurred_at'), '%d/%m/%Y')
            instance.ledger = (DailyLedger
                               .objects
                               .filter(created_on=date)
                               .first()) or DailyLedger.start_day(self.request.user, date=date)
            instance.ledger.ending_balance = instance.ledger.balance
            instance.ledger.save()
        else:
            instance.ledger = DailyLedger.objects.today() or DailyLedger.start_day(self.request.user)
        instance.owner = self.request.user
        instance.save()
        return super(TransactionCreateView, self).form_valid(form)
