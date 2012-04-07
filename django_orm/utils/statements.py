# -*- coding: utf-8 -*-

from django.utils import tree
from django.db.models.sql.datastructures import MultiJoin

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
    def as_sql(self, qn, query=None):
        if query is None:
            query = self.query

        items = []
        params = []

        for child in self.children:
            _sql, _params = child.as_sql(qn, query)

            if isinstance(_sql, RawSQL):
                _sql = _sql.to_str(True)
            
            items.extend([_sql])
            params.extend(_params)

        sql_obj = RawSQL(items, self._connector, query)
        return sql_obj, params


class AND(OperatorTree):
    _connector = "AND"


class OR(OperatorTree):
    _connector = "OR"


class RawStatement(object):
    def __init__(self, sqlstatement, *args):
        self.statement = sqlstatement
        self.params = args

    def as_sql(self, qn, connection):
        return self.statement, self.params


class BaseTree(CommonBaseTree):
    def sql_condition(self, parts, value, qn):
        raise NotImplemented("Can be reimplemented on subclass.")

    def as_sql(self, qn, connection, query):
        self.query = query
        self.items = []
        self.params = ()

        for qobj in self.children:
            if hasattr(qobj, 'as_sql'):
                _sql, _params = qobj.as_sql(qn, connection, query)

            else:
                parts, value = qobj[0].split("__"), qobj[1]
                _sql, _params = self.sql_condition(parts, value, qn)

            self.items.append(_sql)
            self.params += tuple(_params)
        
        if not self.items:
            return None, ()

        if len(self.items) == 1:
            if self.negated:    
                return self.negated_block(self.items[0]), self.params
            return self.items[0],  self.params
        
        join_attr = " %s " % (self.connector)
        result_sql = join_attr.join(self.items)

        if self.negated:
            return self.negated_block(result_sql), self.params

        return result_sql, self.params

    def key_to_quoted_field_name(self, parts, qn):
        num_parts = len(parts)
        if num_parts == 1:
            return u"%s.%s" % (
                qn(self.query.model._meta.db_table),
                qn("__".join(parts))
            )

        if num_parts % 2 != 0:
            raise ValueError("Incorrect number of lookups")
        
        # this works for one level of depth
        #lookup_model = self.query.model._meta.get_field(parts[-2]).rel.to
        #lookup_field = lookup_model._meta.get_field(parts[-1])

        lookup_model = self.query.model
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

        return u"%s.%s" % (
            qn(lookup_model._meta.db_table), 
            qn(lookup_field.attname),
        )

    def negated_block(self, sql):
        return u"NOT (%s)" % (sql)

    def _check_subnodes(self, node, query):
        for child in node.children:
            if isinstance(child, BaseTree):
                self._check_subnodes(child, query)
                continue

            key, value = child
            if "__" not in key:
                continue

            parts = key.split("__")

            try:
                field, target, opts, join_list, last, extra_filters = query.setup_joins(
                    parts, query.model._meta, query.get_initial_alias(), True, True, allow_explicit_fk=True,
                    can_reuse=None, negate=False,
                    process_extras=True)
            except MultiJoin as e:
                pass

    def add_to_query(self, query, alias=None):
        self._check_subnodes(self, query)
        query.where.add(ExtraWhereStatement(query, self), self.connector)

    
class ExtraWhereStatement(object):
    def __init__(self, query, node):
        self.node = node
        self.query = query

    def as_sql(self, qn, connection):
        return self.node.as_sql(qn, connection, self.query)
