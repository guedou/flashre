# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
Explore the calls graph
"""


from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import r2_search_memory, args_detect_int


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


def reverse_callgraph(rfb, address):
    """
    Attempt to find functions calling address

    Note: it is currently too slow for most use cases.
    """

    callers = list()

    # Assemble all possible BSR variants that could encode this address
    mode = rfb.machine.dis_engine().attrib

    # Bruteforce the 12 and 24 bits variants
    for offset in xrange(0, 0xFFFF, 2):
    #for offset in xrange(0x3b0, 0x3d0, 2):  # test with 0xc6786a
        offset = 0
        instr = rfb.mn.fromstring("BSR %s" % offset, mode)
        instr_candidates = rfb.mn.asm(instr, mode)

        for bin_tgt in instr_candidates:
            # Discard the 12 bits when the offset can't be encoded
            if offset > 0xFFF and len(bin_tgt) == 2:
                continue

            # Look the instruction in memory, disassemble hits, and find the
            # caller address
            candidates = r2_search_memory(rfb.r2p, bin_tgt.encode("hex"))
            for tmp_c in candidates:
                tmp = rfb.r2p.cmdj("pdj 1 @ %s" % tmp_c)
                if tmp[0]["jump"] == address:
                    caller_address = rfb.nearest_prologue(tmp_c)
                    if caller_address:
                        callers.append(caller_address)

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
    Graph exloration.
    """

    # Initialize object
    rfb = ReverseFlashairBinary(args.binary_filename, args.offset)

    # Print xrefs
    if args.reverse:
        print [hex(f) for f in reverse_callgraph(rfb, args.address)]
    else:
        dump_functions(rfb, args.address)
