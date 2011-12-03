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

    def close(self):
        global pool

        if self.connection is None:
            return 

        if not self.pool_enabled and self.settings_dict['NAME'] != ":memory:":
            BaseDatabaseWrapper.close(self)
            return

        pool.putconn(self.connection)
        self.connection = None

    def _cursor(self):
        global pool
        if not pool:
            poolclass = PersistentPool \
                if self.pool_type == POOLTYPE_PERSISTENT else QueuePool
            pool = poolclass(self.settings_dict)

        if self.connection is None:
            self.connection = pool.getconn()
        
        cursor = super(PoolMixIn, self)._cursor()
        self.connection.create_function("unaccent", 1, _sqlite_unaccent)
        return cursor


def _sqlite_unaccent(data):
    if isinstance(data, unicode):
        from django_orm.utils import remove_diacritic
        return remove_diacritic(data)
    return data
