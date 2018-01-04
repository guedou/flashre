# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
The main glue
"""


import argparse

from flashre.naming import naming_register, naming_command
from flashre.hints import hints_register, hints_command
from flashre.xref import xref_register, xref_command
from flashre.update import update_register, update_command


if __name__ == "__main__":
    # Allow sub-parsers
    parser = argparse.ArgumentParser(description="Toshiba Flashair RE tools")
    subparser = parser.add_subparsers()

    # Register sub-commands
    naming_register(subparser)
    hints_register(subparser)
    xref_register(subparser)
    update_register(subparser)
    args = parser.parse_args()

    # Call the sub-command
    args.func(args)
