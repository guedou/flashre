# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
The main glue
"""


import argparse

from flashre.dump import dump_register, dump_command
from flashre.emulate import emulate_register, emulate_command
from flashre.flags import flags_register, flags_command
from flashre.hints import hints_register, hints_command
from flashre.naming import naming_register, naming_command
from flashre.telnet import telnet_register, telnet_command
from flashre.update import update_register, update_command
from flashre.xref import xref_register, xref_command


if __name__ == "__main__":
    # Allow sub-parsers
    parser = argparse.ArgumentParser(description="Toshiba Flashair RE tools")
    subparser = parser.add_subparsers()

    # Register sub-commands
    dump_register(subparser)
    emulate_register(subparser)
    flags_register(subparser)
    hints_register(subparser)
    naming_register(subparser)
    telnet_register(subparser)
    update_register(subparser)
    xref_register(subparser)
    args = parser.parse_args()

    # Call the sub-command
    args.func(args)
