# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Prepare the demo payload
"""


from __future__ import print_function

import sys

from flashre.binaries_helpers import ReverseFlashairBinary
from flashre.utils import r2_search_memory


def demo_register(parser):
    """
    Register the demo sub-command.
    """

    new_parser = parser.add_parser("demo",
                                   help="Build the demo payload")
    new_parser.add_argument("update_filename", help="flashair update filename")
    new_parser.set_defaults(func=demo_command)


def demo_command(args):
    """
    Build the demo payload
    """

    # Initialize the RFB object
    base_address = 0xc0ffe0
    rfb = ReverseFlashairBinary(args.update_filename, base_address)

    # Search the user task string in the binary
    addresses = list()
    for offset, _str in rfb.strings():
        if _str.startswith("+user_task"):
            addr = offset + base_address
            addresses.append(addr)

    # Assemble MOV instruction with the addresses
    candidates = list()
    for addr in addresses:
        candidate = rfb.assemble("MOVU R1, 0x%x" % addr)
        candidates.extend(candidate)

    # Search these instructions in the binary
    printf_addresses = set()
    for candidate in candidates:
        for offset in r2_search_memory(rfb.r2p, candidate.encode("hex")):
            # Disassemble two instructions
            result = rfb.r2p.cmdj("pdj 2 @ %s" % offset)
            try:
                instruction = result[1]["disasm"]
            except (IndexError, KeyError):
                print("Error: incorrect format: %s" % result, file=sys.stderr)
                continue

            # Check if it is a function call
            if not instruction.startswith("BSR"):
                print("Error: instruction is not BSR! - %s" % instruction,
                      file=sys.stderr)
                continue

            # Return the function address
            try:
                address = instruction.split(" ")[1]
                printf_addresses.add(address)
            except IndexError:
                print("Error: instruction is not BSR! - %s" % instruction,
                      file=sys.stderr)
                continue

    # Only a single address is valid
    if len(printf_addresses) != 1:
        print("Error: several addresses for printf() - %s" % printf_addresses,
              file=sys.stderr)
        sys.exit()

    # Assemble the MOVU instruction
    #printf_addresses = set([0xD0DEE0])  # v4.00.00 - used in userpg()
    mov_list = rfb.assemble("MOVU R0, %s" % printf_addresses.pop())
    # Filter the 24bits MOVU variant
    movu = [instr for instr in mov_list if instr[1] == "\xd0"]
    if len(movu) != 1:
        print("Error: several MOVU remains - %s" % movu,
              file=sys.stderr)
        sys.exit()

    movu_r0 = movu[0]
    movu_r1 = "0ad1001e".decode("hex")  # MOVU R1, 0x1E000A
    calc = """+-------------+
|        77345|
+-------------+

+-+ +-+ +-+ +-+
|7| |8| |9| |/|
+-+ +-+ +-+ +-+

+-+ +-+ +-+ +-+
|4| |5| |6| |*|
+-+ +-+ +-+ +-+

+-+ +-+ +-+ +-+
|1| |2| |3| |-|
+-+ +-+ +-+ +-+

    +-+     +-+
    |0|     |+|
    +-+     +-+
"""

    # Add a RET and a NULL byte
    sys.stdout.write(movu_r0 + movu_r1 + "\x02\x70" + calc + "\x00")
