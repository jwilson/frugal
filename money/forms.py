# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Transaction


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        exclude = ('uuid', 'ledger')
