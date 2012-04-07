# -*- coding: utf-8 -*-

from django.db import models
from django_orm.utils.aggregates import AggregateNode

class Unaccent(AggregateNode):
    sql_function = 'unaccent'
