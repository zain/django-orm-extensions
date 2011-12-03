# -*- coding: utf-8 -*-

from django.conf import settings
from django_orm.pool import QueuePool, PersistentPool
from django_orm import POOLTYPE_PERSISTENT, POOLTYPE_QUEUE

pool = None

class PoolMixIn(object):
    pool_enabled = False

    def __init__(self, *args, **kwargs):
        super(PoolMixIn, self).__init__(*args, **kwargs)
        options = self.settings_dict.get('OPTIONS', {})
        self.pool_type = options.get('POOLTYPE', POOLTYPE_PERSISTENT)
        self.pool_enabled = options.pop('POOL_ENABLED', True)

    def _try_connected(self):
        if self.connection is not None:
            try:
                self.connection.ping()
                return True
            except DatabaseError:
                self.connection.close()
                self.connection = None
        return False

    def close(self):
        global pool
        if self.connection is None:
            return

        if not self.pool_enabled:
            self.connection.close()
            self.connection = None
            return

        if not self.connection.ping():
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

        if not self.connection:
            self.connection = pool.getconn()
            if self.connection is not None and not self._valid_connection():
                self.connection.close()
                self.connection = None

        return super(PoolMixIn, self)._cursor()
