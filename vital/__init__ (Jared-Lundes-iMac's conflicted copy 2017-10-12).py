# -*- coding: utf-8 -*-
"""

   `Vital`
    Essential tools for building Python 3 applications.
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde
    http://github.com/jaredlunde/vital-tools

"""
from vital import cache
from vital import security
from vital import tools
if tools.systools.compat('3.3'):
    from vital import debug


__author__ = "Jared Lunde"
__license__ = "MIT"
__version__ = "0.1.7"
