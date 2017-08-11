# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import DailyLedger, FixedAmount


@admin.register(FixedAmount)
class FixedAmountAdmin(admin.ModelAdmin):
    pass


@admin.register(DailyLedger)
class DailyLedgerAdmin(admin.ModelAdmin):
    pass
