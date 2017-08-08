# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Transaction, ScheduledTransaction, Account, DailyLedger, Expense, Income


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    pass


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    pass


@admin.register(DailyLedger)
class DailyLedgerAdmin(admin.ModelAdmin):
    pass
