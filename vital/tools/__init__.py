# -*- coding: utf-8 -*-
"""

   `Vital Tools for manipulating Python data structures`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde

"""
import importlib
from pydoc import locate, ErrorDuringImport

from vital.tools.dicts import *
from vital.tools.encoding import *
from vital.tools.html import *
from vital.tools.http import *
from vital.tools.lists import *
from vital.tools.strings import *


def getattr_in(obj, name):
    """ Finds an in @obj via a period-delimited string @name.
        @obj: (#object)
        @name: (#str) |.|-separated keys to search @obj in
        ..
            obj.deep.attr = 'deep value'
            getattr_in(obj, 'obj.deep.attr')
        ..
        |'deep value'|
    """
    for part in name.split('.'):
        obj = getattr(obj, part)
    return obj


def import_from(name):
    """ Imports a module, class or method from string and unwraps it
        if wrapped by functools

        @name: (#str) name of the python object

        -> imported object
    """
    obj = name
    if isinstance(name, str) and len(name):
        try:
            obj = locate(name)
            assert obj is not None
        except (AttributeError, TypeError, AssertionError, ErrorDuringImport):
            try:
                name = name.split(".")
                attr = name[-1]
                name = ".".join(name[:-1])
                mod = importlib.import_module(name)
                obj = getattr(mod, attr)
            except (SyntaxError, AttributeError, ImportError, ValueError):
                try:
                    name = name.split(".")
                    attr_sup = name[-1]
                    name = ".".join(name[:-1])
                    mod = importlib.import_module(name)
                    obj = getattr(getattr(mod, attr_sup), attr)
                except:
                    # We give up.
                    pass

    obj = unwrap_obj(obj)
    return obj


def unwrap_obj(obj):
    """ Gets the actual object from a decorated or wrapped function
        @obj: (#object) the object to unwrap
    """
    try:
        obj = obj.fget
    except (AttributeError, TypeError):
        pass
    try:
        # Cached properties
        if obj.func.__doc__ == obj.__doc__:
            obj = obj.func
    except AttributeError:
        pass
    try:
        # Setter/Getters
        obj = obj.getter
    except AttributeError:
        pass
    try:
        # Wrapped Funcs
        obj = inspect.unwrap(obj)
    except:
        pass
    return obj
