# -*- coding: utf-8 -*-

from django.utils.datastructures import SortedDict

class AggragateMixIn(object):
    def inline_annotate(self, **kwargs):
        extra_select, params = SortedDict(), []

        for alias, node in kwargs.iteritems():
            _sql, _params = node.as_sql(self.quote_name, None)
            extra_select[alias] = _sql
            params.extend(_params)

        return self.extra(select=extra_select, select_params=params)
