"""

   `Vital local caching tools`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) © 2016 Jared Lunde

"""
from threading import local
from vital.cache.decorators import *


__all__ = (
  'local_lru',
  'async_lru',
  'typed_lru',
  'local_expiring_lru',
  'cached_property',
  'DictProperty',
  'memoize',
  'pickle_memoize',
  'sweet_pickle',
  'high_pickle'
  'local_property'
)


def local_property():
    """ Property structure which maps within the :func:local() thread
        ©2014, Marcel Hellkamp
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
