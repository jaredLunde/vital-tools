# -*- coding: utf-8 -*-
"""

   `Vital Security` helpful functions for securing data
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
    The MIT License (MIT) (c) 2016 Jared Lunde

"""
import os
import random
import string
from math import ceil
from cmath import log, exp

import hmac
from Crypto.Cipher import AES
from hashlib import sha256

from base64 import b64encode, b64decode
try:
    import ujson as json
except ImportError:
    import json

from vital.tools.encoding import uniorbytes


#
#  ``General cryptography``
#
def aes_b64_encrypt(value, secret, block_size=AES.block_size):
    """ AES encrypt @value with @secret using the |CFB| mode of AES
        with a cryptographically secure initialization vector.

        -> (#str) AES encrypted @value

        ..
            from vital.security import aes_encrypt, aes_decrypt
            aes_encrypt("Hello, world",
                        "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw='
            aes_decrypt(
                "zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw=",
                "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'Hello, world'
        ..
    """
    iv = randstr(block_size * 2, rng=random)
    cipher = AES.new(secret[:32], AES.MODE_CFB, iv[:block_size].encode())
    return iv + b64encode(cipher.encrypt(
        uniorbytes(value, bytes))).decode('utf-8')


def aes_b64_decrypt(value, secret, block_size=AES.block_size):
    """ AES decrypt @value with @secret using the |CFB| mode of AES
        with a cryptographically secure initialization vector.

        -> (#str) AES decrypted @value

        ..
            from vital.security import aes_encrypt, aes_decrypt
            aes_encrypt("Hello, world",
                        "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw='
            aes_decrypt(
                "zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw=",
                "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'Hello, world'
        ..
    """
    if value is not None:
        iv = value[:block_size]
        cipher = AES.new(secret[:32], AES.MODE_CFB, iv)
        return cipher.decrypt(b64decode(
            uniorbytes(value[block_size * 2:], bytes))).decode('utf-8')


def aes_encrypt(value, secret, block_size=AES.block_size):
    """ AES encrypt @value with @secret using the |CFB| mode of AES
        with a cryptographically secure initialization vector.

        -> (#bytes) AES encrypted @value

        ..
            from vital.security import aes_encrypt, aes_decrypt
            aes_encrypt("Hello, world",
                        "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw='
            aes_decrypt(
                "zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw=",
                "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'Hello, world'
        ..f
    """
    iv = os.urandom(block_size * 2)
    cipher = AES.new(secret[:32], AES.MODE_CFB, iv[:block_size])
    return b'%s%s' % (iv, cipher.encrypt(value))


def aes_decrypt(value, secret, block_size=AES.block_size):
    """ AES decrypt @value with @secret using the |CFB| mode of AES
        with a cryptographically secure initialization vector.

        -> (#str) AES decrypted @value

        ..
            from vital.security import aes_encrypt, aes_decrypt
            aes_encrypt("Hello, world",
                        "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw='
            aes_decrypt(
                "zYgVYMbeOuiHR50aMFinY9JsfyMQCvpzI+LNqNcmZhw=",
                "aLWEFlwgwlreWELFNWEFWLEgwklgbweLKWEBGW")
            # -> 'Hello, world'
        ..
    """
    if value is not None:
        cipher = AES.new(secret[:32], AES.MODE_CFB, value[:block_size])
        return cipher.decrypt(uniorbytes(value[block_size * 2:], bytes))


def aes_pad(s, block_size=32, padding='{'):
    """ Adds padding to get the correct block sizes for AES encryption

        @s: #str being AES encrypted or decrypted
        @block_size: the AES block size
        @padding: character to pad with

        -> padded #str

        ..
            from vital.security import aes_pad
            aes_pad("swing")
            # -> 'swing{{{{{{{{{{{{{{{{{{{{{{{{{{{'
        ..
    """
    return s + (block_size - len(s) % block_size) * padding


def aes_unpad(s, block_size=32, padding='{'):
    """ Removes padding to get the value from @s for AES decryption

        @s: #str being AES encrypted or decrypted
        @block_size: the AES block size
        @padding: character to pad with

        -> unpadded #str

        ..
            from vital.security import aes_pad
            aes_unpad("swing{{{{{{{{{{{{{{{{{{{{{{{{{{{")
            # -> 'swing'
        ..
    """
    return s.rstrip(padding)


def lscmp(a, b):
    """ Compares two strings in a cryptographically safe way:
        Runtime is not affected by length of common prefix, so this
        is helpful against timing attacks.

        ..
            from vital.security import lscmp
            lscmp("ringo", "starr")
            # -> False
            lscmp("ringo", "ringo")
            # -> True
        ..
    """
    l = len
    return not sum(0 if x == y else 1 for x, y in zip(a, b)) and l(a) == l(b)


