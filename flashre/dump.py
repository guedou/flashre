# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Dump the FlashAir memory using telnet
"""


import sys

from flashre.telnet import FlashAirTelnet
from flashre.utils import args_detect_int


def convert_dump(filename):
    """Convert a memory dump to binary."""

    # Get the file content
    fd_dump = open(filename)
    lines = fd_dump.readlines()

    # Remove useless lines
    lines = [l for l in lines if l[0] is not 'a']
    lines = [l for l in lines if "dump" not in l]
    lines = [l for l in lines if '>' not in l]
    lines = [l for l in lines if not l.startswith('#')]

    # Transform and merge data
    lines = [l.strip().replace(' ', '') for l in lines]
    content = ''.join(lines)

    # Decode hexadecimal values
    content = content.decode("hex")

    # Convert to big or little endian
    binary = ""
    for offset in range(0, len(content), 4):
        value = content[offset:offset+4]

        binary += value[3] + value[2] + value[1] + value[0]

    return binary


def dump_register(parser):
    """
    Register the 'dump' sub-command.
    """
    new_parser = parser.add_parser("dump", help="Dump FlashAir memory")
    new_parser.add_argument("-t", "--target", dest="target",
                            default="192.168.0.1",
                            help="address or name of the FlashAir")
    new_parser.add_argument("-b", "--begin", dest="begin",
                            type=args_detect_int, default=0,
                            help="begin the dump at this address")
    new_parser.add_argument("-e", "--end", dest="end",
                            type=args_detect_int, default=0x200000,
                            help="end the dump at this address")
    new_parser.add_argument("-c", "--convert", dest="convert", default=False,
                            action="store_true",
                            help="convert a FlashAir text dump")
    new_parser.add_argument("filename", help="FlashAir dump filename")
    new_parser.set_defaults(func=dump_command)


def dump_command(args):
    """
    Dump FlashAir memory.
    """

    if args.convert:
        binary = convert_dump(args.filename)
        print binary

    else:

        if args.end <= args.begin:
            message = "Incorrect addresses range (0x%x, 0x%x) !"
            print >> sys.stderr, message % (args.begin, args.end)
            sys.exit()

        try:
            fd_dump = open(args.filename, "w")
        except Exception:
            print >> sys.stderr, "Cannot open '%s' !" % args.filename
            sys.exit()

        fat = FlashAirTelnet(args.target)
        for address in xrange(args.begin, args.end, 0x184):
            # Dont dump over args.end
            offset = args.end - address
            if offset > 0x180:
                length = 0x180
            else:
                length = offset
            dump_cmd = "dump 0x%x -l 0x%x" % (address, length)
            print >> fd_dump, fat.single_command(dump_cmd)

        fd_dump.close()
        fat.close()
