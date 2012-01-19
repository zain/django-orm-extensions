# -*- coding: utf-8 -*-

from psycopg2.extras import register_hstore
from django.db.backends.postgresql_psycopg2.base import CursorWrapper
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper as BaseDatabaseWrapper

from django_orm.backends.postgresql_psycopg2.creation import DatabaseCreation
from django_orm.backends.postgresql_psycopg2.operations import DatabaseOperations
from django_orm.backends.postgresql_psycopg2.pool import PoolMixIn

import psycopg2
import uuid

class DatabaseWrapper(PoolMixIn, BaseDatabaseWrapper):
    """
    Psycopg2 database backend that allows the use 
    of server side cursors and connection poolings
    support.
    """
    _pg_version = None

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.server_side_cursors = False
        self.server_side_cursor_itersize = None
        self.ops = DatabaseOperations(self)
        self.creation = DatabaseCreation(self)

    def _register(self):
        self._register = lambda: None
        #self.creation.install_hstore_contrib()
        register_hstore(self.connection, globally=True, unicode=True)

    def _cursor(self):
        """
        Returns a unique server side cursor if they are enabled, 
        otherwise falls through to the default client side cursors.
        """

        cursor = super(DatabaseWrapper, self)._cursor()
        if self.server_side_cursors:
            cursor = self.connection.cursor(name='cur%s' %\
                str(uuid.uuid4()).replace('-', ''))
            cursor.tzinfo_factory = None
            if self.server_side_cursor_itersize is not None:
                cursor.itersize = self.server_side_cursor_itersize
            cursor = CursorWrapper(cursor)

        self._register()
        if not hasattr(self, '_version'):
            try:
                from django.db.backends.postgresql.version import get_version
                self.__class__._version = get_version(cursor)
            except ImportError:
                pass

        if self._pg_version is None:
            self._pg_version = self.postgres_version
        return cursor
            
    @property
    def postgres_version(self):
        from django_orm.backends.postgresql_psycopg2.version import get_version
        if not hasattr(self, '_postgres_version'):
            self.__class__._postgres_version = get_version(self.connection)
        return self._postgres_version