#
#  ``Cookies``
#
def cookie(data, key_salt='', secret=None, digestmod=None):
    """ Encodes or decodes a signed cookie.
        @data: cookie data
        @key_salt: HMAC key signing salt
        @secret: HMAC signing secret key
        @digestmod: hashing algorithm to sign with, recommended >=sha256

        -> HMAC signed or unsigned cookie data

        ..
            from vital.security import cookie

            cookie("Hello, world.", "saltyDog", secret="alBVlwe")
            # -> '!YuOoKwDp8GhrwwojdjTxSCj1c2Z+7yz7r6cC7E3hBWo=?IkhlbGxvLCB3b3JsZC4i'
            cookie(
                "!YuOoKwDp8GhrwwojdjTxSCj1c2Z+7yz7r6cC7E3hBWo=?IkhlbGxvLCB3b3JsZC4i",
                "saltyDog", secret="alBVlwe")
            # -> 'Hello, world.'
        ..
    """
    digestmod = digestmod or sha256
    if not data:
        return None
    try:
        # Decode signed cookie
        assert cookie_is_encoded(data)
        datab = uniorbytes(data, bytes)
        sig, msg = datab.split(uniorbytes('?', bytes), 1)
        key = ("{}{}").format(secret, key_salt)
        sig_check = hmac.new(
            key=uniorbytes(key, bytes), msg=msg, digestmod=digestmod).digest()
        sig_check = uniorbytes(b64encode(sig_check), bytes)
        if lscmp(sig[1:], sig_check):
            return json.loads(uniorbytes(b64decode(msg)))
        return None
    except:
        # Encode and sign a json-able object. Return a string.
        key = ("{}{}").format(secret, key_salt)
        msg = b64encode(uniorbytes(json.dumps(data), bytes))
        sig = hmac.new(
            key=uniorbytes(key, bytes), msg=msg,
            digestmod=digestmod).digest()
        sig = uniorbytes(b64encode(sig), bytes)
        return uniorbytes('!'.encode() + sig + '?'.encode() + msg)


def cookie_is_encoded(data):
    """ Tests whether or not a cookie is encoded / HMAC signed

        -> #bool True if encoded

        ..
            from vital.security import cookie_is_encoded

            cookie_is_encoded(
                "!YuOoKwDp8GhrwwojdjTxSCj1c2Z+7yz7r6cC7E3hBWo=?IkhlbGxvLCB3b3JsZC4i")
            # -> True
        ..
    """
    return data.startswith('!') and '?' in data


def strkey(val, chaffify=1, keyspace=string.ascii_letters+string.digits):
    """ Converts integers to a sequence of strings, and reverse.
        This is not intended to obfuscate numbers in any kind of
        cryptographically secure way, in fact it's the opposite. It's
        for predictable, reversable, obfuscation. It can also be used to
        transform a random bit integer to a string of the same bit
        length.

        @val: #int or #str
        @chaffify: #int multiple to avoid 1=b, 2=c, ... obfuscates the ordering
        @keyspace: #str allowed output chars

        -> #str if @val is #int, #int if @val is #str

        ..
            from vital.security import strkey

            strkey(0, chaffify=1)
            # -> b
            strkey(0, chaffify=4)
            # -> e
            strkey(90000000000050500502200302035023)
            # -> 'f3yMpJQUazIZHp1UO7k'
            strkey('f3yMpJQUazIZHp1UO7k')
            # -> 90000000000050500502200302035023
            strkey(2000000, chaffify=200000000000)
            # -> 'DIaqtyo2sC'
        ..
    """
    chaffify = chaffify or 1
    keylen = len(keyspace)
    try:
        # INT TO STRING
        # must be a positive integer
        if val < 2:
            raise ValueError("Input value must be greater than 1.")
        # chaffify the value
        val = val * chaffify
        # output the new string value
        out = []
        out_add = out.append
        while val > 0:
            val, digit = divmod(val, keylen)
            out_add(keyspace[digit])
        return "".join(out)[::-1]
    except TypeError:
        # STRING TO INT
        out = 0
        val = str(val)
        find = str.find
        for c in val:
            out = out * keylen + find(keyspace, c)
        # dechaffify the value
        out = out // chaffify
        return int(out)


