# Copyright (C) 2017 Guillaume Valadon <guillaume@valadon.net>

"""
Objets that simply binaries manipulation
"""


from flashre.utils import get_r2pipe, get_strings, get_prologues

from miasm2.analysis.machine import Machine


class ReverseFlashairBinary(object):
    """
    Frequent operations on the flashair binary
    """

    def __init__(self, filename, offset=0, r2_options=None):
        """
        Initialize the object
        """

        # Remember the file offset
        self.offset = offset

        # Get a r2pipe handle
        self.r2p = get_r2pipe(filename, offset, r2_options)

        # Create the miasm Machine
        self.machine = Machine("mepl")
        self.mn = self.machine.mn()

    def strings(self):
        """
        get_strings wrapper
        """
        return get_strings(self.r2p)

    def prologues(self):
        """
        get_prologues wrapper
        """
        return get_prologues(self.r2p)

    def nearest_prologue(self, address):
        prologues = sorted([(address-p, p) for p in self.prologues() if p < address])
        if len(prologues):
            return prologues[0][1]
        return prologues
