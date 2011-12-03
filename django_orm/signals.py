# -*- coding: utf-8 -*-

import django.dispatch

register_backend = django.dispatch.Signal(providing_args=["connection"])
