# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Extract interesting strings from a dump
"""


import json

from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import args_detect_int



def strings_register(parser):
    """
    Register the strings sub-command.
    """

    new_parser = parser.add_parser("strings", help="Extract strings from a dump")
    new_parser.add_argument("--value", type=args_detect_int, default=150,
                            help="strings per block threshold value")
    new_parser.add_argument("binary_filename", help="flashair binary filename")
    new_parser.set_defaults(func=strings_command)



def strings_command(args):
    """
    Extract strings
    """

    # Initialize object
    rfb = ReverseFlashairBinary(args.binary_filename)

    # Display strings
    strings_count = json.loads(rfb.r2p.cmd("b 128; p=zj"))
    for entropy in strings_count["entropy"]:
        if entropy["value"] >= args.value:
            print rfb.r2p.cmd("s %s; b 128; psb" % entropy["addr"])
