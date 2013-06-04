import unittest
import sys
from io import StringIO
import os
from lxml import html
from xmlsrr import xmlsrr
from xmlsrr import instructionSet


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
        self.assertRaises(SystemExit, xmlsrr.argumentParser, arguments.split())

    def test_no_target_folder(self):
        arguments = ''
        self.assertRaises(ValueError, xmlsrr.argumentParser, arguments)

    def test_target_folder_argument(self):
        arguments = '/tmp/xmlsrr-test'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.target, arguments)

    def test_instruction_file_argument(self):
        instructionFile = '/tmp/test-instructions.txt'
        arguments = '/tmp/xmlsrr-test -i ' + instructionFile
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.instructions, instructionFile)

    def test_instruction_file_argument_long_name(self):
        instructionFile = '/tmp/test-instructions.txt'
        arguments = '/tmp/xmlsrr-test --instructions ' + instructionFile
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.instructions, instructionFile)

    def test_log_file_argument(self):
        logFile = '/tmp/test-log.log'
        arguments = '/tmp/xmlsrr-test -l ' + logFile
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.log, logFile)

    def test_log_file_argument_long_name(self):
        logFile = '/tmp/test-log.log'
        arguments = '/tmp/xmlsrr-test --log ' + logFile
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.log, logFile)

    def test_help_program_name(self):
        arguments = '-h'
        self.assertRaises(SystemExit, xmlsrr.argumentParser, arguments.split())
        self.assertRegex(self.output.getvalue(), "usage: xmlsrr")

    def test_output_folder_argument(self):
        outputFolder = '/tmp/xmlsrr/output/'
        arguments = '/tmp/xmlsrr/source/ -o ' + outputFolder
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.output, outputFolder)

    def test_output_folder_argument_long_name(self):
        outputFolder = '/tmp/xmlsrr/output/'
        arguments = '/tmp/xmlsrr/source/ --output ' + outputFolder
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.output, outputFolder)

    def test_silent_argument(self):
        arguments = '/tmp/xmlsrr/source/ -s'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertTrue(args.silent)

    def test_silent_argument_long_name(self):
        arguments = '/tmp/xmlsrr/source/ --silent'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertTrue(args.silent)

    def test_verbose_argument(self):
        arguments = '/tmp/xmlsrr/source/ -v'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.verbose, 1)

    def test_verbose_argument_long_name(self):
        arguments = '/tmp/xmlsrr/source/ --verbose'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.verbose, 1)

    def test_verbose_argument_multiple(self):
        arguments = '/tmp/xmlsrr/source -vvvv'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertEqual(args.verbose, 4)

    def test_verify_argument(self):
        arguments = '/tmp/xmlsrr/source -V'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertTrue(args.verify)

    def test_verify_argument_long_name(self):
        arguments = '/tmp/xmlsrr/source --verify'
        args = xmlsrr.argumentParser(arguments.split())
        self.assertTrue(args.verify)


class TestValidateOptions(unittest.TestCase):
    pass


class TestParseInstructions(unittest.TestCase):
    pass


class TestValidateInstructionFile(unittest.TestCase):
    pass


class TestValidateVerbosity(unittest.TestCase):
    pass


class TestValidateTarget(unittest.TestCase):
    def test_destination_valid(self):
        def fakeOsAccess(targetFolder, test):
            if test == os.F_OK:
                return True
            if test == os.R_OK:
                return True

        os.access = fakeOsAccess

        targetFolder = '/tmp/xmlsrr/source'
        target = xmlsrr.validateTarget(targetFolder, None)
        self.assertEqual(target, targetFolder)


    def test_destination_invalid(self):
        def fakeOsAccess(targetFolder, test):
            if test == os.F_OK:
                return False

        os.access = fakeOsAccess

        targetFolder = '@!$@$!@$!$!@$'
        self.assertRaises(NotADirectoryError, xmlsrr.validateTarget, targetFolder, None)


    def test_destination_cannot_read(self):
        def fakeOsAccess(targetFolder, test):
            if test == os.F_OK:
                return True
            if test == os.R_OK:
                return False

        os.access = fakeOsAccess
        targetFolder = '/tmp/xmlsrr/source'
        self.assertRaises(PermissionError, xmlsrr.validateTarget, targetFolder, None)


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


