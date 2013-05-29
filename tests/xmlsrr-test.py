import unittest
from xmlssr import xmlssr

class TestInitialization(unittest.TestCase):

    def setUp(self):
        pass

    def test_help(self):
        arguments = "-h"
        self.assertRaises(SystemExit, xmlssr.argument_parser, arguments)

    def test_no_target_folder(self):
        arguments = ""
        self.assertRaises(ValueError, xmlssr.argument_parser, arguments)

    def test_target_folder_argument(self):
        arguments = "/tmp/xmlrss-test"
        args = xmlssr.argument_parser(arguments)
        self.assertEqual(args.target, arguments)

    def test_instruction_file_argument(self):
        arguments = "/tmp/xmlrss-test -i /tmp/butt"
        args = xmlssr.argument_parser(arguments)