# -*- coding: utf-8 -*-

from django.test import TestCase
from django_orm.postgresql.aggregates import Unaccent

from .models import TestModel
from .models import Person

class UnaccentLikeTest(TestCase):
    def setUp(self):
        self.obj0 = TestModel.objects.create(name=u"Andréi", desc="Fòoo Bar")
        self.obj1 = TestModel.objects.create(name=u"Pêpe", desc="Bär Foo")

    def test_unaccent_method(self):
        qs = TestModel.manager.unaccent(name=u"Andrei")
        self.assertEqual(qs.count(), 1)

        qs = TestModel.manager.unaccent(name=u"andrei")
        self.assertEqual(qs.count(), 0)

    def test_iunaccent_method(self):
        qs = TestModel.manager.iunaccent(name=u"andrei")
        self.assertEqual(qs.count(), 1)

class TestUnaccent(TestCase):
    def setUp(self):
        self.p1 = Person.objects.create(name='Andréi')
        self.p2 = Person.objects.create(name='Pèpâ')

    def tearDown(self):
        self.p1.delete()
        self.p2.delete()
    
    def test_annotate(self):
        qs = Person.manager.inline_annotate(
            name_unaccent = Unaccent("name").as_aggregate()
        )
        qs = list(qs)
        self.assertEqual(qs[0].name_unaccent, 'Andrei')
        self.assertEqual(qs[1].name_unaccent, 'Pepa')

    def test_statement(self):
        qs = Person.manager.where(Unaccent("name").as_statement("=", "Andrei"))
        self.assertEqual(qs.count(), 1)
