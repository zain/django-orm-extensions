# -*- coding: utf-8 -*-

from django.db.models.sql.constants import SINGLE
from django_orm.postgresql.hstore.query import select_query, update_query
from django_orm.cache.query import CachedQuerySet
from django_orm.postgresql.query import PgQuery


class PgQuerySet(CachedQuerySet):
    """
    Redefinition of standard queryset (with cache)
    for postgresql backend.
    """

    def __init__(self, model=None, query=None, using=None):
        query = query or PgQuery(model)
        super(PgQuerySet, self).__init__(model=model, query=query, using=using)

    @select_query
    def array_slice(self, query, attr, x, y):
        query.add_extra({'_': '%s[%%s:%%s]' % attr}, [x+1, y+1], None, None, None, None)
        result = query.get_compiler(self.db).execute_sql(SINGLE)
        if result and result[0]:
            field = self.model._meta.get_field_by_name(attr)[0]
            return field.to_python(result[0])
        return result[0]

    @select_query
    def array_length(self, query, attr):
        query.add_extra({'_': 'array_length(%s, 1)' % attr}, [], None, None, None, None)
        result = query.get_compiler(self.db).execute_sql(SINGLE)
        if result and result[0]:
            field = self.model._meta.get_field_by_name(attr)[0]
            return field.to_python(result[0])
        return result[0]
