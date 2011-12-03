# -*- coding: utf-8 -*-


from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as BaseDatabaseWrapper
from django_orm.backends.postgresql_psycopg2.pool import PoolMixIn

class DatabaseWrapper(PoolMixIn, BaseDatabaseWrapper):
    pass
