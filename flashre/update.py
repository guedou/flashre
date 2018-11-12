# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Manipulate FlashAir updates
"""


import os
import sys

from scapy.all import Packet, StrFixedLenField, StrFixedLenEnumField, \
                      XShortField, XIntField, XByteField, LEIntField, raw


# FlashAir update header definition
UPDATE_HEADER_TYPES = ["MAIN2", "BOOT", "MAC", "RF", "USRPRG"]


class FlashAirUpdateHeader(Packet):
    name = "FlashAir Update Header"
    fields_desc = [StrFixedLenEnumField("card", "FLASHAIR", 8,
                                        UPDATE_HEADER_TYPES),
                   # 'name' is not a valid Scapy field name
                   StrFixedLenField("type", "MAIN2", 8),
                   StrFixedLenField("unk0", "\x01\x02\x03\x04", 4),
                   XShortField("unk1", 0),
                   XIntField("unk2", 0),
                   XByteField("checksum", 0),
                   XByteField("unk3", 0),
                   LEIntField("length", 0),
                   ]


def checksum(data):
    """
    Compute the checksum used in FlashAir updates.
    """

    cksum = 0
    for _byte in data:
        cksum = (cksum + ord(_byte)) & 0xFF

    return cksum


def load_update(filename):
    """
    Load an update, and return a header object and the data.
    """

    try:
        f_obj = open(filename, "rb")
        header = f_obj.read(32)  # length of the update header
        return FlashAirUpdateHeader(header), f_obj.read()
    except IOError:
        print >> sys.stderr, "load_update(): can't open '%s' ! " % filename
        return None, None


def fake_update(filename, fake_data_filename, w04, header_type="BOOT"):
    """
    Build a fake update file.
    """

    # Check arguments validity
    if len(header_type) > 8:
        print >> sys.stderr, "fake_update(): update type is too long!"
        return None

    if header_type not in UPDATE_HEADER_TYPES:
        print >> sys.stderr, "fake_update(): invalid header type!"
        return None

    # Load fake data from file
    try:
        f_obj = open(fake_data_filename, "rb")
        data = f_obj.read()
    except IOError:
        msg = "load_update(): can't open fake data '%s' !"
        print >> sys.stderr, msg % fake_data_filename
        return None

    # Build the header
    header = FlashAirUpdateHeader()
    header.type = header_type
    header.checksum = checksum(data)
    header.length = len(data)
    if w04:
        header.unk0 = "W-04"

    # Do not write to the file if it already exists
    if os.path.exists(filename):
        msg = "fake_upate(): '%s' already exists! Delete if needed."
        print >> sys.stderr, msg % filename
        return None

    # Write the fake update to disk
    f_obj = open(filename, "wb")
    f_obj.write(raw(header) + data)
    f_obj.close()

    return len(data)


def update_register(parser):
    """
    Register the 'update' sub-command.
    """
    new_parser = parser.add_parser("update", help="Play with updates")
    new_parser.add_argument("--check", action='store_true', default=True,
                            help="display and check the header")
    new_parser.add_argument("--fake", help="build a fake update using the data from this file")
    new_parser.add_argument("--type", help="fake update type",
                            default="USRPRG",
                            choices=UPDATE_HEADER_TYPES)
    new_parser.add_argument("--w04", help="build a fake W-04 update",
                            action="store_true", default=False)
    new_parser.add_argument("update_filename", help="FlashAir update filename")
    new_parser.set_defaults(func=update_command)


def update_command(args):
    """
    Update files manipulation.
    """

    # Build a fake update
    if args.fake and fake_update(args.update_filename, args.fake, args.w04,
                                 header_type=args.type) is None:
        return

    # Verify the checksum an display the header
    if args.check:
        header, data = load_update(args.update_filename)
        if header is None:
            return

        header.show()
        assert checksum(data) == header.checksum
