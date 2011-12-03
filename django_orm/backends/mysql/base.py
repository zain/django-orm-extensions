# -*- coding: utf-8 -*-

from django import VERSION
from django.db.backends.util import truncate_name
from django.db.backends.mysql.base import connection_created, django_conversions, CursorWrapper
from django.db.backends.mysql.base import DatabaseWrapper as BaseDatabaseWrapper
from django.db.backends.util import truncate_name

from django.core import signals
from django.conf import settings

from django_orm.pool import QueuePool, PersistentPool
from django_orm import POOLTYPE_PERSISTENT, POOLTYPE_QUEUE
from django_orm.backends.mysql.creation import DatabaseCreation

import threading
import datetime
import logging
import uuid

log = logging.getLogger(__name__)

from django_orm.backends.mysql.pool import PoolMixIn

class DatabaseWrapper(PoolMixIn, BaseDatabaseWrapper):
    """
    Mysql database backend with connection poolings
    support.

    """

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = DatabaseCreation(self)