class TestValidateOutput(unittest.TestCase):
    pass


class TestValidateLog(unittest.TestCase):
    pass


class TestValidateInstructionsExist(unittest.TestCase):
    def test_empty_instruction_list(self):
        instructionsList = []
        self.assertRaises(ValueError, xmlsrr.validateInstructionsExist, instructionsList)

    def test_no_instructions_provided(self):
        instructionsList = None
        self.assertRaises(ValueError, xmlsrr.validateInstructionsExist, instructionsList)

    def test_single_instruction(self):
        instructionsList = ['body']
        instructions = xmlsrr.validateInstructionsExist(instructionsList)
        self.assertEqual(instructions, instructionsList)

    def test_single_instruction_empty(self):
        instructionsList = ['']
        self.assertRaises(ValueError, xmlsrr.validateInstructionsExist, instructionsList)

    def test_multiple_instructions(self):
        instructionsList = ['body', 'p']
        instructions = xmlsrr.validateInstructionsExist(instructionsList)
        self.assertEqual(instructions, instructionsList)

    def test_mulitple_instructions_one_empty(self):
        instructionsList = ['', 'body']
        instructions = xmlsrr.validateInstructionsExist(instructionsList)
        self.assertEqual(instructions, ['body'])

    def test_multiple_instructions_all_empty(self):
        instructionsList = ['', '']
        self.assertRaises(ValueError, xmlsrr.validateInstructionsExist, instructionsList)


class TestMatchInstruction(unittest.TestCase):
    def test_element_no_match(self):
        htmlText = '<html><body><p class="awesome">Some Text</p></body></html>'
        instructions = 'div'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_element_match(self):
        htmlText = '<html><body><p class="awesome">Some Text</p></body></html>'
        instructions = 'p'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_class_no_match(self):
        htmlText = '<html><body><p class="awesome">Some Text</p></body></html>'
        instructions = '.non'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_class_match(self):
        htmlText = '<html><body><p class="awesome">Some Text</p></body></html>'
        instructions = '.awesome'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_id_no_match(self):
        htmlText = '<html><body><p id="someName" class="awesome">Some Text</p></body></html>'
        instructions = '#non'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_id_match(self):
        htmlText = '<html><body><p id="someName" class="awesome">Some Text</p></body></html>'
        instructions = '#someName'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_attribute_name_match(self):
        htmlText = '<html><body><p lang="en-us" id="someName" class="awesome">Some Text</p></body></html>'
        instructions = '[lang]'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_attribute_name_no_match(self):
        htmlText = '<html><body><p lang="en-us" id="someName" class="awesome">Some Text</p></body></html>'
        instructions = '[nolang]'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_attribute_value_match(self):
        htmlText = '<html><body><p lang="en-us" id="someName" class="awesome">Some Text</p></body></html>'
        instructions = '[lang=en-us]'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_attribute_value_no_match(self):
        htmlText = '<html><body><p lang="en-us" id="someName" class="awesome">Some Text</p></body></html>'
        instructions = '[lang=de-de]'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_match_multiple_classes_match_all(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p></body></html>'
        instructions = '.awesome.time'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_match_multiple_classes_match_one(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p></body></html>'
        instructions = '.awesome'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_match_element_class(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p></body></html>'
        instructions = 'p.awesome'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_match_element_class_no_match(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p></body></html>'
        instructions = 'p.non'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_match_element_id_match(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p></body></html>'
        instructions = 'p.non'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_complex_match(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p></body></html>'
        instructions = 'body .awesome'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertTrue(xmlsrr.matchInstruction(element, instruction))

    def test_complex_no_match(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p></body></html>'
        instructions = 'body .non'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))

    def test_sibling_match(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling text</p></body></html>'
        instructions = 'p.sibling'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        self.assertFalse(xmlsrr.matchInstruction(element, instruction))


class TestGetInstructions(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()