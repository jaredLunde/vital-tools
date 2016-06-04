# -*- coding: utf-8 -*-
"""

   `Vital List Tools`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde

"""
from random import SystemRandom as rng

try:
    from collections import UserList
except ImportError:
    UserList = list


def unique_list(seq):
    """ Removes duplicate elements from given @seq

        @seq: a #list or sequence-like object

        -> #list
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def pairwise(seq):
    """ @seq: (#iterable)

        -> yields pairs
        ..
            for pair in pairwise([0, 1, 2, 3, 4, 5]):
                print(pair)
            # (0, 1)
            # (2, 3)
            # (4, 5)
        ..
    """
    return grouped(seq, 2)


def grouped(seq, size):
    """ @seq: (#iterable)

        -> yields groups
        ..
            lst = [0, 1, 2, 3, 4, 5]
            for group in grouped(lst, 3):
                print(group)
            # (0, 1, 2)
            # (3, 4, 5)
        ..
    """
    return zip(*[iter(seq)] * size)


def flatten(*seqs):
    """ Flattens a sequence e.g. |[(1, 2), (3, (4, 5))] -> [1, 2, 3, 4, 5]|

        @seq: #tuple, #list or :class:UserList

        -> yields an iterator

        ..
            l = [(1, 2), (3, 4)]
            for x in flatten(l):
                print(x)
        ..
    """
    for seq in seqs:
        for item in seq:
            if isinstance(item, (tuple, list, UserList)):
                for subitem in flatten(item):
                    yield subitem
            else:
                yield item


def remove_empty(seq):
    """ Removes #None types from sequences

        @seq: a #list or sequence-like object

        -> #list
    """
    return [x for x in seq if x is not None]


def randrange(seq):
    """ Yields random values from @seq until @seq is empty """
    seq = seq.copy()
    choose = rng().choice
    remove = seq.remove
    for x in range(len(seq)):
        y = choose(seq)
        remove(y)
        yield y
