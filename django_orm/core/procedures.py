# -*- coding: utf-8 -*-

from django.db import connections, transaction

class Procedure(object):
    sql_source = None

    def create_statement(self, using='default'):
        """
        Executes create sql.

        TODO: capture all exceptions
        """

        if sql_source is None:
            return False

        connection = connections[using]

        if not transaction.is_managed(using=using):
            transaction.enter_transaction_management(using=using)
            forced_managed = True
        else:
            forced_managed = False

        cursor = connection.cursor()
        cursor.executemany(self.sql_source)
        
        try:
            if forced_managed:
                transaction.commit(using=using)
            else:
                transaction.commit_unless_managed(using=using)
        finally:
            if forced_managed:
                transaction.leave_transaction_management(using=using)
        
        return True

    def call(self, *args):
        # TODO
        pass


