# -*- coding: utf-8 -*-
"""

   `Vital Dict Tools`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde

"""
from itertools import chain
from collections import OrderedDict


__all__ = (
    "merge_dict",
    "revrank_dict",
    "rank_dict",
    "getitem_in")


def merge_dict(*dicts):
    """ Merges given @*dicts into one #dict and returns a new dict
        without changing the state of the inputs.

        @*dicts: one or several #dict objects

        -> new merged #dict
    """
    return dict(chain(*list(d.items() for d in dicts)))


def revrank_dict(dict, key=lambda t: t[1], as_tuple=False):
    """ Reverse sorts a #dict by a given key, optionally returning it as a
        #tuple. By default, the @dict is sorted by it's value.

        @dict: the #dict you wish to sorts
        @key: the #sorted key to use
        @as_tuple: returns result as a #tuple ((k, v),...)

        -> :class:OrderedDict or #tuple
    """
    sorted_list = sorted(dict.items(), key=key, reverse=True)
    return OrderedDict(sorted_list) if not as_tuple else tuple(sorted_list)


def rank_dict(dict, key=lambda t: t[1], as_tuple=False):
    """ Sorts a #dict by a given key, optionally returning it as a
        #tuple. By default, the @dict is sorted by it's value.

        @dict: the #dict you wish to sorts
        @key: the #sorted key to use
        @as_tuple: returns result as a #tuple ((k, v),...)

        -> :class:OrderedDict or #tuple
    """
    sorted_list = sorted(dict.items(), key=key)
    return OrderedDict(sorted_list) if not as_tuple else tuple(sorted_list)


def getitem_in(obj, name):
    """ Finds a key in @obj via a period-delimited string @name.
        @obj: (#dict)
        @name: (#str) |.|-separated keys to search @obj in
        ..
            obj = {'foo': {'bar': {'baz': True}}}
            getitem_in(obj, 'foo.bar.baz')
        ..
        |True|
    """
    for part in name.split('.'):
        obj = obj[part]
    return obj
