# -*- coding: utf-8 -*-

from django.db import connection
from django_orm.postgresql.aggregates import Unaccent
from django.utils.unittest import TestCase
from django.utils import unittest
from django.db import connection

from .models import Person

class TestFts(TestCase):
    def setUp(self):
        Person.objects.all().delete()

        self.p1 = Person.objects.create(
            name=u'Andréi',
            description=u"Python programmer",
        )
        self.p2 = Person.objects.create(
            name=u'Pèpâ',
            description=u"Is a housewife",
        )

    @unittest.skipIf(connection.vendor != 'postgresql', "Only for postgresql")
    def test_search_and(self):
        qs1 = Person.objects.search(query="programmer", raw=True)
        qs2 = Person.objects.search(query="Andrei", raw=True)

        self.assertEqual(qs1.count(), 1)
        self.assertEqual(qs2.count(), 1)

    @unittest.skipIf(connection.vendor != 'postgresql', "Only for postgresql")
    def test_search_and_2(self):
        qs1 = Person.objects.search(query="Andrei & programmer", raw=True)
        qs2 = Person.objects.search(query="Pepa & housewife", raw=True)
        qs3 = Person.objects.search(query="Pepa & programmer", raw=True)

        self.assertEqual(qs1.count(), 1)
        self.assertEqual(qs2.count(), 1)
        self.assertEqual(qs3.count(), 0)

    @unittest.skipIf(connection.vendor != 'postgresql', "Only for postgresql")
    def test_search_or(self):
        qs1 = Person.objects.search(query="Andrei | Pepa", raw=True)
        qs2 = Person.objects.search(query="Andrei | Pepo", raw=True)
        qs3 = Person.objects.search(query="Pèpâ | Andrei", raw=True)
        qs4 = Person.objects.search(query="Pepo | Francisco", raw=True)

        self.assertEqual(qs1.count(), 2)
        self.assertEqual(qs2.count(), 1)
        self.assertEqual(qs3.count(), 2)
        self.assertEqual(qs4.count(), 0)
    
    @unittest.skipIf(connection.vendor != 'postgresql', "Only for postgresql")
    def test_update_indexes(self):
        self.p1.name = 'Francisco'
        self.p1.save()

        qs = Person.objects.search(query="Pepo | Francisco", raw=True)
        self.assertEqual(qs.count(), 1)

    @unittest.skipIf(connection.vendor != 'postgresql', "Only for postgresql")
    def test_search_query_lookup(self):
        qs = Person.objects.filter(search_index__query="Andrei programmer")
        self.assertEqual(qs.count(), 1)

    @unittest.skipIf(connection.vendor != 'postgresql', "Only for postgresql")
    def test_search_query_raw_lookup(self):
        qs = Person.objects.filter(search_index__query_raw="Andrei & programmer")
        self.assertEqual(qs.count(), 1)
