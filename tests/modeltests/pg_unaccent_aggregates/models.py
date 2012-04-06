
from django.db import models
from django_orm.postgresql.manager import Manager

class Person(models.Model):
    name = models.CharField(max_length=32)

    objects = models.Manager()
    manager = Manager()

    def __unicode__(self):
        return self.name
