# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Test dump.py
"""


class TestDump(object):

    def test_convert(self):
        """
        Test the convert_dump() function
        """

        from flashre.dump import convert_dump

        from mock import patch, mock_open

        dump_output = """
dump 0x0 -l 0x180
address=0x00000000 length=0x180
 0001d808 0008df18 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 """
        with patch("__builtin__.open", mock_open(read_data=dump_output)) as mock_file:
            binary = convert_dump("mock.log")

            mock_file.assert_called_with("mock.log")
            assert binary[:16] == "08d8010018df08000000000000000000".decode("hex")
