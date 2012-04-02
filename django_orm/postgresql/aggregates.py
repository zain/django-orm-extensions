# -*- coding: utf-8 -*-

from django.db import models
from django_orm.postgresql.sql import aggregates as aggregates_module

class Aggregate(models.aggregates.Aggregate):
    def add_to_query(self, query, alias, col, source, is_summary):
        klass = getattr(aggregates_module, self.name)
        aggregate = klass(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate
        

class ArrayLength(Aggregate):
    """
    Aggregate: returns the length of the requested array.
    """
    name = "ArrayLength"

class Unaccent(Aggregate):
    name = 'Unaccent'
