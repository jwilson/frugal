# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

register = template.Library()


@register.filter
def get_difference_class(difference):
    return 'success' if difference >= 0 else 'danger'
