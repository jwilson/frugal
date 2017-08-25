# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Transaction, DailyLedger


@receiver(pre_save, sender=Transaction)
def check_for_daily_ledger(sender, **kwargs):
    daily_ledger, created = DailyLedger.objects.get_or_create(created_on=timezone.now().date())