# -*- coding: utf-8 -*-

class AggregateNode(object):
    sql_template = '%(function)s(%(field)s)'
    sql_function = None
    is_ordinal = False
    is_computed = False

    def __init__(self, field, *args, **kwargs):
        self.field = field
        self.args = args
        self.extern_params = kwargs

    @property
    def field_parts(self):
        return self.field.split("__")
    
    def as_sql(self, qn, connection):
        """
        Return the aggregate/annotation rendered as sql.
        """
        params = {}
        if self.sql_function is not None:
            params['function'] = self.sql_function

        if isinstance(self.field, basestring):
            params['field'] = qn(self.field)
        elif isinstance(self.field, (tuple, list)):
            _tbl, _fld = self.field
            params['field'] = "%s.%s" % (qn(_tbl), qn(_fld))
        else:
            raise ValueError("Invalid field value")

        params.update(self.extern_params)
        return self.sql_template % params, self.args
