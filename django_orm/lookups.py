# -*- coding: utf-8 -*-

from django.utils import tree
from django.db.models.sql.datastructures import MultiJoin

class BaseTree(tree.Node):
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
        super(BaseTree, self).__init__(children=list(args) + kwargs.items())

    def _combine(self, other, conn):
        if not isinstance(other, (BaseTree)): 
            raise TypeError(other)
        obj = type(self)()
        obj.add(self, conn)
        obj.add(other, conn)
        #obj.query = self.query
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

    def sql_condition(self, parts, value, qn):
        raise NotImplemented("Can be reimplemented on subclass.")

    def qn(self, name):
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
            parts = key.split("__")
            if len(parts) <= 1:
                continue

            opts = query.model._meta
            alias = query.get_initial_alias()
            allow_many = True

            try:
                field, target, opts, join_list, last, extra_filters = query.setup_joins(
                    parts, opts, alias, True, allow_many, allow_explicit_fk=True,
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
