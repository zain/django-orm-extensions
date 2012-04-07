# -*- coding: utf-8 -*-

from django_orm.utils.aggregates import AggregateNode

class HstoreSlice(AggregateNode):
    """
    Obtain dictionary with only selected keys.

    Usage example::
        
        queryset = SomeModel.objects\
            .inline_annotate(HstoreSlice("data", ['v']))
    """

    sql_template = '%(function)s(%(field)s, %%s)'
    sql_function = 'slice'


class HstorePeek(AggregateNode):
    """
    Obtain values from hstore field.
    Usage example::
        
        queryset = SomeModel.objects\
            .inline_annotate(peeked=HstorePeek("data", "v"))
    """

    sql_template = '%(field)s -> %%s'


class HstoreKeys(AggregateNode):
    """
    Obtain keys from hstore fields.
    Usage::
        
        queryset = SomeModel.objects\
            .inline_annotate(keys=HstoreKeys("somefield"))
    """

    sql_function = 'akeys'
