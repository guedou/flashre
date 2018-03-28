# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
Display strings used in functions
"""


import string

from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import args_detect_int


def load_hints(rfb, filename):
    """
    Load strings from the objdump output and build the hints dictionary
    """

    # Build the strings dictionary
    strings_dict = dict()
    for offset, _str in rfb.strings():
        if len([c for c in _str if c in string.printable]) != len(_str):
            continue

        offset += rfb.offset  # workaround as iiz does not work fine when an
                              # offset is specified to r2
        strings_dict[offset] = _str

    # Build the hints dictionary
    hints = dict()
    for line in open(filename):
        try:
            addr = int(line.split(':')[0], 16)
            str_addr = int(line.split(',')[1], 16)
        except (ValueError, IndexError):
            continue

        if addr not in hints:
            value = strings_dict.get(str_addr, None)
            if value:
                hints[addr] = value

    return hints


def hints_register(parser):
    """
    Register the hints sub-command.
    """

    new_parser = parser.add_parser("hints", help="Identify strings used in functions")
    new_parser.add_argument("--offset", type=args_detect_int, default=0,
                            help="map file at given address")
    new_parser.add_argument("binary_filename", help="flashair binary filename")
    new_parser.add_argument("movs_filename", help="objdump mov* output filename")
    new_parser.set_defaults(func=hints_command)


def hints_command(args):
    """
    Display strings used in functions
    """

    # Initialize object
    rfb = ReverseFlashairBinary(args.binary_filename, args.offset)

    # Load hints and prologues
    hints = load_hints(rfb, args.movs_filename)
    prologues = sorted(rfb.prologues())

    # Display hints
    hints_addresses = sorted(hints.keys())
    current_hint = hints_addresses.pop(0)
    faddr = prologues[0]

    for i in xrange(1, len(prologues)-1):
        print_line = False
        faddr_next = prologues[i+1]
        while faddr < current_hint < faddr_next:
            print hex(faddr), hex(current_hint), hints[current_hint]
            if len(hints_addresses):
                current_hint = hints_addresses.pop(0)
            else:
                current_hint = -1  # exit the while loop
            print_line = True
        if print_line:
            print "===="
        faddr = faddr_next
