# -*- coding: utf-8 -*-

from django.db.models.sql.constants import QUERY_TERMS

"""
Posible aggregate list:
- area(object)          -> double
- center(object)        -> point
- diameter(circle)      -> double
- height(box)           -> double
- isclosed(path)        -> bool
- isopen(path)          -> bool
- length(object)        -> double
- npoints(path, polygon)-> int
- radius(circle)        -> double
- width(box)            -> double

A lot of agregates are used for querys.

"""

geometric_lookups = (
    # with 2 arguments
    'distance', #  field <-> field = X

    #with one argument
    'numpoints', # # "field" = X
    'numpoints_gt',
    'numpoints_gte',
    'numpoints_lt',
    'numpoints_lte',

    'center',   # center("field") = X
    'is_closed',            # isclosed(path)
    'is_open',              # isopen(path)
    'length'                # length(object)
    'length_gt',
    'length_lt',
    'length_gte',
    'length_lte',
    'width',                # width(box)
    'width_gt',
    'width_lt',
    'width_gte',
    'width_lte',
    'radius',               # radius(circle)
    'radius_gt',
    'radius_lt',
    'radius_gte',
    'radius_lte',
    'npoints',              # npoints(path, polygon)
    'npoints_gt',
    'npoints_lt',
    'npoints_gte',
    'npoints_lte',
    'diameter',             # diameter(circle)
    'diameter_gt',
    'diameter_lt',
    'diameter_gte',
    'diameter_lte',
    'area',                 # area(object)
    'area_gt',
    'area_lt',
    'area_gte',
    'area_lte',
    'overlap',
    'strictly_left_of',
    'strictly_right_of',
    'notextendto_right_of',
    'notextendto_left_of',
    'strictly_below',
    'strictly_above',
    'notextend_above',
    'notextend_below',
    'is_below',
    'is_above',
    'intersects',
    'is_horizontal',
    'is_perpendicular',
    'is_parallel',
    'contained_in_or_on',
    'same_as',
    'contains',
    'center',
)

GEOMETRIC_LOOKUPS = dict((x, None) for x in geometric_lookups)
FTS_LOCKUPS = {'query': None, 'query_raw':None}
VARCHAR_LOOKUPS = dict((x, None) for x in ('unaccent', 'iunaccent'))
INTERVAL_LOOKUPS = dict((x, None) for x in  ('distinct', 'exact', 'gt','lt','gte', 'lte'))
ARRAY_LOOKUPS = dict((x, None) for x in ('indexexact', 'distinct', 'slice', 'contains', 
                                'containedby', 'overlap', 'exact', 'gt','lt','gte', 'lte'))

QUERY_TERMS.update(GEOMETRIC_LOOKUPS)
QUERY_TERMS.update(FTS_LOCKUPS)
QUERY_TERMS.update(VARCHAR_LOOKUPS)
QUERY_TERMS.update(INTERVAL_LOOKUPS)
QUERY_TERMS.update(ARRAY_LOOKUPS)

GEOMETRIC_TYPES = dict((x, None) for x in \
    ('box', 'point', 'line', 'lseg', 'path', 'polygon', 'circle'))
