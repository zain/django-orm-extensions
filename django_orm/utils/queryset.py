# -*- coding: utf-8 -*-

from django.utils.datastructures import SortedDict
from django.db.models.sql.where import ExtraWhere
from django_orm.utils.statements import AND, OR

class StatementMixIn(object):
    def _setup_joins_for_fields(self, parts, node, query):
        parts_num = len(parts)

        if parts_num == 0:
            return

        if parts_num == 1:
            node.field = (self.model._meta.db_table, parts[0])
            return

        field, source, opts, join_list, last, _ = query.setup_joins(
            parts, self.model._meta, query.get_initial_alias(), False)
        
        # Process the join chain to see if it can be trimmed
        col, _, join_list = query.trim_joins(source, join_list, last, False)
        
        # If the aggregate references a model or field that requires a join,
        # those joins must be LEFT OUTER - empty join rows must be returned
        # in order for zeros to be returned for those aggregates.
        for column_alias in join_list:
            query.promote_alias(column_alias, unconditional=True)

        lookup_model = self.model
        for counter, field_name in enumerate(parts):
            try:
                lookup_field = lookup_model._meta.get_field(field_name)
            except FieldDoesNotExist:
                parts.pop()
                break
            
            try:
                lookup_model = lookup_field.rel.to
            except AttributeError:
                parts.pop()
                break

        node.field = (lookup_model._meta.db_table, lookup_field.attname)

    def inline_annotate(self, **kwargs):
        extra_select, params = SortedDict(), []
        clone = self._clone()

        for alias, node in kwargs.iteritems():
            #self._setup_joins_for_fields(node.field_parts, node, clone.query)
            _sql, _params = node.as_sql(self.quote_name, self)

            extra_select[alias] = _sql
            params.extend(_params)

        clone.query.add_extra(extra_select, params, None, None, None, None)
        return clone

    def where(self, *args):
        clone = self._clone()
        statement = AND(*args)

        _sql, _params = statement.as_sql(self.quote_name, clone)
        if hasattr(_sql, 'to_str'):
            _sql = _sql.to_str()

        clone.query.where.add(ExtraWhere([_sql], _params), "AND")
        return clone

