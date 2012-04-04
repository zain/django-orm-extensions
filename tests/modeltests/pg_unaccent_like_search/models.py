# -*- coding: utf-8 -*-

from django.db import models

class 


class TestModel(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField()
