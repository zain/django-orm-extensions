# -*- coding: utf-8 -*-

from django.db import models
from django_orm.sqlite3.queryset import SqliteQuerySet
from django_orm.cache.manager import CacheManagerMixIn

class ManagerMixIn(object):
    def get_query_set(self):
        return SqliteQuerySet(model=self.model, using=self._db)

    def contribute_to_class(self, model, name):
        if not getattr(model, '_orm_manager', None):
            model._orm_manager = self
        super(ManagerMixIn, self).contribute_to_class(model, name)

    def unaccent(self, **kwargs):
        return self.get_query_set().unaccent(**kwargs)

    def iunaccent(self, **kwargs):
        return self.get_query_set().iunaccent(**kwargs)


class Manager(ManagerMixIn, CacheManagerMixIn, models.Manager):
    use_for_related_fields = True
