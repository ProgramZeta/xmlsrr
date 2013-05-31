import unittest
from xmlsrr import instructionSet

class TestDetermineType(unittest.TestCase):
    def test_search_string(self):
        instruction = 'html'
        mode = instructionSet.determineType(instruction)
        self.assertEqual(mode, 'search')

    def test_remove_string(self):
        instruction = '/img'
        mode = instructionSet.determineType(instruction)
        self.assertEqual(mode, 'remove')

    def test_replace_string(self):
        instruction = 'p.red -> p.blue'
        mode = instructionSet.determineType(instruction)
        self.assertEqual(mode, 'replace')

    def test_remove_replace_error(self):
        instruction = '/p.red -> p.blue'
        self.assertRaises(ValueError, instructionSet.determineType, instruction)

class TestDeterminePattern(unittest.TestCase):
    def test_empty_pattern(self):
        instruction = ''
        self.assertRaises(ValueError, instructionSet.determinePattern, instruction)

    def test_single_space_pattern(self):
        instruction = ' '
        self.assertRaises(ValueError, instructionSet.determinePattern, instruction)

class TestDetermineReplacement(unittest.TestCase):
    def test_single_replace(self):
        instruction = 'p.red -> p.blue'

    def test_multiple_replace(self):
        instruction = 'p.red -> p.blue -> p.green'
        self.assertRaises(ValueError, instructionSet.determineReplacement, instruction)

    def test_invalid_replace_statement(self):
        instruction = 'p.red -> p.blue p.green'
        self.assertRaises(ValueError, instructionSet.determineReplacement, instruction)