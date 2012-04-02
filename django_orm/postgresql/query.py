# -*- coding: utf-8 -*-

from django.db.models.sql.query import Query
from django_orm.postgresql.constants import QUERY_TERMS
from django_orm.postgresql.sql import PgWhereNode

class PgQuery(Query):
    query_terms = QUERY_TERMS
    def __init__(self, model):
        super(PgQuery, self).__init__(model, where=PgWhereNode)
