# -*- coding: utf-8 -*-
from django.db.models import signals
from django.db.backends import signals as backend_signals
from django.db.utils import DatabaseError
from django.conf import settings
from django.utils.importlib import import_module

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
    from django.db import models

    meta_orm_class = getattr(sender, 'OrmMeta', None)
    if not meta_orm_class:
        meta_orm_obj = OrmMeta()
    else:
        meta_orm_obj = meta_orm_class()
        options = getattr(meta_orm_obj, 'options', {})

        if 'cache_object' not in options:
            options['cache_object'] = DEFAULT_CACHE_ENABLED
        
        if 'default_timeout' not in options:
            options['default_timeout'] = DEFAULT_CACHE_TIMEOUT

        meta_orm_obj.options = options
    
    sender.add_to_class('_orm_meta', meta_orm_obj)
    sender.add_to_class('_get_cache_key_for_pk', 
        staticmethod(lambda x,y: get_cache_key_for_pk(x, y)))
    sender.add_to_class('cache_key', 
        property(lambda x: x._get_cache_key_for_pk(x.__class__, x.pk)))


signals.class_prepared.connect(ensure_default_manager)


class ConnectionCreateHandler(object):
    default_function = lambda x,y: None

    def __call__(self, sender, connection, **kwargs):
        self.sender = sender
        getattr(self, 'on_%s_connection_created' % (connection.vendor),
            self.default_function)(connection)
        
    def on_postgresql_connection_created(self, connection):
        print "Postgresql:", connection

    def on_mysql_connection_created(self, connection):
        print "MySQL:", connection

    def on_sqlite_connection_created(self, connection):
        print "Sqlite3:", connection


on_connection_created = ConnectionCreateHandler()
backend_signals.connection_created.connect(on_connection_created)


#def load_types_for_app(app_path, connection):
#    try:
#        ct_mod = import_module(app_path + ".composite_types")
#    except ImportError:
#        return
#
#    if not hasattr(ct_mod, '__register__'):
#        return
#
#    valid_types_class = set(ct_mod.__register__)
#
#    for klass_str in valid_types_class:
#        klass = getattr(ct_mod, klass_str)
#        tname, schema = klass.__name__.lower(), 'public'
#            
#        try:
#            curs = connection.cursor()
#            curs.execute(klass._create_sql_raw)
#        except DatabaseError:
#            print "Type %s already exists on database." % (tname)
#
#
#def pre_syncdb_callback(**kwargs):
#    from django.db import connection
#    installed_apps = getattr(settings, 'INSTALLED_APPS')
#    for app in installed_apps:
#        load_types_for_app(app, connection)
#
#
#from django_orm.signals import pre_syncdb
#pre_syncdb.connect(pre_syncdb_callback)
