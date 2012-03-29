# -*- coding: utf-8 -*-

from django.db import models

class Item(models.Model):

    name = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return self.name
