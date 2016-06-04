# -*- coding: utf-8 -*-
"""

  `Vital HTML Tools`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   The MIT License (MIT) (c) 2016 Jared Lunde

"""
import re
import uuid

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from vital.tools.strings import hashtag_re, mentions_re


__all__ = (
    "whitespace_re",
    "js_comments_re",
    "remove_whitespace",
    "hashtag_links",
    "mentions_links",
    "nl2p",
    "escape_json"
)


whitespace_re = re.compile(r"""\s+""").sub
js_comments_re = re.compile(
    r"""(?:\/\*(?:[\s\S]*?)\*\/)|(?:([\s])+\/\/(?:.*)$)""", re.M).sub
html_ignore_whitespace_re = re.compile(
    r"""<(script|textarea|code|pre)>(.*?(?!<\1>).+?)</\s*\1>""", re.DOTALL)


def remove_whitespace(s):
    """ Unsafely attempts to remove HTML whitespace. This is not an HTML parser
        which is why its considered 'unsafe', but it should work for most
        implementations. Just use on at your own risk.

        @s: #str

        -> HTML with whitespace removed, ignoring <pre>, script, textarea and code
            tags
    """
    ignores = {}
    for ignore in html_ignore_whitespace_re.finditer(s):
        name = "{}{}{}".format(r"{}", uuid.uuid4(), r"{}")
        ignores[name] = ignore.group()
        s = s.replace(ignore.group(), name)
    s = whitespace_re(r' ', s).strip()
    for name, val in ignores.items():
        s = s.replace(name, val)
    return s


def hashtag_links(uri, s):
    """ Turns hashtag-like strings into HTML links

        @uri: /uri/ root for the hashtag-like
        @s: the #str string you're looking for |#|hashtags in

        -> #str HTML link |<a href="/uri/hashtag">hashtag</a>|
    """
    for tag, after in hashtag_re.findall(s):
        _uri = '/' + (uri or "").lstrip("/") + quote(tag)
        link = '<a href="{}">#{}</a>{}'.format(_uri.lower(), tag, after)
        s = s.replace('#' + tag, link)
    return s


def mentions_links(uri, s):
    """ Turns mentions-like strings into HTML links,
        @uri: /uri/ root for the hashtag-like
        @s: the #str string you're looking for |@|mentions in

        -> #str HTML link |<a href="/uri/mention">mention</a>|
    """
    for username, after in mentions_re.findall(s):
        _uri = '/' + (uri or "").lstrip("/") + quote(username)
        link = '<a href="{}">@{}</a>{}'.format(_uri.lower(), username, after)
        s = s.replace('@' + username, link)
    return s


_p_re = re.compile(r'(?:\r\n|\r|\n){2,}')


def nl2p(string):
    return ''.join(('<p>%s</p>' % s.replace('\n', '<br>')
                   for s in _p_re.split(string)))


def escape_json(string):
    return string.replace('\\', '\\\\')\
                 .replace('"', '\\"')
