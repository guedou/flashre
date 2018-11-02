#!/usr/bin/env python2
# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
flashair IO plugin - ease interacting with the Toshiba FlashAir SD card

Note: it could be used as follows:
    $ r2pm install lang-python2
    $ r2 -i flashair-io.py -qc 'o flashair://' --
"""


import os
import tempfile

import r2lang

from flashre.telnet import FlashAirTelnet
from flashre.dump import convert_dump


# Global variables
FAT = None
file_offset = 0


def flashair_check(path, many):
    """
    Check if the path contains the FlashAir 'protocol'
    """

    return path.startswith("flashair://")


def flashair_open(path, rw, perm):
    """
    Open a telnet collection to the FlashAir
    """

    global FAT
    FAT = FlashAirTelnet("192.168.0.1")

    return True


def flashair_seek(offset, whence):
    """
    Adjust the current file offset
    """

    global file_offset

    if whence == 0:  # SET
        file_offset = offset

    elif whence == 1:  # CUR
        file_offset += offset
        return file_offset

    elif whence == 2:  # END
        # Assuming the plugin only access the SPI 4MB
        file_offset = 0x400000 + offset
        return file_offset

    return file_offset


def flashair_read(offset, size):
    """
    Read data and return the corresponding bytes
    """

    global FAT

    try:
        # Dump bytes
        data = ""
        if size <= 0x180:
            data = FAT.single_command("dump 0x%x -l %d" % (offset, size))
        else:
            for address in xrange(offset, offset+size, 0x180):
                data = FAT.single_command("dump 0x%x -l %d" % (address, size))

        # Convert hex bytes to binary
        _, fname = tempfile.mkstemp()
        fdesc = open(fname, "w")
        fdesc.write(data)
        fdesc.close()
        data = convert_dump(fname)
        os.remove(fname)

    except Exception:
        data = '\x00' * size

    return data[:size]


def flashair_io_plugin(a):

    return {"name": "flashair",
            "license": "LGPL3",
            "desc": "flashair IO plugin (flashair://)",
            "check": flashair_check,
            "open": flashair_open,
            "seek": flashair_seek,
            "read": flashair_read}

# Register the IO plugin
r2lang.plugin("io", flashair_io_plugin)
