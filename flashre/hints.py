# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
Display strings used in functions
"""


import json

from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import args_detect_int, r2_search_memory


def load_hints(rfb, base_address, keyword):
    """
    Load strings matching the keyword and build the hints dictionary
    """

    hints = dict()
    for offset, _str in rfb.strings():
        if _str.lower().find(keyword.lower()) is not -1:
            offset += base_address  # TODO: remove when radare2 is fixed
            offsets = (offset & 0xFF,
                       (offset >> 8) & 0xFF,
                       (offset >> 16) & 0xFF)
            movu_pattern = "%.2xd.%.2x%.2x" % offsets
            for addr in r2_search_memory(rfb.r2p, movu_pattern):
                # TODO: add when radare2 is fixed
                #binary = rfb.r2p.cmd("p8 4 @ %d" % (addr + base_address))
                #mode = rfb.machine.dis_engine().attrib
                #instr = rfb.mn.dis(binary.decode("hex"), mode)
                #if not str(instr).startswith("MOVU"):
                #    continue
                hints[addr] = _str
    return hints


def reverse_hints(rfb, address):
    """
    Identify strings used in functions
    """
    rfb.r2p.cmd("s %s; af " % address)
    instructions = json.loads(rfb.r2p.cmd("pdj $FI"))

    for instr in instructions:
        if instr["opcode"].startswith("MOVU"):
            str_addr = instr["opcode"].split(",")[1]
            r2_str = rfb.r2p.cmd("ps @ %s" % str_addr)
            if r2_str and r2_str[0] != '\\':
                print address, str_addr.lower(), r2_str


def hints_register(parser):
    """
    Register the hints sub-command.
    """

    new_parser = parser.add_parser("hints",
                                   help="Identify strings used in functions")
    new_parser.add_argument("--offset", type=args_detect_int, default=0,
                            help="map file at given address")
    new_parser.add_argument("--reverse", action='store_true', default=False,
                            help="find strings")
    new_parser.add_argument("binary_filename", help="flashair binary filename")
    new_parser.add_argument("keyword",
                            help="keyword OR function addresses filename")
    new_parser.set_defaults(func=hints_command)


def hints_command(args):
    """
    Display strings used in functions
    """

    # Initialize object
    rfb = ReverseFlashairBinary(args.binary_filename, args.offset)

    # Display strings used in functions
    if args.reverse:
        for address in open(args.keyword):
            reverse_hints(rfb, address.strip())
            print "===="
        return

    # Load hints and prologues
    hints = load_hints(rfb, args.offset, args.keyword)
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
