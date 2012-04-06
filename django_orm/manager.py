# -*- coding: utf-8 -*-

class ManagerMixIn(object):
    """
    Base django-orm manager mixin.
    """
    def contribute_to_class(self, model, name):
        if not getattr(model, '_orm_manager', None):
            model._orm_manager = self
        super(ManagerMixIn, self).contribute_to_class(model, name)

    def unaccent(self, **kwargs):
        return self.get_query_set().unaccent(**kwargs)

    def iunaccent(self, **kwargs):
        return self.get_query_set().iunaccent(**kwargs)
