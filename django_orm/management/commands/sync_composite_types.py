# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.conf import settings

from django.utils.importlib import import_module
from django.db import transaction
from django.db import connection
from django.db.utils import DatabaseError

# TODO: using parameter

class Command(BaseCommand):
    @transaction.commit_manually
    def load_types_for_app(self, app_path):
        try:
            ct_mod = import_module(app_path + ".composite_types")
        except ImportError:
            return

        if not hasattr(ct_mod, '__register__'):
            return

        valid_types_class = set(ct_mod.__register__)

        for klass_str in valid_types_class:
            klass = getattr(ct_mod, klass_str)
            tname, schema = klass.__name__.lower(), 'public'
            
            try:
                curs = connection.cursor()
                curs.execute(klass._as_create_sql())
                transaction.commit()
            except DatabaseError:
                print "Type %s already exists on database." % (tname)
                transaction.rollback()
            
            #from psycopg2.extras import register_composite
            #register_composite(tname, curs, globally=True)

        transaction.commit()
    
    def handle(self, *args, **options):
        installed_apps = getattr(settings, 'INSTALLED_APPS')
        for app in installed_apps:
            self.load_types_for_app(app)

