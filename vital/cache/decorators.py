# -*- coding: utf-8 -*-
"""

   `Vital local cache decorators`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde

"""
try:
    import asyncio
except ImportError:
    pass
import time
import collections
import datetime
import pickle

from functools import wraps, partial, update_wrapper

try:
    from functools import lru_cache
except ImportError:
    pass


__all__ = (
  'local_lru',
  'typed_lru',
  'local_expiring_lru',
  'cached_property',
  'DictProperty',
  'memoize',
  'pickle_memoize',
  'sweet_pickle',
  'high_pickle'
)


#
#  ``Python Caching Decorators``
#
def local_lru(obj):
    """ Property that maps to a key in a local dict-like attribute.
        self._cache must be an OrderedDict
        self._cache_size must be defined as LRU size
        ..
        class Foo(object):

            def __init__(self, cache_size=5000):
                self._cache = OrderedDict()
                self._cache_size = cache_size

            @local_lru
            def expensive_meth(self, arg):
                pass
        ..
    """
    @wraps(obj)
    def memoizer(*args, **kwargs):
        instance = args[0]
        lru_size = instance._cache_size
        if lru_size:
            cache = instance._cache
            key = str((args, kwargs))
            try:
                r = cache.pop(key)
                cache[key] = r
            except KeyError:
                if len(cache) >= lru_size:
                    cache.popitem(last=False)
                r = cache[key] = obj(*args, **kwargs)
            return r
        return obj(*args, **kwargs)
    return memoizer


def typed_lru(maxsize, types=None):
    """ :func:functools.lru_cache wrapper which allows you to prevent object
        types outside of @types from being cached.

        The main use case for this is preventing unhashable type errors when
        you still want to cache some results.
        ..
            from vital.cache import typed_lru

            @typed_lru(300, (str, int))
            def some_expensive_func():
                pass

            @typed_lru(300, str)
            def some_expensive_func2():
                pass

            @typed_lru(300, collections.Hashable)
            def some_expensive_func3():
                pass
        ..
    """
    types = types or collections.Hashable

    def lru(obj):
        @lru_cache(maxsize)
        def _lru_cache(*args, **kwargs):
            return obj(*args, **kwargs)

        @wraps(obj)
        def _convenience(*args, **kwargs):
            broken = False
            for arg in args:
                if not isinstance(arg, types):
                    broken = True
                    break
            for arg, val in kwargs.items():
                if not isinstance(arg, types) and isinstance(val, types):
                    broken = True
                    break
            if not broken:
                try:
                    return _lru_cache(*args, **kwargs)
                except TypeError:
                    return obj(*args, **kwargs)
            return obj(*args, **kwargs)
        return _convenience
    return lru


def local_expiring_lru(obj):
    """ Property that maps to a key in a local dict-like attribute.
        self._cache must be an OrderedDict
        self._cache_size must be defined as LRU size
        self._cache_ttl is the expiration time in seconds
        ..
        class Foo(object):

            def __init__(self, cache_size=5000, cache_ttl=600):
                self._cache = OrderedDict()
                self._cache_size = cache_size
                self._cache_ttl = cache_ttl

            @local_expiring_lru
            def expensive_meth(self, arg):
                pass
        ..
    """
    @wraps(obj)
    def memoizer(*args, **kwargs):
        instance = args[0]
        lru_size = instance._cache_size
        cache_ttl = instance._cache_ttl
        if lru_size and cache_ttl:
            cache = instance._cache
            kargs = list(args)
            kargs[0] = id(instance)
            key = str((kargs, kwargs))
            try:
                r = list(cache.pop(key))
                if r[1] < datetime.datetime.utcnow():
                    r[0] = None
                else:
                    cache[key] = r
            except (KeyError, AssertionError):
                if len(cache) >= lru_size:
                    cache.popitem(last=False)
                r = cache[key] = (
                    obj(*args, **kwargs),
                    datetime.datetime.utcnow() + datetime.timedelta(
                        seconds=cache_ttl)
                )
            if r[0]:
                return r[0]
        return obj(*args, **kwargs)
    return memoizer


