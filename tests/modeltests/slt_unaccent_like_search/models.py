# -*- coding: utf-8 -*-

from django.db import models
from django_orm.sqlite3.manager import Manager


class TestModel(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField()
    
    objects = models.Manager()
    manager = Manager()


class FooModel(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField()
    
    objects = models.Manager()
    manager = Manager()


class Foo2Model(models.Model):
    parent = models.ForeignKey("FooModel", related_name="foo2")


    objects = models.Manager()
    manager = Manager()
