# coding=utf-8
import unittest
import sys
from io import StringIO
import os
from lxml import html
from lxml import etree
import xmlsrr
import instructionSet


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


class TestProcessInstructions(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_stdout

    def test_no_changes(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling <em>text</em></p></body></html>'
        resultText = b'<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling <em>text</em></p></body></html>'
        instructions = '/div'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))

    def test_remove_element(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling <em>text</em></p></body></html>'
        resultText = b'<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling </p></body></html>'
        instructions = '/em'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))

    def test_remove_class(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling <em>text</em></p></body></html>'
        resultText = b'<html><body><p class="sibling">sibling <em>text</em></p></body></html>'
        instructions = '/.awesome'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))

    def test_remove_id(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling <em>text</em></p></body></html>'
        resultText = b'<html><body><p class="sibling">sibling <em>text</em></p></body></html>'
        instructions = '/#someName'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))

    def test_remove_attribute_add_class(self):
        htmlText = '<html><body><p id="someName" style="text-indent:0px; margin-left: 26px;list-style-position:outside;" class="awesome time">Some Text</p><p class="sibling">sibling <em>text</em></p></body></html>'
        resultText = b'<html><body><p id="someName" class="awesome time listIndent1">Some Text</p><p class="sibling">sibling <em>text</em></p></body></html>'
        instructions = '[style=text-indent:0px; margin-left: 26px;list-style-position:outside;] -> .listIndent1'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))


    def test_replace_element(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling text</p></body></html>'
        resultText = b'<html><body><div id="someName" class="awesome time">Some Text</div><div class="sibling">sibling text</div></body></html>'
        instructions = 'p -> div'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))

    def test_replace_id_remove_class(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling text</p></body></html>'
        resultText = b'<html><body><p id="someOtherName" class="time">Some Text</p><p class="sibling">sibling text</p></body></html>'
        instructions = 'p#someName.awesome -> p#someOtherName'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))


    def test_replace_id_and_class(self):
        htmlText = '<html><body><p id="someName" class="awesome time">Some Text</p><p class="sibling">sibling text</p></body></html>'
        resultText = b'<html><body><p id="someOtherName" class="time blah">Some Text</p><p class="sibling">sibling text</p></body></html>'
        instructions = 'p#someName.awesome -> p#someOtherName.blah'
        element = html.fromstring(htmlText)
        instruction = instructionSet.InstructionSet(instructions)
        result = xmlsrr.processInstructions(element, instruction)
        self.assertEqual(resultText, etree.tostring(result))


if __name__ == "__main__":
    unittest.main()