# -*- coding: utf-8 -*-

from django.conf import settings
from django_orm.pool import QueuePool, PersistentPool
from django_orm import POOLTYPE_PERSISTENT, POOLTYPE_QUEUE
import psycopg2

pool = None

class PoolMixIn(object):
    pool_enabled = False
    pool_type = POOLTYPE_PERSISTENT

    def __init__(self, *args, **kwargs):
        super(PoolMixIn, self).__init__(*args, **kwargs)
        options = self.settings_dict.get('OPTIONS', {})
        self.pool_type = options.get('POOLTYPE', POOLTYPE_PERSISTENT)
        self.pool_enabled = options.pop('POOL_ENABLED', False)

    def _try_connected(self):
        """
        Try if connection object is connected
        to a database.

        :param psycopg.connection connection: db connection.
        :returns: True or False
        :rtype: bool
        """
        try:
            self.connection.cursor().execute("SELECT 1;")
            return True
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            return False

    def close(self):
        global pool
        if self.connection is None:
            return
        
        if not self.pool_enabled:
            self.connection.close()
            self.connection = None
            return

        if not self.connection.closed:
            pool.putconn(self.connection)

        self.connection = None

    def _cursor(self):
        """
        Returns a unique server side cursor if they are enabled, 
        otherwise falls through to the default client side cursors.
        """
        global pool
        if not pool:
            poolclass = PersistentPool \
                if self.pool_type == POOLTYPE_PERSISTENT else QueuePool
            pool = poolclass(self.settings_dict)
        
        if self.connection is None:
            self.connection = pool.getconn()
            if self.connection is not None and not self._try_connected():
                self.connection = None

        if self.connection is not None:
            self.connection.set_client_encoding('UTF8')
            self.connection.set_isolation_level(self.isolation_level)

        return super(PoolMixIn, self)._cursor()
