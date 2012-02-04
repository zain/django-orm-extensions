# -*- coding: utf-8 -*-

from itertools import repeat

from django.utils.encoding import force_unicode
from django.db import models, connections, transaction

def auto_update_index_handler(sender, instance, *args, **kwargs):
    sender._orm_manager.update_index(pk=instance.pk, using=kwargs['using'])

class SearchManagerMixIn(object):
    vector_field = None

    def __init__(self, fields=None, search_field='search_index', 
                                    config='pg_catalog.english',
                                    auto_update_index = False):
        self.fields = None
        if fields is not None:
            if isinstance(fields, (list, tuple)):
                if len(fields) > 0 and isinstance(fields[0], (list,tuple)):
                    self.fields = fields
                else:
                    self.fields = [(x, None) for x in fields]

        self.vector_field = search_field
        self.default_weight = 'A'
        self.config = config
        self.auto_update_index = auto_update_index
        super(SearchManagerMixIn, self).__init__()

    def contribute_to_class(self, cls, name):
        # Add instance method for update index.
        _update_index = lambda x: x._orm_manager.update_index(pk=x.pk)
        setattr(cls, 'update_index', _update_index)

        # Set auto update if need
        if self.auto_update_index:
            models.signals.post_save.connect(auto_update_index_handler, sender=cls)

        super(SearchManagerMixIn, self).contribute_to_class(cls, name)

    def _find_fields(self):
        fields = [f for f in self.model._meta.fields if isinstance(f,(models.CharField,models.TextField))]
        return [f.name for f in fields]

    def _vector_sql(self, field, weight=None, config=None, using=None):
        if not weight:
            weight = self.default_weight
        if not config:
            config = self.config
        f = self.model._meta.get_field(field)

        using = using if using is not None else self.db
        connection = connections[using]
        qn = connection.ops.quote_name
        sql_template = "setweight(to_tsvector('%s', coalesce(unaccent(%s), '')), '%s')"
        return sql_template % (config, qn(f.column), weight)

    def update_index(self, pk=None, config=None, using=None):
        if using is None:
            using = self.db

        sql_instances = []

        if not self.fields:
            self.fields = self._find_fields()

        sql_instances = [self._vector_sql(field, weight, config, using) \
            for field, weight in self.fields]

        vector_sql = ' || '.join(sql_instances)
        where_sql = ''
        params = []

        connection = connections[using]
        qn = connection.ops.quote_name

        if pk is not None:
            if isinstance(pk, (list, tuple)):
                params = pk
            else:
                params = [pk]

            where_sql = "WHERE %s IN (%s)" % (
                qn(self.model._meta.pk.column),
                ','.join(repeat("%s", len(params)))
            )

        sql = "UPDATE %s SET %s = %s %s;" % (
            qn(self.model._meta.db_table),
            qn(self.vector_field),
            vector_sql,
            where_sql
        )

        if not transaction.is_managed(using=using):
            transaction.enter_transaction_management(using=using)
            forced_managed = True
        else:
            forced_managed = False

        cursor = connection.cursor()
        cursor.execute(sql, params)

        try:
            if forced_managed:
                transaction.commit(using=using)
            else:
                transaction.commit_unless_managed(using=using)
        finally:
            if forced_managed:
                transaction.leave_transaction_management(using=using)


    def search(self, query, rank_field=None, rank_normalization=32, config=None,
               raw=False, using=None):

        if not config:
            config = self.config

        db_alias = using if using is not None else self.db
        connection = connections[db_alias]
        qn = connection.ops.quote_name

        function = "to_tsquery" if raw else "plainto_tsquery"
        ts_query = "%s('%s', unaccent('%s'))" % (
            function,
            config,
            force_unicode(query).replace("'","''")
        )
        where = " %s @@ %s" % (qn(self.vector_field), ts_query)

        select_dict, order = {}, []
        if rank_field:
            select_dict[rank_field] = 'ts_rank(%s, %s, %d)' % (
                qn(self.vector_field),
                ts_query, rank_normalization
            )
            order = ['-%s' % (rank_field,)]

        qs = self.all()
        if using is not None:
            qs = qs.using(using)

        # TODO: use parametrized queries
        return qs.extra(select=select_dict, where=[where], order_by=order)
