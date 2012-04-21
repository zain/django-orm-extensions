# -*- coding: utf-8 -*-

from django.db import models
from django_orm.postgresql.manager import Manager
from django_orm.postgresql.fields.bytea import ByteaField

class ByteaModel(models.Model):
     data = ByteaField()
     objects = Manager()
