# -*- coding: utf-8 -*-

__version__ = (3, 0, 0, 'beta', 1)

from .signals import pre_syncdb

def patch_django_syncdb_command():
    from django.core.management.commands import syncdb
    original_command = syncdb.Command

    class PatchedCommand(original_command):
        def handle_noargs(self, **options):
            pre_syncdb.send(sender=self)
            super(PatchedCommand, self).handle_noargs(**options)

    syncdb.Command = PatchedCommand

# monky patching django syncdb command for
# emit pre_syncdb signal
patch_django_syncdb_command()

# import dispatch module
from . import dispatch
