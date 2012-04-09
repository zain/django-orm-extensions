# -*- coding: utf-8 -*-

class SqlNode(object):
    @property
    def field_parts(self):
        raise NotImplementedError

    def as_sql(self, qn, queryset):
        raise NotImplementedError
