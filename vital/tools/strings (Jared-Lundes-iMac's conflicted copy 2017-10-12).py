# -*- coding: utf-8 -*-
"""

   `Vital String Tools`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde

"""
import re


camel_pattern = r"""([a-z])([A-Z])"""
camel_re = re.compile(camel_pattern)
def camel_to_underscore(string):
    """ Converts a CamelCased @string to camel_cased

        @string: #str object

        ..
            from vital.tools import camel_to_underscore

            camel_to_underscore("TedKoppel")
            # -> ted_koppel
        ..
    """
    return camel_re.sub(r"""\1_\2""", string).lower()


def underscore_to_camel(string):
    """ Converts an undescored_name @string to UnderscoredName

        @string: #str object

        ..
            from vital.tools import underscore_to_camel

            underscore_to_camel("ted_koppel")
            # -> TedKoppel
        ..
    """
    return "".join(s.capitalize() for s in string.split("_"))


non_alnum_re = re.compile(r"""([^A-Za-z0-9]+)""")
def to_alnum(string):
    """ Removes non-alphanumeric |[A-Za-z0-9]| characters from @string

        -> #str with only alphanumeric |[A-Za-z0-9]| characters

        ..
            import vital.tools
            print(vital.tools.to_alnum("2352@#%@#)gjgaoger"))
            # -> 2352gjgaoger
        ..
    """
    return non_alnum_re.sub("", string)


username_pattern = r"""([A-Za-z0-9_]+$)"""
username_re = re.compile(username_pattern)
def is_username(string, minlen=1, maxlen=15):
    """ Determines whether the @string pattern is username-like
        @string: #str being tested
        @minlen: minimum required username length
        @maxlen: maximum username length

        -> #bool
    """
    if string:
        string = string.strip()
        return username_re.match(string) and (minlen <= len(string) <= maxlen)
    return False


email_pattern = \
    r"""[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]{0,63}\.[a-zA-Z\-0-9]{0,24}$"""
email_re = re.compile(email_pattern)
def is_email(string):
    """ Determines whether the @string pattern is email-like
        @string: #str being tested

        -> #bool
    """
    return True if email_re.match(string) else False


#
## ``JSON bigint to string functions for Javascript``
#
_NUMBERS = (int, float)
def bigint_to_string(val):
    """ Converts @val to a string if it is a big integer (|>2**53-1|)

        @val: #int or #float

        -> #str if @val is a big integer, otherwise @val
    """
    if isinstance(val, _NUMBERS) and not abs(val) <= 2**53-1:
        return str(val)
    return val


#: Recursive bigint to string parser
def rbigint_to_string(obj):
    """ Recursively converts big integers (|>2**53-1|) to strings

        @obj: Any python object

        -> @obj, with any big integers converted to #str objects
    """
    if isinstance(obj, (str, bytes)) or not obj:
        # the input is the desired one, return as is
        return obj
    elif hasattr(obj, 'items'):
        # the input is a dict {}
        for k, item in obj.items():
            obj[k] = rbigint_to_string(item)
        return obj
    elif hasattr(obj, '__iter__'):
        # the input is iterable
        is_tuple = isinstance(obj, tuple)
        if is_tuple:
            obj = list(obj)
        for i, item in enumerate(obj):
            obj[i] = rbigint_to_string(item)
        return obj if not is_tuple else tuple(obj)
    return bigint_to_string(obj)


#: Regex bigint to string (should be applied to valid json string)
bigint_re = re.compile(r"""(\:\s*)(9[0-9]{15,}|[0-9]{17,})([\,\]\}]*)""")
string_bigint_re = \
    re.compile(r"""(\:\s*)(")(9[0-9]{15,}|[0-9]{17,})(")([\s\,\]\}]*)""")
bigint_sub = bigint_re.sub
string_bigint_sub = bigint_re.sub
def json_bigint_to_string(s):
    """ Converts big integer-like values in JSON objects to strings via
        regex pattern. Any integer >= 9000000000000000 will be  replaced
        with a string.

        @s: a JSON encoded string

        -> @s with big integers replaced by string_bigint_sub

        ..
            from vital.tools import json_big_int_to_string
            print(json_big_int_to_string("{k: 9000000000000000}"))
            # -> {k: "9000000000000000"}
        ..
    """
    return bigint_sub(r"""\1"\2"\3""", s)


def json_bigint_from_string(s):
    """ Converts big integer-like string values in JSON objects to integers
        via regex pattern. Any integer-like string >= 9000000000000000 will be
        replaced with an integer.

        @s: a JSON encoded string

        -> @s with big integers replaced by string_bigint_sub

        ..
            from vital.tools import json_big_int_from_string
            print(json_big_int_from_string('{k: "9000000000000000"}'))
            # -> {k: 9000000000000000}
        ..
    """
    return string_bigint_sub(r"""\1"\3"\4""", s)


#: Username/Hashtag are in group \2
mentions_pattern = r"""(?:^|[^@\w])@(\w{1,15})([\b\s]|$)"""
mentions_re = re.compile(mentions_pattern)
try:
    # Wide UCS-4 build
    hashtag_pattern = (
        u"([\w'&%\$" +
        u'\U0001F300-\U0001F64F' +
        u'\U0001F680-\U0001F6FF' +
        u'\u2600-\u26FF\u2700-\u27BF' +
        u']+)')
    hashtag_re_pattern = \
        u'(?:^|[^#\w\@]*)#' + hashtag_pattern + u'([\b\s]|$)?'
    hashtag_re = re.compile(hashtag_re_pattern, re.UNICODE | re.M)
except re.error:
    # Narrow UCS-2 build
    hashtag_pattern = (
        u"([\w'&%\$" +
        u'\U0001F300-\U0001F64F' +
        u'\U0001F680-\U0001F6FF' +
        u'\u2600-\u26FF\u2700-\u27BF' +
        u']+)')
    hashtag_re_pattern = \
        u'(?:^|[^#\w\@]*)#' + hashtag_pattern + u'([\b\s]|$)?'
    hashtag_re = re.compile(hashtag_re_pattern, re.UNICODE | re.M)


def get_hashtags(s):
    """ Gets all #hashtag-like matches in a string

        -> #list of lowercase hashtag #str objects
    """
    return [r[0].lower() for r in hashtag_re.findall(str(s))]


def get_mentions(s):
    """ Gets all @mentions-like matches in a string
        -> #list of lowercase mention #str objects
    """
    return [r[0].lower() for r in mentions_re.findall(str(s))]


def remove_blank_lines(string):
    """ Removes all blank lines in @string

        -> #str without blank lines
    """
    return "\n".join(line
                     for line in string.split("\n")
                     if len(line.strip()))


def to_plural(num, singular, plural):
    if num == 1:
        return '1 %s' % singular
    return '%s %s' % (num, plural)
