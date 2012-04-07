# -*- coding: utf-8 -*-

from django_orm.utils.statements import Statement


class HstoreSlice(Statement):
    """
    Obtain dictionary with only selected keys.

    Usage example::
        
        queryset = SomeModel.objects\
            .inline_annotate(sliced=HstoreSlice("data").as_aggregate(['v']))
    """

    sql_template = '%(function)s(%(field)s, %%s)'
    sql_function = 'slice'


class HstorePeek(Statement):
    """
    Obtain values from hstore field.
    Usage example::
        
        queryset = SomeModel.objects\
            .inline_annotate(peeked=HstorePeek("data").as_aggregate("v"))
    """

    sql_template = '%(field)s -> %%s'


class HstoreKeys(Statement):
    """
    Obtain keys from hstore fields.
    Usage::
        
        queryset = SomeModel.objects\
            .inline_annotate(keys=HstoreKeys("somefield").as_aggregate())
    """

    sql_function = 'akeys'
