# -*- coding: utf-8 -*-

from psycopg2.extensions import adapt, register_adapter, AsIs, new_type, register_type
from django.db import models
from django.utils.encoding import force_unicode


class ComplexTypeError(Exception):
    pass


def adapt_complex(obj):
    return AsIs(obj._as_sql())
 

class CompositeTypeMeta(type):
    def __init__(cls, name, bases, attrs):
        super(CompositeTypeMeta, cls).__init__(name, bases, attrs)
        
        cls.fields = {}
        for key, value in attrs.iteritems():
            if isinstance(value, CompositeField):
                setattr(value, '_name', key)
                cls.fields[key] = value
        
        if "order" not in attrs:
            raise Exception("order parameter is mandatory")
        elif len(attrs['order']) > 0:
            register_adapter(cls,  adapt_complex)

        cls.type_name = classmethod(lambda x: cls.__name__.lower())
        setattr(cls, '_as_sql_fields', classmethod(CompositeTypeMeta._as_sql_fields))
        setattr(cls, '_as_create_sql', classmethod(CompositeTypeMeta._create_sql))
        setattr(cls, '_as_sql', classmethod(CompositeTypeMeta._as_sql))

    def _as_sql_fields(self):
        return u",\n    ".join([x._as_sql() for x in \
            [self.fields[oi] for oi in self.order]])
        
    def _create_sql(self):
        template = u"CREATE TYPE %s AS (\n    %s\n);"
        return template % (
            self.type_name(),
            self._as_sql_fields()
        )

    def _as_sql(self):
        template = u"ROW(%s)"

        lista = []
        for item in [self.fields[oi]._value for oi in self.order]:
            if isinstance(item, (long, int, float)):
                lista.append(unicode(item))
            elif isinstance(item, CompositeType):
                lista.append(item._as_sql())
            else:
                lista.append("'%s'" % (unicode(item)))

        return template % (
            u", ".join(lista),
        )


class CompositeField(object):
    _value = None
    _name = None

    def __init__(self, field_repr, coerce=None):
        self.field_repr = field_repr
        self.coerce = coerce

    def __get__(self, instance, owner):
        return self._value or None

    def __set__(self, instance, value):
        self._value = value
        if self.coerce:
            try:
                self._value = self.coerce(self._value)
            except Exception as e:
                raise ComplexTypeError(str(e))

    def _as_sql(self):
        return u"%s %s" % (self._name, self.field_repr)


class CompositeType(object):
    __metaclass__ = CompositeTypeMeta
    order = ()

    def __init__(self, *args, **kwargs):
        if len(args) > 0 and len(args) == len(order):
            try:
                for oitem in self.order:
                    setattr(self, oitem, args.pop())
            except IndexError:
                pass
        elif kwargs:
            for oitem in self.order:
                setattr(self, oitem, kwargs.get(oitem, None))

    def _with_wrapper(self, wrapper):
        for oitem in self.order:
            setattr(self, oitem, getattr(wrapper, oitem, None))

    def __repr__(self):
        return u"<CompositeType %s>" % (
            ", ".join(["%s=%s" % (x._name, x._value) \
                for x in self.fields.itervalues()]))

    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name # Quoting once is enough.
        return '"%s"' % name


class CompositeModelField(models.Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self._type = kwargs.pop('type')
        super(CompositeModelField, self).__init__(*args, **kwargs)

    def get_prep_lookup(self, lookup_type, value):
        raise TypeError("At the moment is not implemented")

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        return get_prep_lookup(lookup_type, value)

    def db_type(self, connection):
        return self._type.type_name()

    def to_python(self, value):
        if value and isinstance(value, (list,tuple)):
            obj = self._type()
            obj._with_wrapper(value)
            return obj
        return value
