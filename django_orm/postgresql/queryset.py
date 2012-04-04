# -*- coding: utf-8 -*-

from django.db.models.sql.constants import SINGLE
from django_orm.postgresql.hstore.query import select_query, update_query
from django_orm.cache.queryset import CachedQuerySet

class UnaccentQuerysetMixin(object):
    def unaccent(self, **kwargs):
        where, params = [], []
        for field, search_term in kwargs.items():
            where_sql = u"unaccent(%s) LIKE unaccent(%%s)" % field
            where.append(where_sql)
            params.append(self._prepare_search_term(search_term))
        return self.extra(where=where, params=params)
    
    def iunaccent(self, **kwargs):
        where, params = [], []
        for field, search_term in kwargs.items():
            where_sql = u"lower(unaccent(%s)) LIKE lower(unaccent(%%s))" % field
            where.append(where_sql)
            params.append(self._prepare_search_term(search_term))
        return self.extra(where=where, params=params)

    def _prepare_search_term(self, term):
        return u"%%%s%%" % term

class PgQuerySet(UnaccentQuerysetMixin, CachedQuerySet):
    """
    Redefinition of standard queryset (with cache)
    for postgresql backend.
    """
    pass


class ArrayPgQuerySet(CachedQuerySet):
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
