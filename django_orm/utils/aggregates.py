# -*- coding: utf-8 -*-

class AggregateNode(object):
    sql_template = '%(function)s(%(field)s)'
    sql_function = None
    is_ordinal = False
    is_computed = False

    def __init__(self, field, *args, **kwargs):
        self.field = field
        self.args = args
        self.params = kwargs
    
    def as_sql(self, qn, connection):
        """
        Return the aggregate/annotation rendered as sql.
        """
        params = {
            'function': self.sql_function,
            'field': self.field,
        }
        params.update(self.params)
        return self.sql_template % params, self.args
