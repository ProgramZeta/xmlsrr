import unittest
from xmlssr import xmlssr

class TestInitialization(unittest.TestCase):

    def setUp(self):
        pass

    def test_help(self):
        arguments = "-h"

    def test_no_output_folder(self):
        arguments = ""

    def test_output_folder(self):
        arguments ="tmp"