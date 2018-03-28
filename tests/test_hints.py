# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Test hints.py
"""


from StringIO import StringIO

import mock


class TestHints(object):

    def test_load_hints(self):
        """
        Test the load_hints() function
        """
  
        from flashre.hints import load_hints
        from flashre.binaries_helpers import ReverseFlashairBinary

        # Build a fake ReverseFlashairBinary object
        # Note: get_r2pipe() could be mocked too!
        rfb = ReverseFlashairBinary("", 0)
        rfb.strings = mock.MagicMock(return_value=list())

        # Some bad inputs
        bad_inputs = list()
        bad_inputs.append("x\n")
        bad_inputs.append("x:\n")
        bad_inputs.append("  2dc6e0:       d0 01           mov $1,$tp\n")
        bad_inputs.append("     100:       00 70           di\n")

        # Mock the open() builtin
        m_open = mock.mock_open()
        m_open.return_value = bad_inputs
        with mock.patch("flashre.hints.open", m_open):
            assert load_hints(rfb, "") is None
