import collections
from functools import wraps

__all__ = ('async_lru',)


def async_lru(size=100):
    """ An LRU cache for asyncio coroutines in Python 3.5
        ..
            @async_lru(1024)
            async def slow_coroutine(*args, **kwargs):
                return await some_other_slow_coroutine()
        ..
    """
    cache = collections.OrderedDict()

    def decorator(fn):
        @wraps(fn)
        @asyncio.coroutine
        def memoizer(*args, **kwargs):
            key = str((args, kwargs))
            try:
                result = cache.pop(key)
                cache[key] = result
            except KeyError:
                if len(cache) >= size:
                    cache.popitem(last=False)
                result = cache[key] = yield from fn(*args, **kwargs)
            return result
        return memoizer
    return decorator
