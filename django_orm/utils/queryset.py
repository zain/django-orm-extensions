# -*- coding: utf-8 -*-

from django.utils.datastructures import SortedDict

class AggragateMixIn(object):
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

        node.field = (parts[-2], parts[-1])

    def inline_annotate(self, **kwargs):
        extra_select, params = SortedDict(), []
        clone = self._clone()

        for alias, node in kwargs.iteritems():
            self._setup_joins_for_fields(node.field_parts, node, clone.query)
            _sql, _params = node.as_sql(self.quote_name, None)

            extra_select[alias] = _sql
            params.extend(_params)

        clone.query.add_extra(extra_select, params, None, None, None, None)
        return clone
