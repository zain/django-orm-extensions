Django Orm
==========

Advanced improvement to django orm with third-party modules in one with some usefull features.

For more information, see project page and documentation:

* **Project page:** http://www.niwi.be/post/project-django-orm/
* **Docs:** http://readthedocs.org/docs/django-orm/en/latest/

Global features:
----------------

* Additional indexes creation method from model. (PostgreSQL, MySQL, Sqlite3)
* ORM low level cache for all backends. (beta)
* Unaccent lookup for searches without accents.

Only PostgreSQL features:
-------------------------

* PostgreSQL Full Text Search.
* PostgreSQL complex types and full queryset lookups.
* PostgreSQL server side cursors.
* PostgreSQL hstore integration.
* PostgreSQL unaccent aggregation.

Requirements:
-------------

* PostgreSQL 9.x
* Psycopg2 
* MySQLdb 
* Django 
* Sqlite3
