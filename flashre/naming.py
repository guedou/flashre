# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
Functions naming strategies
"""

import json

from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import r2_search_memory


def print_r2_definitions(candidates):
    """
    Display results using r2 syntax for functions definitions
    """

    for fname in candidates:
        addresses = candidates[fname]
        if len(addresses) > 1:
            for i in xrange(0, len(addresses)):
                print "af %s_%d %s" % (fname, i, addresses.pop())
        else:
            print "af %s 0x%x" % (fname, addresses.pop() + 0xC00000)


class NamingError(object):
    """
    Naming strategy based on error strings.
    """

    @classmethod
    def drop_string(cls, string):
        """
        Discard useless strings.
        """
        return not string.strip().endswith("] (error) %s:%d")

    @classmethod
    def lookup(cls, rfb, address):
        """
        Look for MOV instructions that are using the string address.

        Based on observations, they are "MOVU R1, <ADDRESS>" with a 24 bytes
        immediate aka Major Opcode #13 MOVU.
        """

        # Assemble a MOV that uses this address
        mode = rfb.machine.dis_engine().attrib
        instr = rfb.mn.fromstring("MOVU R1, 0x%x" % (address + rfb.offset), mode)
        # Discard canditates that does not encode R1 on 3 bits
        targets = [(x.encode("hex"), str(rfb.mn.dis(x, mode))) for x in rfb.mn.asm(instr, mode) if x[1] == '\xd1']

        # Look for the offset of these instructions
        ret = []
        for bin_tgt, _ in targets:
            ret += r2_search_memory(rfb.r2p, bin_tgt)  # GV: could be cached

        return ret

    @classmethod
    def check(cls, rfb, string, candidates):
        """
        Extract possible candidates based on the "error" patterns:

        Example:
            0x00c11796      43d1c5c9       MOVU R1, 0xC9C543           ; r1=0xc9c543 "[APL] (error) %s:%d "
            0x00c1179a      34d2c5c9       MOVU R2, 0xC9C534           ; r2=0xc9c534 "APPL_endBuffer"
            0x00c1179e      01c3f901       MOV R3, 505                 ; r3=0x1f9 -> 0xffffff00
        """

        # Extract the function category from the format string
        prefix = string[string.index("[")+1:string.index("]")].replace(" ", "")

        faddresses = set()
        for offset in candidates:
            # Disassemble three instructions and look for the expected sequence
            instructions = json.loads(rfb.r2p.cmd("pdj 3 @ 0x%x" % offset))

            if not instructions[1]["opcode"].startswith("MOVU R2"):
                continue

            # Extract the immediate from the second instruction
            fname_str_addr = instructions[1]["opcode"].split(",")[1][0:]
            fname_str_addr = int(fname_str_addr, 16)
            real_fname = "%s.%s" % (prefix, rfb.r2p.cmd("ps @ 0x%x" % fname_str_addr))

            # Get the closest candidate
            fname_addr = sorted([(int(offset)-p, p) for p in rfb.prologues() if p < int(offset)])
            if not len(fname_addr):
                continue
            faddresses.add(fname_addr[0][1])

        return real_fname.strip(), faddresses


# Naming strategies
NAMING_STRATEGIES = dict()
NAMING_STRATEGIES["error"] = NamingError
#naming_strategies["camelcase"] = naming_camelcase #naming_strategies["printf"] = naming_printf


def naming_register(parser):
    """
    Register the naming sub-command.
    """

    def _detect_int(i):
        return int(i, 0)

    new_parser = parser.add_parser("naming", help="Auto-naming functions")
    new_parser.add_argument("--strategy", choices=NAMING_STRATEGIES.keys(),
                            default="error", help="Naming strategies")
    new_parser.add_argument("--offset", type=_detect_int, default=0,
                            help="map file at given address")
    new_parser.add_argument("binary_filename", help="flashair binary filename")
    new_parser.set_defaults(func=naming_command)


def naming_command(args):
    """
    Auto-name functions using well-known patterns.
    """

    # Initialize objects
    rfb = ReverseFlashairBinary(args.binary_filename, args.offset)
    strategy = NAMING_STRATEGIES[args.strategy]()

    # Start auto-naming
    candidates = dict()
    for offset, string in rfb.strings():
        # Discard non valid strings
        if strategy.drop_string(string):
            continue

        # Look for an instruction that manipulates this string
        instr_offsets = strategy.lookup(rfb, offset)

        # Gather candidates
        fname, addresses = strategy.check(rfb, string, instr_offsets)
        candidates[fname] = candidates.get(fname, set())
        candidates[fname].update(addresses)

    # Display the the results as r2 commands
    print_r2_definitions(candidates)
