# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
Functions naming strategies
"""


import json
import re

from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import r2_search_memory, is_camelcase_str, args_detect_int


def print_r2_definitions(candidates):
    """
    Display results using r2 syntax for functions definitions
    """

    for fname in candidates:
        addresses = candidates[fname]
        if len(addresses) > 1:
            for i in xrange(0, len(addresses)):
                print "af %s_%d 0x%x" % (fname, i, addresses.pop())
        elif len(addresses) == 1:
            print "af %s 0x%x" % (fname, addresses.pop())


class Naming(object):
    """
    Generic naming methods used to easily experiment with new strategies
    """

    @classmethod
    def drop_string(cls, string):
        raise NotImplementedError("Naming.drop_string()")

    @classmethod
    def assemble_instructions(cls, rfb, address):
        raise NotImplementedError("Naming.assemble_instructions()")

    @classmethod
    def is_valid_pattern(cls, rfb, prefix, offset):
        raise NotImplementedError("Naming.is_valid_pattern()")

    @classmethod
    def lookup(cls, rfb, address):
        """
        Look for instructions that are using the string address.
        """

        # Asssemble instructions
        targets = cls.assemble_instructions(rfb, address)

        # Look for the offset of these instructions
        ret = []
        for bin_tgt, _ in targets:
            ret += r2_search_memory(rfb.r2p, bin_tgt)  # GV: could be cached

        return ret

    @classmethod
    def assemble_mov13(cls, rfb, reg, address, filter_pattern):
        """
        Assemble MOV#13 instructions.
        """

        # Assemble a MOV that uses this address
        mode = rfb.machine.dis_engine().attrib
        addr = address + rfb.offset
        instr = rfb.mn.fromstring("MOVU %s, 0x%x" % (reg, addr), mode)
        # Discard candidates that does not encode the register on 3 bits
        candidates = rfb.mn.asm(instr, mode)
        targets = [(x.encode("hex"), str(rfb.mn.dis(x, mode))) for x in candidates
                   if x[1] == filter_pattern]

        return targets

    @classmethod
    def extract_prefix(cls, string):
        """
        Extract the function category from the format string.

        Dummy implementation.
        """
        return string

    @classmethod
    def check(cls, rfb, string, candidates):
        """
        Extract possible candidates based on the current pattern.
        """

        faddresses = set()
        real_fname = ""
        for offset in candidates:

            # Validate the current pattern
            real_fname = cls.is_valid_pattern(rfb, string, offset)
            if len(real_fname) == 0:
                continue

            # Get the closest candidate
            fname_addr = sorted([(int(offset)-p, p) for p in rfb.prologues()
                                 if p < int(offset)])
            if not len(fname_addr):
                continue
            faddresses.add(fname_addr[0][1])

        return real_fname.strip(), faddresses


class NamingError(Naming):
    """
    Naming strategy based on error strings.
    """

    @classmethod
    def drop_string(cls, string):
        """
        Discard useless strings.
        """

        # Regular Expression pattern matching error messages
        # Examples:
        #   [APL] (error) %s:%d
        #   [WPA] (error) <WNK> %s:%d
        #   [iSD] (err) %s:%d
        pattern = re.compile(r"\] \(err.?.?\)")

        return re.search(pattern, string) is None

    @classmethod
    def assemble_instructions(cls, rfb, address):
        """
        Assemble MOV instructions that are using the string address.

        Based on observations, they are "MOVU R1, <ADDRESS>" with a 24 bits
        immediate aka Major Opcode #13 MOVU.
        """

        return cls.assemble_mov13(rfb, "R1", address, "\xd1")

    @classmethod
    def extract_prefix(cls, string):
        """
        Extract the function category from the format string.
        """
        return string[string.index("[")+1:string.index("]")].replace(" ", "")

    @classmethod
    def is_valid_pattern(cls, rfb, string, offset):
        """
        Check a sequence of instructions to validate the "error" pattern:

        Example:
            0x00c11796      43d1c5c9       MOVU R1, 0xC9C543           ; r1=0xc9c543 "[APL] (error) %s:%d "
            0x00c1179a      34d2c5c9       MOVU R2, 0xC9C534           ; r2=0xc9c534 "APPL_endBuffer"
            0x00c1179e      01c3f901       MOV R3, 505                 ; r3=0x1f9 -> 0xffffff00
            0x00c117a2      69df1200       BSR fcn.printf
        """

        # Get the fonction prefix, aka possibe category
        prefix = cls.extract_prefix(string)

        # Disassemble two instructions and look for the expected sequence
        instructions = json.loads(rfb.r2p.cmd("pdj 2 @ 0x%x" % offset))

        if not instructions[1]["opcode"].startswith("MOVU R2"):
            return ""

        # Extract the immediate from the second instruction
        fname_str_addr = instructions[1]["opcode"].split(",")[1][0:]
        fname_str_addr = int(fname_str_addr, 16)
        real_fname = "%s.%s" % (prefix,
                                rfb.r2p.cmd("ps @ 0x%x" % fname_str_addr))

        return real_fname


class NamingCamelCase(Naming):
    """
    Naming strategy based on CamelCase.
    """

    @classmethod
    def drop_string(cls, string):
        """
        Discard useless strings.
        """
        return is_camelcase_str(string) is False

    @classmethod
    def assemble_instructions(cls, rfb, address):
        """
        Assemble MOV instructions that are using the string address.

        Based on observations, they are "MOVU R2, <ADDRESS>" with a 24 bytes
        immediate aka Major Opcode #13 MOVU.
        """

        return cls.assemble_mov13(rfb, "R2", address, "\xd2")

    @classmethod
    def is_valid_pattern(cls, rfb, string, offset):
        """
        Check a sequence of instructions to validate the "CamelCase" pattern:

        Example:
            0x00c3dbe6      e1d184cd       MOVU R1, 0xCD84E1           ; r1=0xcd84e1 "[WPS] (error) %s:%d"
            0x00c3dbea      84d284cd       MOVU R2, 0xCD8484           ; r2=0xcd8484 "SendEapolFrameToXXXTask"
            0x00c3dbee      01c37001       MOV R3, 368                 ; r3=0x170 -> 0xffffff00
            0x00c3dbf2      e9dc4efd       BSR printf
        """

        instructions = json.loads(rfb.r2p.cmd("pdj 3 @ 0x%x" % offset))

        if not instructions[1]["opcode"].startswith("MOV"):
            return ""
        if not instructions[2]["opcode"].startswith("BSR"):
            return ""

        return string


# Naming strategies
NAMING_STRATEGIES = dict()
NAMING_STRATEGIES["error"] = NamingError
NAMING_STRATEGIES["camelcase"] = NamingCamelCase


def naming_register(parser):
    """
    Register the naming sub-command.
    """

    new_parser = parser.add_parser("naming", help="Auto-naming functions")
    new_parser.add_argument("--strategy", choices=NAMING_STRATEGIES.keys(),
                            default="error", help="Naming strategies")
    new_parser.add_argument("--offset", type=args_detect_int, default=0,
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
        if not instr_offsets:
            continue

        # Gather candidates
        fname, addresses = strategy.check(rfb, string, instr_offsets)
        if not fname:
            continue
        candidates[fname] = candidates.get(fname, set())
        candidates[fname].update(addresses)

    # Display the the results as r2 commands
    print_r2_definitions(candidates)
