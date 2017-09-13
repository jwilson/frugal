# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .utils import week_range

FREQUENCY = (
    ('1', _('Weekly')),
    ('2', _('Bi-Weekly')),
    ('3', _('Monthly')),
    ('4', _('Bi-Monthly')),
    ('5', _('Quarterly')),
    ('6', _('Semi Annually')),
    ('7', _('Annually')),
)

FIXED_AMOUNT_TYPE = (
    ('1', 'Expense'),
    ('2', 'Income')
)

TRANSACTION_TYPE = (
    ('1', 'Purchase'),
    ('2', 'Bill'),
    ('3', 'Withdraw'),
    ('4', 'Deposit'),
)


class DailyLedgerQuerySet(models.QuerySet):

    def _filter(self, q, user=None):
        ledgers = self.filter(q)
        if user:
            ledgers = ledgers.filter(Q(owner=user))
        return ledgers

    def this_month(self, user=None):
        return self._filter(Q(created_on__month=timezone.now().month), user=user)

    def this_week(self, user=None):
        return self._filter(Q(created_on__range=week_range(timezone.now())), user=user)

    def today(self, user=None):
        return self._filter(Q(created_on=timezone.now().date()), user=user).first()


@python_2_unicode_compatible
class DailyLedger(models.Model):
    owner = models.ForeignKey(User, related_name='daily_ledgers')
    created_on = models.DateField(auto_now_add=True)
    starting_balance = models.IntegerField(blank=True, null=True)
    ending_balance = models.IntegerField(blank=True, null=True)

    objects = DailyLedgerQuerySet.as_manager()

    def __str__(self):
        return '{}'.format(self.created_on)

    @classmethod
    def start_day(cls, owner):
        DailyLedger.end_day(owner)
        today = DailyLedger.objects.create(owner=owner)
        incomes, expenses = 0, 0
        for expense in FixedAmount.objects.expenses():
            expenses += expense.daily
            today.transactions.add(Transaction.objects.create(owner=owner, amount=expense.daily,
                                                              automatic=True, type='3'))
        for income in FixedAmount.objects.income():
            incomes += income.daily
            today.transactions.add(Transaction.objects.create(owner=owner, amount=income.daily,
                                                              automatic=True, type='4'))
        today.starting_balance = incomes - expenses
        today.save()
        return today

    @classmethod
    def end_day(cls, owner):
        ledger = DailyLedger.objects.filter(owner=owner).order_by('-created_on').first()
        if ledger:
            ledger.ending_balance = ledger.balance
            ledger.save()

    @staticmethod
    def _sum(queryset):
        return queryset.aggregate(total=Sum('amount'))['total'] or 0

    @property
    def balance(self):
        return self.deposits - self.purchases - self.payments - self.withdraws

    @property
    def purchases(self):
        return DailyLedger._sum(self.transactions.filter(type='1'))

    @property
    def payments(self):
        return DailyLedger._sum(self.transactions.filter(type='2'))

    @property
    def withdraws(self):
        return DailyLedger._sum(self.transactions.filter(type='3'))

    @property
    def deposits(self):
        return DailyLedger._sum(self.transactions.filter(type='4'))

    @property
    def difference(self):
        return self.balance - self.starting_balance


@python_2_unicode_compatible
class Transaction(models.Model):
    uuid = models.UUIDField(default=uuid4)
    owner = models.ForeignKey(User, related_name='transactions')
    type = models.CharField(max_length=1, choices=TRANSACTION_TYPE, default='1')
    automatic = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    ledger = models.ForeignKey(DailyLedger, related_name='transactions', blank=True, null=True)

    def __str__(self):
        return '{} @ {}'.format(self.amount, self.ledger)


class FixedAmountQuerySet(models.QuerySet):

    def income(self):
        return self.filter(Q(type='2'))

    def expenses(self):
        return self.filter(Q(type='1'))


@python_2_unicode_compatible
class FixedAmount(models.Model):
    label = models.CharField(max_length=64)
    frequency = models.CharField(max_length=1, choices=FREQUENCY, default='3')
    type = models.CharField(max_length=1, choices=FIXED_AMOUNT_TYPE)

    amount = models.DecimalField(max_digits=7, decimal_places=2)

    weekly = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    monthly = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    yearly = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    daily = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    objects = FixedAmountQuerySet.as_manager()

    def __str__(self):
        return '{} ${}/{} ({})'.format(self.label, self.amount, self.get_frequency_display(), self.get_type_display())

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

        super(FixedAmount, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                      update_fields=update_fields)
