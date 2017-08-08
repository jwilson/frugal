# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView

from .models import Expense


class ExpenseDetailsView(ListView):
    model = Expense
    template_name = 'expense_list.html'