#
# ``Random token generation``
#
def randhex(size=32, rng=None):
    """ Gets a random hex string of @size in terms of number of characters.
        This is an extremely fast way to generate a random string.

        @size: (#int) approximate size of the hex to generate in number
            of characters
        @rng: the random number generator to use, :class:random.SystemRandom
            is used by default.
    """
    return "%0x" % (rng or random.SystemRandom()).getrandbits(size * 4)


def calc_chars_in(bits, keyspace):
    if bits > 512:
        raise ValueError('Bits must be <= 512')
    bits = bits * log(2)
    return log(exp(bits))/log(keyspace)


def chars_in(bits, keyspace):
    """ ..
        log2(keyspace^x_chars) = bits
        log(keyspace^x_chars) = log(2) * bits
        exp(log(keyspace^x_chars)) = exp(log(2) * bits)
        x_chars = log(exp(log(2) * bits)) / log(keyspace)
        ..
        -> (#int) number of characters in @bits of entropy given the @keyspace
    """
    keyspace = len(keyspace)
    if keyspace < 2:
        raise ValueError("Keyspace size must be >1")
    bits_per_cycle = 512
    if bits > bits_per_cycle:
        chars = 0
        bits_processed = 0
        cycles = ceil(bits / bits_per_cycle)
        for _ in range(int(cycles)):
            if bits_processed + bits_per_cycle > bits:
                bits_per_cycle = bits - bits_processed
            chars += calc_chars_in(bits_per_cycle, keyspace)
            bits_processed += bits_per_cycle
    else:
        chars = calc_chars_in(bits, keyspace)
    return abs(chars)


def calc_bits_in(length, keyspace):
    if length > 64:
        raise ValueError('Length must be <= 64')
    return log(keyspace**length, 2)


def bits_in(length, keyspace):
    """ |log2(keyspace^length) = bits|
        -> (#float) number of bits of entropy in @length of characters for
            a given a @keyspace
    """
    keyspace = len(keyspace)
    length_per_cycle = 64
    if length > length_per_cycle:
        bits = 0
        length_processed = 0
        cycles = ceil(length / length_per_cycle)
        for _ in range(int(cycles)):
            if length_processed + length_per_cycle > length:
                length_per_cycle = length - length_processed
            bits += calc_bits_in(length_per_cycle, keyspace)
            length_processed += length_per_cycle
    else:
        bits = calc_bits_in(length, keyspace)
    return float(abs(bits))


def iter_random_chars(bits,
                      keyspace=string.ascii_letters + string.digits + '#/.',
                      rng=None):
    """ Yields a cryptographically secure random key of desired @bits of
        entropy within @keyspace using :class:random.SystemRandom

        @bits: (#int) minimum bits of entropy
        @keyspace: (#str) or iterable allowed output chars

        ..
            from vital.security import iter_rand

            for char in iter_rand(512):
                do_something_with(char)
    """
    if bits < 8:
        raise ValueError('Bits cannot be >8')
    else:
        chars = chars_in(bits, keyspace)
    rng = rng or random.SystemRandom()
    for char in range(int(ceil(chars))):
        yield rng.choice(keyspace)


def randkey(bits, keyspace=string.ascii_letters + string.digits + '#/.',
            rng=None):
    """ Returns a cryptographically secure random key of desired @bits of
        entropy within @keyspace using :class:random.SystemRandom

        @bits: (#int) minimum bits of entropy
        @keyspace: (#str) or iterable allowed output chars
        @rng: the random number generator to use. Defaults to
            :class:random.SystemRandom. Must have a |choice| method

        -> (#str) random key

        ..
            from vital.security import randkey

            randkey(24)
            # -> '9qaX'
            randkey(48)
            # -> 'iPJ5YWs9'
            randkey(64)
            # - > 'C..VJ.KLdxg'
            randkey(64, keyspace="abc", rng=random)
            # -> 'aabcccbabcaacaccccabcaabbabcacabacbbbaaab'
        ..
    """
    return "".join(char for char in iter_random_chars(bits, keyspace, rng))


def randstr(size, keyspace=string.ascii_letters + string.digits, rng=None):
    """ Returns a cryptographically secure random string of desired @size
        (in character length) within @keyspace using :class:random.SystemRandom

        @size: (#int) number of random characters to generate
        @keyspace: (#str) or iterable allowed output chars
        @rng: the random number generator to use. Defaults to
            :class:random.SystemRandom. Must have a |choice| method

        -> #str random key

        ..
            from vital.security import randkey

            randstr(4)
            # -> '9qaX'
        ..
    """
    rng = rng or random.SystemRandom()
    return "".join(rng.choice(keyspace) for char in range(int(ceil(size))))
