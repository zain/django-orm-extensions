# -*- coding: utf-8 -*-

from django.test import TestCase
from django_orm.core.sql import RawExpression, SqlExpression, SqlFunction, AND, OR

from .models import Person

class SqlExpressionsTests(TestCase):
    def test_raw_statements_0(self):
        expresion_instance = OR(
            AND(
                RawExpression("name = %s", "Andrei"), 
                RawExpression("age = %s", 14),
            ),
            AND(
                RawExpression("name = %s", "Vesita"),
                RawExpression("age = %s", 14),
            )
        )
        sql, params = expresion_instance.as_sql(None, None)
        self.assertEqual(sql.to_str(), "(name = %s AND age = %s) OR (name = %s AND age = %s)")
        self.assertEqual(params, ['Andrei', 14, 'Vesita', 14])

    def setUp(self):
        Person.objects.all().delete()

    def test_string_sample_statement(self):
        class BitLength(SqlFunction):
            sql_function = "bit_length"

        obj = Person.objects.create(name="jose")
        queryset = Person.objects.where(
            SqlExpression(BitLength("name"), "=", 32)
        )
        self.assertEqual(queryset.count(), 1)
