# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Manipulate MeP Control/Special registers flags
"""


import struct

from scapy.all import Packet, ByteField, BitField

from flashre.utils import args_detect_int


# 3.3.20. CFG (Configuration Register), page 40
class CFG(Packet):
    name = "Configuration Register"
    fields_desc = [ByteField("unk0", 0),  # R
                   BitField("EVA", 0, 1),  # RW
                   BitField("IVA", 0, 1),  # RW
                   BitField("unk1", 0, 6),  # R
                   ByteField("unk2", 0),  # R
                   # LEND: initial value specified by the configuration
                   BitField("LEND", 0, 1),  # R
                   # DSPL: initial value depends on the external signal value
                   BitField("DSPL", 0, 1),  # R
                   BitField("unk3", 1, 1),  # R
                   BitField("EVM", 0, 1),  # RW
                   BitField("IVM", 1, 1),  # RW
                   BitField("unk4", 0, 1),  # R
                   BitField("ICE", 0, 1),  # RW
                   BitField("DCE", 0, 1)  # RW
                   ]


def flags_register(parser):
    """
    Register the 'flags' sub-command.
    """
    new_parser = parser.add_parser("flags", help="Display registers flags")
    new_parser.add_argument("--cfg", action='store_true', default=False,
                            help="display and check the header")
    new_parser.add_argument("value", type=args_detect_int,
                            help="register value")
    new_parser.set_defaults(func=flags_command)


def flags_command(args):
    """
    Display register flags.
    """

    # Build a fake update
    if args.cfg:
        cfg = CFG(struct.pack(">I", args.value)[0])
        cfg.show()
    else:
        print "Control register not implemented ?"
