# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy

from .models import DailyLedger, FixedAmount, Transaction
from .forms import TransactionForm


class FixedAmountsView(ListView):
    model = FixedAmount
    template_name = 'money/fixed_amount_list.html'


class TransactionCreateView(CreateView):
    model = Transaction
    form = TransactionForm
    fields = ('type', 'amount')
    success_url = reverse_lazy('home')
    template_name = 'money/transaction_create.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.ledger = DailyLedger.objects.today() or DailyLedger.start_day()
        instance.save()
        return super(TransactionCreateView, self).form_valid(form)
