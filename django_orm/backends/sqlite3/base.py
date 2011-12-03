# -*- coding: utf-8 -*-

from django.db.backends.sqlite3.base import DatabaseWrapper as BaseDatabaseWrapper
from django_orm.pool import QueuePool, PersistentPool
from django_orm import POOLTYPE_PERSISTENT, POOLTYPE_QUEUE
from django_orm.backends.sqlite3.creation import DatabaseCreation
from django_orm.backends.sqlite3.pool import PoolMixIn

class DatabaseWrapper(PoolMixIn, BaseDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = DatabaseCreation(self)
