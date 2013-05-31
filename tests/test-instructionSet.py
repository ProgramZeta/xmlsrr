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

    def test_single_element(self):
        instruction = 'html'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(match['elements'][0], instruction)
        self.assertEqual(match['classes'], None)
        self.assertEqual(match['subMatch'], None)

    def test_single_class(self):
        instruction = '.class'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(match['classes'][0], 'class')
        self.assertEqual(match['elements'], None)

    def test_multiple_elements(self):
        instruction = 'html body'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(match['elements'][0], 'html')
        self.assertEqual(match['classes'], None)
        self.assertEqual(match['subMatch']['elements'][0], 'body')

    def test_three_elements(self):
        instruction = 'html body div'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(match['elements'][0], 'html')
        self.assertEqual(match['classes'], None)
        self.assertEqual(len(match['subMatch']['elements']), 1)
        self.assertEqual(match['subMatch']['elements'][0], 'body')
        self.assertEqual(match['subMatch']['classes'], None)
        self.assertEqual(match['subMatch']['subMatch']['elements'][0], 'div')
        self.assertEqual(match['subMatch']['subMatch']['classes'], None)

    def test_multiple_separate_classes(self):
        instruction = '.red .blue'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(match['elements'], None)
        self.assertEqual(match['classes'][0], 'red')
        self.assertEqual(match['subMatch']['elements'], None)
        self.assertEqual(match['subMatch']['classes'][0], 'blue')
        self.assertEqual(match['subMatch']['subMatch'], None)

    def test_multiple_conjoined_classes(self):
        instruction = '.red.blue'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(match['elements'], None)
        self.assertEqual('red', match['classes'][0])
        self.assertEqual('blue', match['classes'][1])
        self.assertEqual(None, match['subMatch'])

    def test_element_multiple_conjoined_classes(self):
        instruction = 'p.red.blue'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['elements']))
        self.assertEqual('p', match['elements'][0])
        self.assertEqual(2, len(match['classes']))
        self.assertEqual('red', match['classes'][0])
        self.assertEqual('blue', match['classes'][1])
        self.assertEqual(None, match['subMatch'])

    def test_element_with_class(self):
        instruction = 'p.blue'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual('p', match['elements'][0])
        self.assertEqual('blue', match['classes'][0])
        self.assertEqual(None, match['subMatch'])


class TestDetermineReplacement(unittest.TestCase):
    def test_single_replace(self):
        instruction = 'p.red -> p.blue'
        search, replace = instructionSet.determineReplacement(instruction)
        self.assertEqual(1, len(search['elements']))
        self.assertEqual(search['elements'][0], 'p')
        self.assertEqual(1, len(search['classes']))
        self.assertEqual(search['classes'][0], 'red')
        self.assertEqual(1, len(replace['elements']))
        self.assertEqual(replace['elements'][0], 'p')
        self.assertEqual(1, len(replace['classes']))
        self.assertEqual(replace['classes'][0], 'blue')

    def test_multiple_replace(self):
        instruction = 'p.red -> p.blue -> p.green'
        self.assertRaises(ValueError, instructionSet.determineReplacement, instruction)

    def test_invalid_replace_statement(self):
        instruction = 'p.red -> p.blue p.green'
        self.assertRaises(ValueError, instructionSet.determineReplacement, instruction)