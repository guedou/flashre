# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
Functions used by several flashre modules
"""


import os
import cPickle as pickle

import r2pipe


def cache(filename):
    """
    A simple decorator to cache results to disk.
    """

    def decorator(func):
        """Note: it is the function that is finally returned"""
        def cached_function(*args):
            """Note: needed to access the returned value"""
            try:
                return pickle.load(open(filename, "r"))
            except IOError:
                value = func(*args)
                pickle.dump(value, open(filename, "w"))
                return value
        return cached_function

    return decorator


def get_r2pipe(filename, offset, options=None):
    """
    Get a r2pipe handle ready to analyse a flashair binary.
    """

    # Set the miasm architecture
    os.putenv("R2M2_ARCH", "mepl")

    # Use the r2m2 architecture
    default_options = ["-a", "r2m2"]

    # Map the binary at a given location
    default_options += ["-m", hex(offset)]

    # Decrease r2 verbority
    default_options += ["-e", "bin.verbose=false"]

    # Add user specified options
    if isinstance(options, list):
        default_options += options

    return r2pipe.open(filename, default_options)


@cache("get_strings.cache")
def get_strings(r2p):
    """
    Return all strings in the binary and their offsets.
    """

    ret = r2p.cmdj("izzj")["strings"]
    return [(s["paddr"], s["string"].decode("base64")) for s in ret]


def r2_search_memory(r2p, pattern):
    """
    Search for a pattern in the binary and return matched offsets.
    """

    return [p["offset"] for p in r2p.cmdj("/xj %s" % pattern)]


@cache("get_prologues.cache")
def get_prologues(r2p):
    """
    Look for well-known MeP prologues in a binary using r2pipe.
    """

    # Type #1 example:
    #   c06f           ADD SP, -16
    #   1a70           LDC R0, LP
    ret = [p["offset"] for p in r2p.cmdj("/xj ..6f1a70")]

    # Type #2 example:
    #   f0cfdcff       ADD3 SP, SP, -36
    #   1a70           LDC R0, LP
    ret += [p["offset"] for p in r2p.cmdj("/xj f0cf....1a70")]

    # Type #3 example:
    #   1a70           LDC R0, LP
    #   f06f           ADD SP, -4
    ret += [p["offset"] for p in r2p.cmdj("/xj 1a70.06f")]

    return ret


@cache("get_calls.cache")
def get_calls(r2p):
    """
    Look for BSR (aka calls) in a binary using r2pipe.
    """

    # Major Opcode #11 - 2 bytes BSR example:
    # Example:
    #   51b8           BSR 0x5C21
    bsr2_pattern = "01b0:0ef0"  # mask needed due to the instruction encoding
    ret = r2_search_memory(r2p, bsr2_pattern)


    # Major Opcode #13 - 4 bytes BSR example:
    # Example:
    #   99dc5506       BSR 0x78178
    bsr4_pattern = "09d80500:0fd80f00"  # mask needed due to the instruction encoding
    ret += r2_search_memory(r2p, bsr4_pattern)

    return ret


def is_camelcase_str(string):
    """Return True if string uses CamelCase."""

    # Discard non alpha strings
    if ' ' in string and not string.isalpha():
        return False

    # Look for two uppercase characters
    #uppers = filter(lambda c: c[0].isupper(), zip(string, xrange(len(string))))
    uppers = [c for c in zip(string, xrange(len(string))) if c[0].isupper()]
    if not uppers and len(string) < 2:
        return False

    # Check if they are followed by lowercase ones
    try:
        before_char = string[uppers[0][1]+1]
        after_char = string[uppers[0][1]+2]
        if before_char.islower() and after_char.islower():
            return True
    except IndexError:
        return False

    return False
