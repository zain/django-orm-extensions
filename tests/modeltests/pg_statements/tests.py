# -*- coding: utf-8 -*-

from django.test import TestCase

from django_orm.utils.statements import RawStatement, Statement, AND, OR

from .models import Person


class StatementsTests(TestCase):
    def test_raw_statements_0(self):
        a = OR(
            AND(
                RawStatement("name = %s", "Andrei"), 
                RawStatement("age = %s", 14),
            ),
            AND(
                RawStatement("name = %s", "Vesita"),
                RawStatement("age = %s", 14),
            )
        )
        sql, params = a.as_sql(None, None)
        self.assertEqual(sql.to_str(), "(name = %s AND age = %s) OR (name = %s AND age = %s)")
        self.assertEqual(params, ['Andrei', 14, 'Vesita', 14])

    def setUp(self):
        Person.objects.all().delete()

    def test_string_sample_statement(self):
        class BitLengthStatement(Statement):
            sql_function = "bit_length"

        obj = Person.objects.create(name="jose")
        queryset = Person.objects.inline_statement(AND(BitLengthStatement("name", "=", 32)))
        self.assertEqual(queryset.count(), 1)
