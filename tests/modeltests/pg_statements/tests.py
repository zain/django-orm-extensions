# -*- coding: utf-8 -*-

from django.test import TestCase


class StatementsTests(TestCase):
    def test_raw_statements(self):
        from django_orm.utils.statements import RawStatement, AND, OR
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
