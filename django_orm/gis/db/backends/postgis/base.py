# -*- coding: utf-8 -*-


from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as BaseDatabaseWrapper
from django_orm.backends.postgresql_psycopg2.pool import PoolMixIn

class DatabaseWrapper(PoolMixIn, BaseDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

    def _cursor(self, *args, **kwargs):
        return super(DatabaseWrapper, self)._cursor(*args, **kwargs)
