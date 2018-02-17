# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Emulate function form a FlashAir binary using miasm2
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
    #jitter.cpu.SP = 0x2807
    #jitter.vm.set_mem(0x2807, "\x00"*1024)

    jitter.cpu.R1 = ord('G')

    def emu_printf(jitter):
        s = jitter.get_str_ansi(jitter.cpu.R1)
        if not '%' in s:
            print s.strip()
        else:
            # Note: the following is specific to 0xc3d506
            print hex(jitter.cpu.SP)
            arg4 = struct.unpack("<I", jitter.vm.get_mem(jitter.cpu.SP, 4))[0]
            arg5 = struct.unpack("<I", jitter.vm.get_mem(jitter.cpu.SP+4, 4))[0]
            arg6 = struct.unpack("<I", jitter.vm.get_mem(jitter.cpu.SP+8, 4))[0]
            if s.strip() == "%d":
                print s.strip() % (jitter.cpu.R2 & 0xFF)
            elif s.strip() == "sock:%d, status:%x":
                print s.strip() % (jitter.cpu.R2 & 0xFF, jitter.cpu.R3)
            elif s.strip() == "next:%p, time:%d tsk:%d alm:%d":
                s = s.replace("%p", "%x")
                print s.strip() % (jitter.cpu.R2, jitter.cpu.R3, jitter.cpu.R4, arg4)
            elif s.strip() == "rbuf:%p, sbuf:%p top:%p end:%p":
                s = s.replace("%p", "%x")
                print s.strip() % (jitter.cpu.R2, jitter.cpu.R3, jitter.cpu.R4, arg4)
            elif s.strip() == "send_res:%p, method %p URI %p c_type %p c_body %p c_len %d":
                s = s.replace("%p", "%x")
                print s.strip() % (jitter.cpu.R2, jitter.cpu.R3, jitter.cpu.R4, arg4, arg5, arg6)
            elif s.strip() == "send byte: %u":
                print s.strip() % jitter.cpu.R2
            else:
                print s.strip()
                print s.strip() % (jitter.cpu.R2&0xFF, jitter.cpu.R3&0xFF, jitter.cpu.R4&0xFF, arg4&0xFF, arg5, arg6)
        jitter.pc = jitter.cpu.LP
        return True
    jitter.add_breakpoint(0xC12A8E, emu_printf)

    # Note: - attempt at emulating LDCB/STCB based putchar
    #       - these instructions could be implemented in sem.py, then we could
    #         use a memory breakpoint to catch these instructions
    #def emu_ldcb_3FE(jitter):
    #    jitter.cpu.R1 = 0x8
    #    #jitter.pc = 0x402
    #    return True
    #jitter.add_breakpoint(0x3FE, emu_ldcb_3FE)
    #
    #def emu_stcb_414(jitter):
    #    print "--> %c" % (jitter.cpu.R1 & 0xFF)
    #    return True
    #jitter.add_breakpoint(0x414, emu_stcb_414)

    jitter.add_breakpoint(jitter.cpu.LP, lambda x: False)

    jitter.jit.log_mn = args.log_mn
    jitter.jit.log_regs = args.log_regs

    jitter.init_run(args.function_address)
    jitter.continue_run()
