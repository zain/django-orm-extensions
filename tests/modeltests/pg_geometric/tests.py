# -*- coding: utf-8 -*-

from django.test import TestCase
from django_orm.core.sql import RawExpression, SqlExpression, SqlFunction, AND, OR

from .models import SomeObject
from django_orm.postgresql.geometric.objects import Point, Circle, Box

class PointTests(TestCase):
    def setUp(self):
        self.obj0 = SomeObject.objects.create(pos=Point([1,1]))
        self.obj1 = SomeObject.objects.create(pos=Point([2,1]))
        self.obj2 = SomeObject.objects.create(pos=Point([5,6]))
        self.obj3 = SomeObject.objects.create(pos=Point([4,4]))

    def tearDown(self):
        SomeObject.objects.all().delete()

    def test_casting(self):
        self.assertIsInstance(self.obj0.pos, Point)
        self.assertEqual(self.obj0.pos, Point([1,1]))

    def test_custom_instance(self):
        self.assertEqual(Point([1,1]), Point(1,1))

    def test_incorrect_constructor(self):
        with self.assertRaises(ValueError):
            x = Point([1,2,3])

        with self.assertRaises(ValueError):
            x = Point(1,2,3)

        with self.assertRaises(ValueError):
            x = Point(1)
