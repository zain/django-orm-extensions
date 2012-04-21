# -*- coding: utf-8 -*-

from django.test import TestCase

from django_orm.postgresql.fields.bytea import ByteaField
from django_orm.core.sql import SqlExpression
from .models import ByteaModel

import hashlib
import os.path
import io


class ByteaFieldTest(TestCase):
    def setUp(self):
        ByteaModel.objects.all().delete()

    def test_internals_field(self):
        field = ByteaField()
        prep_value = field.get_db_prep_value(None, None)
        self.assertEqual(prep_value, None)

    def test_simple_insert(self):
        path = os.path.join(os.path.dirname(__file__), "test.jpg")
        data = ''

        with io.open(path, "rb") as f:
            data = f.read()

        strhash = hashlib.sha256(data).hexdigest()
        obj = ByteaModel.objects.create(data=data)
        obj = ByteaModel.objects.get(pk=obj.id)
        self.assertEqual(strhash, hashlib.sha256(obj.data).hexdigest())

    def test_insert_void(self):
        obj = ByteaModel.objects.create(data=None)
        obj = ByteaModel.objects.get(pk=obj.id)
        self.assertEqual(obj.data, None)
