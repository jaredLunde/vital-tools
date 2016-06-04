# -*- coding: utf-8 -*-
"""

   `Vital local caching tools`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde

"""
import sys
from threading import local

from vital.cache.decorators import *

_all = [
  'local_lru',
  'typed_lru',
  'local_expiring_lru',
  'cached_property',
  'DictProperty',
  'memoize',
  'pickle_memoize',
  'sweet_pickle',
  'high_pickle'
  'local_property'
]

from vital.tools import systools

if systools.compat('3.4'):
    from vital.cache.async_decorators import async_lru
    _all.append(async_lru)


__all__ = _all


def local_property():
    """ Property structure which maps within the :func:local() thread
        (c)2014, Marcel Hellkamp
    """
    ls = local()

    def fget(self):
        try:
            return ls.var
        except AttributeError:
            raise RuntimeError("Request context not initialized.")

    def fset(self, value):
        ls.var = value

    def fdel(self):
        del ls.var

    return property(fget, fset, fdel, 'Thread-local property')