class DictProperty(object):
    """ Property that maps to a key in a local dict-like attribute.
        ..
        class Foo(object):

            def __init__(self):
                self._cache = threading.local()

            @DictProperty('_cache', 'key_name', read_only=True)
            def expensive_func(self):
                pass
        ..
        Copyright (c) 2014, Marcel Hellkamp
    """

    def __init__(self, attr, key=None, read_only=False):
        """ @attr: the local attribute name
            @key: the keyname to store in @attr
            @read_only: prevents setting this value if True
        """
        self.attr, self.key, self.read_only = attr, key, read_only
        self.getter = None

    def __call__(self, func):
        update_wrapper(self, func, updated=[])
        self.getter, self.key = func, self.key or func.__name__
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self
        key, storage = self.key, getattr(obj, self.attr)
        if key not in storage:
            storage[key] = self.getter(obj)
        return storage[key]

    def __set__(self, obj, value):
        if self.read_only:
            raise AttributeError("Read-Only property.")
        getattr(obj, self.attr)[self.key] = value

    def __delete__(self, obj):
        if self.read_only:
            raise AttributeError("Read-Only property.")
        del getattr(obj, self.attr)[self.key]


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.
        ..
        class Foo(object):

            @cached_property
            def expensive_func(self, arg):
                pass
        ..
        Copyright (c) 2014, Marcel Hellkamp
    """
    def __init__(self, func):
        """ @func: the wrapped method """
        self.__doc__ = func.__getattribute__('__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.func.__name__] = self.func(obj)
        return obj.__dict__[self.func.__name__]


class memoize(object):
    """ Memory-efficient memoization using __slots__.
        The cache key is the #str representation of the #tuple (args, kwargs)
        the cached function receives. Because of this, it is not recommend that
        you cache functions with object arguments without unique __repr__()'s.
        If you need argument-safe memoization, use :class:pickle_memoize
        which pickles the key.
        ..
        class Foo(object):

            @memoize
            def expensive_func(self, arg):
                pass
        ..
    """
    __slots__ = ('obj',)
    data = {}

    def __init__(self, obj):
        self.obj = obj

    def _key(self, args, kwargs):
        return str((args, kwargs))

    def __repr__(self):
        return self.obj.__repr__()

    def __call__(self, *args, **kwargs):
        cache = self.data
        key = self._key(args, kwargs)
        try:
            return dict.__getitem__(cache, key)
        except KeyError:
            dict.__setitem__(cache, key, self.obj(*args, **kwargs))
            return dict.__getitem__(cache, key)

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return partial(self.__call__, obj)


class pickle_memoize(memoize):
    """ The same as :class:memoize, but pickles the argument key.
        ..
        class Foo:
            @pickle_memoize
            def expensive_func(self, arg):
                ....
        ..
    """
    __slots__ = ('obj',)

    def _key(self, args, kwargs):
        return high_pickle.dumps((args, kwargs))


#
#  ``Serialization``
#
class _pickle:
    """ Pickle serializers with varying protocols
        :var:high_pickle returns pickler with highest protocol
        :var:sweet_pickle returns pickler with protocol 3
    """
    protocol = pickle.HIGHEST_PROTOCOL

    def __init__(self, protocol=pickle.HIGHEST_PROTOCOL):
        """ @protocol: #int pickle protocol, highest protocol by default """
        self.protocol = protocol

    def dumps(self, data):
        return pickle.dumps(data, self.protocol)

    def loads(self, data):
        return pickle.loads(data, encoding="utf-8")

    def dump(self, data):
        return pickle.dump(data, self.protocol)

    def load(self, data):
        return pickle.load(dataa, encoding="utf-8")


sweet_pickle = _pickle(3)
high_pickle = _pickle()
