# -*- coding: utf-8 -*-
from django.db.models import signals
from django.conf import settings

import logging; log = logging.getLogger('orm.cache')


DEFAULT_CACHE_TIMEOUT = getattr(settings, 'ORM_CACHE_DEFAULT_TIMEOUT', 60)
DEFAULT_CACHE_ENABLED = getattr(settings, 'ORM_CACHE_DEFAULT_ENABLED', False)

class OrmMeta(object):
    options = {
        'cache_object': DEFAULT_CACHE_ENABLED,
        'cache_queryset': DEFAULT_CACHE_ENABLED,
        'default_timeout': DEFAULT_CACHE_TIMEOUT,
    }

def ensure_default_manager(sender, **kwargs):
    from django_orm.cache.utils import get_cache_key_for_pk
    from django_orm.cache.invalidator import invalidate_object
    from django_orm.manager import FTSManager as Manager
    from django.db import models

    meta_orm_class = getattr(sender, 'OrmMeta', None)
    if not meta_orm_class:
        meta_orm_obj = OrmMeta()
    else:
        meta_orm_obj = meta_orm_class()
        options = getattr(meta_orm_obj, 'options', {})

        if 'cache_object' not in options:
            options['cache_object'] = DEFAULT_CACHE_ENABLED
        
        if 'cache_queryset' not in options:
            options['cache_queryset'] = DEFAULT_CACHE_ENABLED
        
        if options['cache_queryset']:
            options['cache_object'] = True

        if 'default_timeout' not in options:
            options['default_timeout'] = DEFAULT_CACHE_TIMEOUT

        meta_orm_obj.options = options
    
    sender.add_to_class('_orm_meta', meta_orm_obj)
    if not getattr(sender, '_orm_manager', None):
        sender.add_to_class('_orm_manager', Manager())

    sender.add_to_class('_get_cache_key_for_pk', 
        staticmethod(lambda x,y: get_cache_key_for_pk(x, y)))
    sender.add_to_class('cache_key', 
        property(lambda x: x._get_cache_key_for_pk(x.__class__, x.pk)))

signals.class_prepared.connect(ensure_default_manager)


from django.db import DatabaseError
from django.utils.importlib import import_module
from django_orm.signals import register_backend
from psycopg2.extras import register_composite
import inspect
from psycopg2 import extensions as _ext


def load_types_for_app(app_path, connection):
    try:
        ct_mod = import_module(app_path +'.composite_types')
    except ImportError:
        return

    valid_types_class = []
    for typeclass in dir(ct_mod):
        if typeclass.startswith('_'):
            continue
        valid_types_class.append(typeclass)
    
    cursor = connection.cursor()
    for type_class_str in set(valid_types_class):
        klass = getattr(ct_mod, type_class_str)
        if not getattr(klass, '_register', False) or not inspect.isclass(klass):
            continue

        tname, schema = klass.__name__.lower(), 'public'
        conn_status = connection.connection.status
        conn = connection.connection
        curs = conn.cursor()

        curs.execute("""\
SELECT t.oid, attname, atttypid
FROM pg_type t
JOIN pg_namespace ns ON typnamespace = ns.oid
JOIN pg_attribute a ON attrelid = typrelid
WHERE typname = %s and nspname = %s
ORDER BY attnum;
""", (tname, schema))

        recs = curs.fetchall()

        # revert the status of the connection as before the command
        if (conn_status != _ext.STATUS_IN_TRANSACTION
        and conn.isolation_level != _ext.ISOLATION_LEVEL_AUTOCOMMIT):
            conn.rollback()
        
        if not recs:
            curs.execute(klass._as_create_sql())
            conn.commit()
        
        register_composite(tname, conn, globally=True)


def register_complex_types(sender, connection, **kwargs):
    if not getattr(connection, '_composite_registered', False):
        installed_apps = getattr(settings, 'INSTALLED_APPS')
        for app in installed_apps:
            load_types_for_app(app, connection)

        setattr(connection, '_composite_registered', True)

register_backend.connect(register_complex_types, \
    dispatch_uid='complex_types_register')
