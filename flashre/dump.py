# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Dump the FlashAir memory using telnet
"""


from flashre.telnet import FlashAirTelnet

# flash dump using telnet directly
#  -> check why the old code does not work anymore ..
# full memmory dump using the watchdog
# dump conversion, using struct !
#  struct.pack(">I", struct.unpack("<I", data)[0]) # Convert from LE to BE !
# -> it seems that the printf %08x converts data to LE
# TODO: telnet based memory dump


def convert_dump(filename):
    """Convert a memory dump to binary."""

    # Get the file content
    fd = open(filename)
    lines = fd.readlines()

    # Remove useless lines
    lines = filter(lambda l: l[0] is not "a", lines)
    lines = filter(lambda l: not "dump" in l, lines)
    lines = filter(lambda l: not ">" in l, lines)
    lines = [ l for l in lines if not l.startswith("#") ]

    # Transform and merge data
    lines = map(lambda l: l.strip().replace(" ", ""), lines)
    content = "".join(lines)

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
    new_parser.add_argument("-t", "--target", dest="target", default="192.168.0.1",
                            help="address or name of the FlashAir")
    new_parser.add_argument("-c", "--convert", dest="convert", default=False,
                            action="store_true", help="convert a FlashAir text dump")
    new_parser.add_argument("filename", help="FlashAir dump filename")
    new_parser.set_defaults(func=dump_command)


def dump_command(args):
    """
    Dump FlashAir memory.
    """

    if not args.convert:
        print >> sys.stderr, "Only '--convert' is currently implemented!"

    binary = convert_dump(args.filename)

    print binary
