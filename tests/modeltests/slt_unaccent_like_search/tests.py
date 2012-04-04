# -*- coding: utf-8 -*-

from django.test import TestCase
from .models import TestModel

class UnaccentLikeTest(TestCase):
    def setUp(self):
        self.obj0 = TestModel.objects.create(name=u"Andréi", desc="Fòoo Bar")
        self.obj1 = TestModel.objects.create(name=u"Pêpe", desc="Bär Foo")

    def test_unaccent_method(self):
        qs = TestModel.manager.unaccent(name=u"Andrei")
        self.assertEqual(qs.count(), 1)

        qs = TestModel.manager.unaccent(name=u"andri")
        self.assertEqual(qs.count(), 0)

    def test_iunaccent_method(self):
        qs = TestModel.manager.iunaccent(name=u"andrei")
        self.assertEqual(qs.count(), 1)
