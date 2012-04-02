# -*- coding: utf-8 -*-

from psycopg2.extras import register_hstore
from psycopg2.extras import register_composite

from django.db.backends.postgresql_psycopg2.base import CursorWrapper
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper as BaseDatabaseWrapper

from django_orm.backends.postgresql_psycopg2.creation import DatabaseCreation
from django_orm.backends.postgresql_psycopg2.operations import DatabaseOperations
from django_orm.backends.postgresql_psycopg2.pool import PoolMixIn

import psycopg2
import uuid


class DatabaseWrapperMeta(type):
    def __call__(cls, *args, **kwargs): 
        super_call = super(DatabaseWrapperMeta, cls).__call__
        instance = super_call(*args, **kwargs)

        from django_orm.postgresql.geometric import objects
        for klass_name in objects.__all__:
            klass = getattr(objects, klass_name)

            if hasattr(klass, 'register_cast'):
                klass.register_cast(instance)
        
        DatabaseWrapperMeta.__call__ = super_call
        register_hstore(instance.cursor(), globally=True, unicode=True)
        return instance


class DatabaseWrapper(PoolMixIn, BaseDatabaseWrapper):
    """
    Psycopg2 database backend that allows the use 
    of server side cursors and connection poolings
    support.
    """
    __metaclass__ = DatabaseWrapperMeta
    _pg_version = None

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.server_side_cursors = False
        self.server_side_cursor_itersize = None
        self.ops = DatabaseOperations(self)
        self.creation = DatabaseCreation(self)

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
