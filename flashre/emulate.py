# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Emulate function from a FlashAir binary using miasm2
"""


import struct

from miasm2.analysis.machine import Machine
from miasm2.jitter.csts import *

from flashre.utils import args_detect_int


# TODO
# - use Sandbox.call() ?
# - pass functions arguments from the command line
# - add breakpoint from the command line


def emulate_register(parser):
    """
    Register the 'emulate' sub-command.
    """
    new_parser = parser.add_parser("emulate", help="emulate a function")
    new_parser.add_argument("binary_filename", help="flashair binary filename")
    new_parser.add_argument("function_address", type=args_detect_int, default=0,
                            help="the function address to emulate")
    new_parser.add_argument("--log_mn", action='store_true', default=False,
                             help="show instructions")
    new_parser.add_argument("--log_regs", action='store_true', default=False,
                             help="show registers values")
    new_parser.set_defaults(func=emulate_command)


def emulate_command(args):
    """
    Emulate a function. 
    """

    machine = Machine("mepl")
    jitter = machine.jitter(jit_type="gcc")  # TODO: from args
    jitter.init_stack()

    asm = open(args.binary_filename).read()
    jitter.vm.add_memory_page(0, PAGE_READ | PAGE_WRITE, asm)
    jitter.cpu.LP = 0x2807

    jitter.vm.add_memory_page(0x2807, PAGE_READ | PAGE_WRITE, "Hello MeP!\x00")
    jitter.cpu.R1 = 0x2807

    jitter.add_breakpoint(jitter.cpu.LP, lambda x: False)

    jitter.jit.log_mn = args.log_mn
    jitter.jit.log_regs = args.log_regs

    jitter.init_run(args.function_address)
    jitter.continue_run()
