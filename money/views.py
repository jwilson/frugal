# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView

from .models import FixedAmount


class FixedAmountDetailsView(ListView):
    model = FixedAmount
    template_name = 'money/fixed_amount_list.html'
