# -*- coding: utf-8 -*-

from django.db.models.sql import aggregates
from django_orm.fields.standard import CharField

class Unaccent(aggregates.Aggregate):
    sql_function = 'unaccent'

    def __init__(self, col, source=None, is_summary=False, **extra):
        source = CharField(max_length=10000)
        super(Unaccent, self).__init__(col, source, is_summary, **extra)


class ArrayLength(aggregates.Aggregate):
    sql_function = 'array_length'
    sql_template = '%(function)s(%(field)s, 1)'
    is_ordinal = True
