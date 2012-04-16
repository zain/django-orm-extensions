# -*- coding: utf-8 -*-

from django.db import connections, transaction
from django_orm.core.util.transaction import TransactionContext

from .exceptions import UndefinedProcedureSource, UndefinedProcedureName

class Procedure(object):
    sql_source = None
    sql_name = None
    returns_data = False

    def create_statement(self, using='default'):
        """
        Executes create sql.

        TODO: capture all exceptions
        """

        if sql_source is None:
            raise UndefinedProcedureSource("sql_source is None")

        connection = connections[using]
        with TransactionContext(using=using):
            cursor = connection.cursor()
            cursor.executemany(self.sql_source)
        
        return True

    @classmethod
    def _postgresq_call(cls, *args, **kwargs):
        using = kwargs.pop('using')
        
        connection = connections[using]
        cursor = connection.cursor()

        with TransactionContext(using=using):
            cursor.call(cls.sql_name, args)

        # TODO:
        #  * simple queryset implementation
        #  * simple object casting

        while True:
            rows = cursor.fetchmany()
            if len(rows) == 0:
                break

            for row in rows:
                yield row
            
    
    @classmethod
    def call(cls, *args, **kwargs):
        if "using" not in kwargs:
            kwargs['using'] = 'default'

        if cls.sql_name == None:
            raise UndefinedProcedureName("sql_name is None")

        # at the moment only postgresql procedure support.
        cls._postgresq_call(*args, **kwargs)
