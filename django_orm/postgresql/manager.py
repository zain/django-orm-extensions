# -*- coding: utf-8 -*-

from django_orm.postgresql.fts.manager import SearchManagerMixIn
from django_orm.postgresql.queryset import PgQuerySet
from django.db import models

class ManagerMixIn(object):
    """
    Base django-orm manager mixin for postgresql database backend.
    """

    def get_query_set(self):
        return PgQuerySet(model=self.model, using=self._db)

    def contribute_to_class(self, model, name):
        if not getattr(model, '_orm_manager', None):
            model._orm_manager = self
        super(ManagerMixIn, self).contribute_to_class(model, name)

    def unaccent(self, **kwargs):
        return self.get_query_set().unaccent(**kwargs)

    def iunaccent(self, **kwargs):
        return self.get_query_set().iunaccent(**kwargs)


class CacheManagerMixIn(object):
    """
    Base django-orm manager mixin with cache functionality methods.
    """

    def cache(self, *args, **kwargs):
        """ 
        Active cache for this queryset 
        """
        queryset = self.get_query_set()
        cache_method = getattr(queryset, 'cache', None)
        if cache_method:
            return cache_method(*args, **kwargs)

        return queryset

    def no_cache(self, *args, **kwargs):
        """
        Deactive cache for this queryset. 
        """
        queryset = self.get_query_set()
        cache_method = getattr(queryset, 'no_cache', None)
        if cache_method:
            return cache_method(*args, **kwargs)
        return queryset

    def contribute_to_class(self, model, name):
        if hasattr(model, '_orm_meta') and model._orm_meta.options['cache_object']:
            signals.post_save.connect(invalidate_object, sender=model)
            signals.post_delete.connect(invalidate_object, sender=model)
        super(CacheManagerMixIn, self).contribute_to_class(model, name)


class Manager(ManagerMixIn, CacheManagerMixIn, models.Manager):
    """
    Normal user manager. With cache methods.
    Without fulltext search functionality.
    """
    use_for_related_fields = True


class FtsManager(SearchManagerMixIn, ManagerMixIn, CacheManagerMixIn, models.Manager):
    """
    Base django-orm manager with full text search methods.
    """
    use_for_related_fields = True


class ArrayDataMixin(object):
    def get_query_set(self):
        # TODO: this is invalid queryset
        return PgQuerySet(model=self.model, using=self._db)

    def array_slice(self, attr, x, y, **params):
        """
        Deactive cache for this queryset. 
        """
        return self.filter(**params).array_slice(attr, x, y)

    def array_length(self, attr, **params):
        """
        Get length from some array field. Only for postgresql vendor. 
        """
        return self.filter(**params).array_length(attr)


class ArrayManager(ArrayDataMixin, CacheManagerMixIn, models.Manager):
    """
    Django-orm base manager for use with array fields.
    """
    use_for_related_fields = True

