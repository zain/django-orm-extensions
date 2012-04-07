# -*- coding: utf-8 -*-

from django.test import TestCase
from .models import TestModel, FooModel, Foo2Model

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


from django_orm.sqlite3.statements import Unaccent

class UnaccentComplexTest(TestCase):
    def setUp(self):
        self.obj0 = FooModel.objects.create(name=u"pépe", desc="Fòoo Bar")
        self.x_obj0 = Foo2Model.objects.create(parent=self.obj0)

    def test_query(self):
        qs = FooModel.manager.add_unaccent_filter(Unaccent(name="pepe") | Unaccent(name="Vesita"))
        self.assertEqual(qs.count(), 1)

    def test_query_2(self):
        qs = Foo2Model.manager.add_unaccent_filter(parent__name="pepe")
        self.assertEqual(qs.count(), 1)

    def tearDown(self):
        FooModel.manager.all().delete()
        Foo2Model.manager.all().delete()
