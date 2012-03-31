# -*- coding: utf-8 -*-

from django.db import connection
from django.utils.unittest import TestCase
from django.utils import unittest
from django.db import transaction, IntegrityError

from .models import Item

class TestPoolBackend(TestCase):

    def setUp(self):
        Item.objects.all().delete()

    @unittest.skipIf(connection.vendor != 'postgresql', "Only for postgresql")
    def test_savepoint_test(self):
        with transaction.commit_on_success():

            Item.objects.create(name='item 1')
            Item.objects.create(name='item 2')

            sid = transaction.savepoint()
            try:
                duplicated = Item.objects.create(name='item 1')
                transaction.savepoint_commit(sid)
            except IntegrityError:
                transaction.savepoint_rollback(sid)

            Item.objects.create(name='item 3')
            Item.objects.get_or_create(name='item 1')
