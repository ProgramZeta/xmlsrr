import unittest
import sys
from xmlsrr import xmlsrr
from io import StringIO
import os


class TestArgumentParser(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_stdout

    def test_help(self):
        arguments = '-h'
        self.assertRaises(SystemExit, xmlsrr.argumentParser, arguments)

    def test_no_target_folder(self):
        arguments = ''
        self.assertRaises(ValueError, xmlsrr.argumentParser, arguments)

    def test_target_folder_argument(self):
        arguments = '/tmp/xmlsrr-test'
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.target, arguments)

    def test_instruction_file_argument(self):
        instructionFile = '/tmp/test-instructions.txt'
        arguments = '/tmp/xmlsrr-test -i ' + instructionFile
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.instructions, instructionFile)

    def test_instruction_file_argument_long_name(self):
        instructionFile = '/tmp/test-instructions.txt'
        arguments = '/tmp/xmlsrr-test --instructions ' + instructionFile
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.instructions, instructionFile)

    def test_log_file_argument(self):
        logFile = '/tmp/test-log.log'
        arguments = '/tmp/xmlsrr-test -l ' + logFile
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.log, logFile)

    def test_log_file_argument_long_name(self):
        logFile = '/tmp/test-log.log'
        arguments = '/tmp/xmlsrr-test --log ' + logFile
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.log, logFile)

    def test_help_program_name(self):
        arguments = '-h'
        self.assertRaises(SystemExit, xmlsrr.argumentParser, arguments)
        self.assertRegex(self.output.getvalue(), "usage: xmlsrr")

    def test_output_folder_argument(self):
        outputFolder = '/tmp/xmlsrr/output/'
        arguments = '/tmp/xmlsrr/source/ -o ' + outputFolder
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.output, outputFolder)

    def test_output_folder_argument_long_name(self):
        outputFolder = '/tmp/xmlsrr/output/'
        arguments = '/tmp/xmlsrr/source/ --output ' + outputFolder
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.output, outputFolder)

    def test_silent_argument(self):
        arguments = '/tmp/xmlsrr/source/ -s'
        args = xmlsrr.argumentParser(arguments)
        self.assertTrue(args.silent)

    def test_silent_argument_long_name(self):
        arguments = '/tmp/xmlsrr/source/ --silent'
        args = xmlsrr.argumentParser(arguments)
        self.assertTrue(args.silent)

    def test_verbose_argument(self):
        arguments = '/tmp/xmlsrr/source/ -v'
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.verbose, 1)

    def test_verbose_argument_long_name(self):
        arguments = '/tmp/xmlsrr/source/ --verbose'
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.verbose, 1)

    def test_verbose_argument_multiple(self):
        arguments = '/tmp/xmlsrr/source -vvvv'
        args = xmlsrr.argumentParser(arguments)
        self.assertEqual(args.verbose, 4)

    def test_verify_argument(self):
        arguments = '/tmp/xmlsrr/source -V'
        args = xmlsrr.argumentParser(arguments)
        self.assertTrue(args.verify)

    def test_verify_argument_long_name(self):
        arguments = '/tmp/xmlsrr/source --verify'
        args = xmlsrr.argumentParser(arguments)
        self.assertTrue(args.verify)

class TestValidateTarget(unittest.TestCase):
    def test_destination_valid(self):
        def fakeOsAccess(targetFolder, test):
            if test == os.F_OK:
                return True
            if test == os.R_OK:
                return True

        os.access = fakeOsAccess

        targetFolder = '/tmp/xmlsrr/source'
        target = xmlsrr.validateTarget(targetFolder)
        self.assertEqual(target, targetFolder)

    def test_destination_invalid(self):
        def fakeOsAccess(targetFolder, test):
            if test == os.F_OK:
                return False

        os.access = fakeOsAccess

        targetFolder = '@!$@$!@$!$!@$'
        self.assertRaises(NotADirectoryError, xmlsrr.validateTarget, targetFolder)

    def test_destination_cannot_read(self):
        def fakeOsAccess(targetFolder, test):
            if test == os.F_OK:
                return True
            if test == os.R_OK:
                return False

        os.access = fakeOsAccess
        targetFolder = '/tmp/xmlsrr/source'
        self.assertRaises(PermissionError, xmlsrr.validateTarget, targetFolder)

    def test_destination_cannot_write(self):
        def fakeOsAccess(targetFolder, test):
            if test == os.F_OK:
                return True
            if test == os.R_OK:
                return True
            if test == os.W_OK:
                return False

        os.access = fakeOsAccess
        targetFolder = '/tmp/xmlsrr/source'
        self.assertRaises(PermissionError, xmlsrr.validateTarget, [targetFolder], False)
