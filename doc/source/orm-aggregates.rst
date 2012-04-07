==========
Aggregates
==========

Annotations and Aggregates in django only work with numeric types, ie int and float. 
This means that if you want to do something more out of the ordinary, we're pretty tied 
to the implementation of django.

Django-Orm implements its own system of Aggregates and annotations. Much simpler and 
lighter. Lets deal with all types that the database supports.

**NOTE**: All examples are for postgresql, but this feature is available for mysql and sqlite3 as well.

Unaccent aggregate/annotation
-----------------------------

The best way to see how it works, is an example. Unaccent is a good candidate.
Unaccent is an aggregation function that admits any field of type "CharField" or "TextField" and 
leaves without accents.

Usage example:

.. code-block:: python

    from niwi.models import Post
    from django_orm.postgresql.aggregates import Unaccent
    # sqlite: from django_orm.sqlite3.aggregates import Unaccent
    # mysql: from django_orm.mysql.aggregates import Unaccent

    qs = Post.objects.inline_annotate(title_unaccent=Unaccent('title')).filter(pk=15)
    print qs[0].title
    # prints: Tipado estático en python.
    print qs[0].title_unaccent
    # prints: Tipado estatico en python.

Note for postgresql9.0 users:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use this feature, you must install the extension unaccented. 

Example::
    
    psql -U user dbname -f /usr/share/postgresql/contrib/unaccent.sql


Note for postgresql9.1 users:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use this feature, you must install the extension unaccented.

Example::
    
    psql -U user dbname -c "CREATE EXTENSION unaccent;" -q
