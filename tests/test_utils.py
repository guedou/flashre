# Copyright (C) 2018 Guillaume Valadon <guillaume@valadon.net>

"""
Test utils.py
"""


import mock


class TestUtils(object):

    def test_is_camelcase_str(self):
        """
        Test the is_camelcase_str() function
        """
  
        from flashre.utils import is_camelcase_str

        bad_inputs = [" CamelCase", "CamelCasE", "CAmelCase"]
        good_inputs = ["ccCamelCaseee", "CamelCase", "CaMelCaSe"]

        for _string in bad_inputs:
            assert is_camelcase_str(_string) is False

        for _string in good_inputs:
            assert is_camelcase_str(_string) is True
