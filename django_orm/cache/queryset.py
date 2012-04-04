# -*- coding: utf-8 -*-

from django.db.models.query import QuerySet
from django.db.models.query import ITER_CHUNK_SIZE
from django.db import backend, connection

from django.conf import settings

from .utils import get_cache_key_for_pk, get_cache
from django_orm.cache.exceptions import CacheMissingWarning


CACHE_KEY_PREFIX = getattr(settings, 'ORM_CACHE_KEY_PREFIX', 'orm.cache')
CACHE_FETCH_BY_ID = getattr(settings, 'ORM_CACHE_FETCH_BY_ID', False)
DEFAULT_CACHE_TIMEOUT = getattr(settings, 'ORM_CACHE_DEFAULT_TIMEOUT', 60) 
DEFAULT_CACHE_ENABLED = getattr(settings, 'ORM_CACHE_DEFAULT_ENABLED', False)


class ObjectCacheMixIn(object):
    cache_fetch_by_id = False
    cache_object_enable = DEFAULT_CACHE_ENABLED
    cache_key_prefix = CACHE_KEY_PREFIX
    cache_timeout = DEFAULT_CACHE_TIMEOUT

    def __init__(self, *args, **kwargs):
        super(ObjectCacheMixIn, self)__init__(*args, **kwargs)

        orm_meta = getattr(self.model, '_orm_meta', None)
        if not orm_meta:
            return

        options = getattr(orm_meta, 'options', None)
        if not options:
            return

        self.cache_object_enable = options['cache_object']
        self.cache_timeout = options['default_timeout']

    def _clone(self, klass=None, **kwargs):
        qs = super(ObjectCacheMixIn, self)._clone(klass, **kwargs)
        qs.cache_fetch_by_id = self.cache_fetch_by_id
        qs.cache_object_enable = self.cache_object_enable
        qs.cache_timeout = self.cache_timeout
        return qs

    def cache(self, timeout=None):
        if self.cache_object_enable:
            if timeout:
                qs = self._clone()
                qs.cache_timeout = timeout
                return qs

            return self

        if not timeout:
            timeout = self.cache_timeout

        qs = self._clone()
        qs.cache_object_enable = True
        qs.cache_timeout = timeout
        return qs

    def no_cache(self):
        if not self.cache_object_enable:
            pass

    




