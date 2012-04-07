# -*- coding: utf-8 -*-

from django.db import models
from django_orm.utils.statements import Statement

class Unaccent(Statement):
    sql_function = 'unaccent'
