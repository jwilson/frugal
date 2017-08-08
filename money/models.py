# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Sum
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


INCOME_TYPE = (
    ('1', 'Reoccurring')
)


EXPENSE_TYPE = (
    ('1', _('Purchase')),
    ('2', _('Bill')),
)


FREQUENCY = (
    ('1', _('Weekly')),
    ('2', _('Bi-Weekly')),
    ('3', _('Monthly')),
    ('4', _('Bi-Monthly')),
    ('5', _('Quarterly')),
    ('6', _('Semi Annually')),
    ('7', _('Annually')),
)


class Account(models.Model):
    label = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    def __unicode__(self):
        return '{} - {}'.format(self.label, self.balance)

@python_2_unicode_compatible
class DailyLedger(models.Model):
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.created_on)

    def get_expense_totals(self):
        return self._get_totals(**{'scheduledtransaction__income__isnull': False})

    def get_income_totals(self):
        return self._get_totals(**{'scheduledtransaction__expense__isnull': False})

    def _get_totals(self, **kwargs):
        return self.transactions.exclude(**kwargs).aggregate(
            total=Sum('scheduledtransaction__daily'))['total'] or Decimal(0.00)


class Transaction(models.Model):
    natural_id = models.UUIDField(default=uuid4)
    label = models.CharField(max_length=64)
    frequency = models.CharField(max_length=1, choices=FREQUENCY, default='3')
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    ledger = models.ForeignKey(DailyLedger, related_name='transactions')


class ScheduledTransaction(Transaction):
    weekly = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    monthly = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    yearly = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    daily = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.frequency == '1':
            self.weekly = self.amount
            self.yearly = self.weekly * 52
            self.monthly = self.yearly / 12
            self.daily = self.yearly / 365
        elif self.frequency == '2':
            self.yearly = self.amount * 26
            self.monthly = self.yearly / 12
            self.weekly = self.yearly / 52
            self.daily = self.yearly / 365
        elif self.frequency == '3':
            self.monthly = self.amount
            self.yearly = self.monthly * 12
            self.weekly = self.yearly / 52
            self.daily = self.yearly / 365
        elif self.frequency == '4':
            self.monthly = self.amount * 2
            self.yearly = self.monthly * 12
            self.weekly = self.yearly / 52
            self.daily = self.yearly / 365
        elif self.frequency == '5':
            self.monthly = self.amount / 4
            self.yearly = self.monthly * 12
            self.weekly = self.yearly / 52
            self.daily = self.yearly / 365
        elif self.frequency == '6':
            self.monthly = self.amount / 6
            self.yearly = self.monthly * 12
            self.weekly = self.yearly / 52
            self.daily = self.yearly / 365
        elif self.frequency == '7':
            self.yearly = self.amount
            self.monthly = self.yearly / 12
            self.weekly = self.yearly / 52
            self.daily = self.yearly / 365

        super(ScheduledTransaction, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                               update_fields=update_fields)


class Income(ScheduledTransaction):
    def __unicode__(self):
        return '{} {}/{}'.format(self.label, self.amount, self.get_frequency_display())


class Expense(ScheduledTransaction):
    def __unicode__(self):
        return '{} {}/{}'.format(self.label, self.amount, self.get_frequency_display())
