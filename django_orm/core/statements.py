# -*- coding: utf-8 -*-

from django.utils import tree
from django.db.models.sql.datastructures import MultiJoin
from django.db.models.fields import FieldDoesNotExist

def _setup_joins_for_fields(parts, node, queryset):
    parts_num = len(parts)
    
    if parts_num == 0:
        return
    
    if parts_num == 1:
        node.field = (queryset.model._meta.db_table, parts[0])
    
    field, source, opts, join_list, last, _ = queryset.query.setup_joins(
        parts, queryset.model._meta, queryset.query.get_initial_alias(), False)
    
    # Process the join chain to see if it can be trimmed
    col, _, join_list = queryset.query.trim_joins(source, join_list, last, False)
    
    # If the aggregate references a model or field that requires a join,
    # those joins must be LEFT OUTER - empty join rows must be returned
    # in order for zeros to be returned for those aggregates.
    for column_alias in join_list:
        queryset.query.promote_alias(column_alias, unconditional=True)

    # this works for one level of depth
    #lookup_model = self.query.model._meta.get_field(parts[-2]).rel.to
    #lookup_field = lookup_model._meta.get_field(parts[-1])
    
    if parts_num >= 2:
        lookup_model = queryset.model
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


class CommonBaseTree(tree.Node):
    """
    Encapsulates filters as objects that can then be combined logically (using
    & and |).
    """
    # Connection types
    AND = 'AND'
    OR = 'OR'
    default = AND 
    query = None

    def __init__(self, *args, **kwargs):
        super(CommonBaseTree, self).__init__(children=list(args) + kwargs.items())

    def _combine(self, other, conn):
        if not isinstance(other, (BaseTree)): 
            raise TypeError(other)
        obj = type(self)()
        obj.add(self, conn)
        obj.add(other, conn)
        return obj 

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj
    
    def set_query(self, query):
        self.query = query
        return self


class RawSQL(object):
    def __init__(self, items, connector, query=None):
        self.items = items
        self.connector = connector
        self.query = query

    def __str__(self):
        connector = " %s " % (self.connector)
        return connector.join(self.items)

    def to_str(self, closure=False):
        if closure:
            return u"(%s)" % unicode(self)
        return unicode(self)


class OperatorTree(CommonBaseTree):
    """
    Base operator node class.
    """
    def as_sql(self, qn, queryset):
        items, params = [], []

        for child in self.children:
            _sql, _params = child.as_sql(qn, queryset)
            
            if isinstance(_sql, RawSQL):
                _sql = _sql.to_str(True)
            
            items.extend([_sql])
            params.extend(_params)

        sql_obj = RawSQL(items, self._connector, queryset)
        return sql_obj, params


class AND(OperatorTree):
    _connector = "AND"


class OR(OperatorTree):
    _connector = "OR"


class RawStatement(object):
    field_parts = []

    def __init__(self, sqlstatement, *args):
        self.statement = sqlstatement
        self.params = args

    def as_sql(self, qn, queryset):
        return self.statement, self.params


class Statement(object):
    """
    Base class for all statements and aggregates.
    """

    sql_template = "%(function)s(%(field)s)"
    use_template = 'sql_template'

    sql_function = None
    sql_operator = None

    args = []

    @property
    def field_parts(self):
        return self.field.split("__")

    def __init__(self, field, *args):
        self.field = field
        self.args = list(args)
    
    def as_sql(self, qn, queryset):
        """
        Return the statement rendered as sql.
        """
        
        # setup joins if needed
        _setup_joins_for_fields(self.field_parts, self, queryset)

        # build sql
        params = {}
        if self.sql_function is not None:
            params['function'] = self.sql_function

        if self.sql_operator is not None:
            params['op'] = self.sql_operator

        if isinstance(self.field, basestring):
            params['field'] = qn(self.field)
        elif isinstance(self.field, (tuple, list)):
            _tbl, _fld = self.field
            params['field'] = "%s.%s" % (qn(_tbl), qn(_fld))
        else:
            raise ValueError("Invalid field value")

        params.update(self.extra)
        
        template = getattr(self, self.use_template)
        return template % params, self.args

    def as_statement(self, operator, *args, **kwargs):
        self.use_template = 'stmt_template'

        if not hasattr(self, 'stmt_template'):
            self.stmt_template = self.sql_template + " %(op)s %%s"

        self.sql_operator = operator

        self.args.extend(args)
        self.extra = kwargs
        return self

    def as_aggregate(self, *args, **kwargs):
        self.args.extend(args)
        self.extra = kwargs
        self.sql_operator = None
        return self
