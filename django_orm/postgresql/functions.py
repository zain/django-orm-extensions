# -*- coding: utf-8 -*-

from django.db import models
from django_orm.core.sql import SqlFunction

class Unaccent(SqlFunction):
    sql_function = 'unaccent'
