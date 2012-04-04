# -*- coding: utf-8 -*-

from django.test import TestCase
from .models import TestModel


class UnaccentLikeTest(TestCase):
    def setUp(self):
        self.obj0 = TestModel.objects.create(name=u"Andréi", desc="Fòoo Bar")
        self.obj1 = TestModel.objects.create(name=u"Pêpe", desc="Bär Foo")

    def test


