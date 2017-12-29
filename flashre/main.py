# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
The main glue
"""


import argparse

from flashre.naming import naming_register, naming_command


if __name__ == "__main__":
    # Allow sub-parsers
    parser = argparse.ArgumentParser(description="Toshiba Flashair RE tools")
    subparser = parser.add_subparsers()

    # Register sub-commands
    naming_register(subparser)
    args = parser.parse_args()

    # Call the sub-command
    args.func(args)
