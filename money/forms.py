# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import FixedAmount, Transaction


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        exclude = ('uuid', 'ledger')


class FixedAmountForm(forms.ModelForm):

    class Meta:
        model = FixedAmount
        exclude = ['weekly', 'monthly', 'yearly', 'daily']