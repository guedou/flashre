# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Explore the calls graph
"""


import collections

from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import args_detect_int


def callgraph(rfb, address):
    """
    List functions called from address.
    """

    # Define a function, and find xrefs
    rfb.r2p.cmd("s 0x%x" % address)
    rfb.r2p.cmd("af 0x%x" % address)
    calls = rfb.r2p.cmd("afx 0x%x" % address)

    # afxj is not implemented, the output must be parsed manually
    called = list()
    if calls:
        for line in calls.split('\n'):
            if not line.startswith("C"):
                continue
            tmp = line.split('>')[1][1:]
            addr = int(tmp, 16)
            called.append(addr)

    return called


def dump_functions(rfb, address):
    """"
    Recursively print all functions called from address
    """

    done = set()
    addresses = [address]
    while addresses:

        tmp = addresses.pop(0)
        ret = set(callgraph(rfb, tmp))
        addresses += [f for f in ret if f not in done]
        done.add(tmp)

        print hex(tmp), "->", [hex(f) for f in ret]
    return done


# Ease implementing the reverse callgraph detection logic
BSR = collections.namedtuple("BSR", ["pattern", "verify"])

def _verify_bsr12(address, r2_hit):
    """
    Verify the immediate encoded by the 12 bits BSR variant
    """

    # Discard offsets that cannot be encoded with 12 bits
    if (address - r2_hit["offset"]) > 0xFFF:
        return False
    imm = (address - r2_hit["offset"]) & 0xFFF

    # Check the encoded immediate
    value = int(r2_hit["data"], 16)
    if (((value & 0xF) << 8) + (value >>8)-1) != imm:
        return False

    return True
BSR12 = BSR("01b0:01f0", _verify_bsr12)


def _verify_bsr24(address, r2_hit):
    """
    Verify the immediate encoded by the 24 bits BSR variant
    """

    # Discard offsets that cannot be encoded with 24 bits
    if (address - r2_hit["offset"]) > 0xFFFFFF:
        return False
    imm = (address - r2_hit["offset"]) & 0xFFFFFF

    # Check the encoded immediate
    value = int(r2_hit["data"], 16)

    tmp = (value & 0xFF) << 16
    tmp += ((value & 0xFF00)>> 8) << 8
    inverted_bytes = ((value >> 24) & 0xFF) + ((value >> 8) & 0xFF00)
    tmp += ((inverted_bytes >> 4) & 0x7F) << 1

    if tmp != imm:
        return False

    return True
BSR24 = BSR("09d80000:0ff80000", _verify_bsr24)


def reverse_callgraph(rfb, address):
    """
    List functions that are using this address.

    Due to r2m2 performance, BSR are searched using their 12 and 24 bits
    patterns. The corresponding immediates are decoded directly without the
    disassembler.

    Note: this function does not detect JMP based calls that occur sometimes.
    """


    callers = list()
    for bsr in [BSR12, BSR24]:
        for hit in rfb.r2p.cmdj("/xj %s" % bsr.pattern):
            # Discard non even offsets
            if hit["offset"] % 2:
                continue

            # Verify the called address
            if not bsr.verify(address, hit):
                continue

            # Extract the caller address
            for instr in rfb.r2p.cmdj("pdj 1 @ %s" %  hit["offset"]):
                if instr["jump"] == address:
                    callers.append(rfb.nearest_prologue(instr["offset"]))

    return callers


def xref_register(parser):
    """
    Register the xrefs sub-command.
    """

    new_parser = parser.add_parser("xref", help="Explore the calls graph")
    new_parser.add_argument("--offset", type=args_detect_int, default=0,
                            help="map file at given address")
    new_parser.add_argument("--reverse", action='store_true', default=False, help="find callers")
    new_parser.add_argument("binary_filename", help="flashair binary filename")
    new_parser.add_argument("address", type=args_detect_int, help="find xref from this address")
    new_parser.set_defaults(func=xref_command)


def xref_command(args):
    """
    Graph exploration.
    """

    # Initialize object
    rfb = ReverseFlashairBinary(args.binary_filename, args.offset)

    # Print xrefs
    if args.reverse:
        print [hex(f) for f in reverse_callgraph(rfb, args.address)]
    else:
        dump_functions(rfb, args.address)
