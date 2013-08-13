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


class TestParseInstruction(unittest.TestCase):
    def test_search_pattern(self):
        pattern = 'p.red'
        instruction = instructionSet.InstructionSet(pattern)
        self.assertEqual('search', instruction.mode)

    def test_remove_pattern(self):
        pattern = '/p.red'
        instruction = instructionSet.InstructionSet(pattern)
        self.assertEqual('remove', instruction.mode)

    def test_replace_pattern(self):
        pattern = 'p.red -> p.blue'
        instruction = instructionSet.InstructionSet(pattern)
        self.assertEqual('replace', instruction.mode)


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
        self.assertEqual(1, len(match['elements']))
        self.assertEqual('html', match['elements'][0])
        self.assertEqual(None, match['classes'])
        self.assertEqual(None, match['subMatch'])

    def test_element_trailing_space(self):
        instruction = 'html     '
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['elements']))
        self.assertEqual('html', match['elements'][0])
        self.assertEqual(None, match['classes'])
        self.assertEqual(None, match['subMatch'])

    def test_single_class(self):
        instruction = '.class'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['classes']))
        self.assertEqual('class', match['classes'][0])
        self.assertEqual(None, match['elements'])

    def test_multiple_elements(self):
        instruction = 'html body'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['elements']))
        self.assertEqual('html', match['elements'][0])
        self.assertEqual(None, match['classes'])
        self.assertEqual(1, len(match['subMatch'].match['elements']))
        self.assertEqual(match['subMatch'].match['elements'][0], 'body')

    def test_three_elements(self):
        instruction = 'html body div'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(len(match['elements']), 1)
        self.assertEqual(match['elements'][0], 'html')
        self.assertEqual(match['classes'], None)
        self.assertEqual(len(match['subMatch'].match['elements']), 1)
        self.assertEqual(match['subMatch'].match['elements'][0], 'body')
        self.assertEqual(match['subMatch'].match['classes'], None)
        self.assertEqual(match['subMatch'].match['subMatch'].match['elements'][0], 'div')
        self.assertEqual(match['subMatch'].match['subMatch'].match['classes'], None)

    def test_multiple_separate_classes(self):
        instruction = '.red .blue'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(match['elements'], None)
        self.assertEqual(match['classes'][0], 'red')
        self.assertEqual(match['subMatch'].match['elements'], None)
        self.assertEqual(match['subMatch'].match['classes'][0], 'blue')
        self.assertEqual(match['subMatch'].match['subMatch'], None)

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
        self.assertEqual(len(match['elements']), 1)
        self.assertEqual('p', match['elements'][0])
        self.assertEqual(len(match['classes']), 1)
        self.assertEqual('blue', match['classes'][0])
        self.assertEqual(None, match['subMatch'])

    def test_single_id(self):
        instruction = '#id'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(None, match['elements'])
        self.assertEqual(None, match['classes'])
        self.assertEqual(1, len(match['ids']))
        self.assertEqual('id', match['ids'][0])

    def test_element_with_id(self):
        instruction = 'p#id'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['elements']))
        self.assertEqual('p', match['elements'][0])
        self.assertEqual(None, match['classes'])
        self.assertEqual(1, len(match['ids']))
        self.assertEqual('id', match['ids'][0])

    def test_element_with_class_and_id(self):
        instruction = 'p.class#id'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['elements']))
        self.assertEqual('p', match['elements'][0])
        self.assertEqual(1, len(match['classes']))
        self.assertEqual('class', match['classes'][0])
        self.assertEqual(1, len(match['ids']))
        self.assertEqual('id', match['ids'][0])

    def test_element_with_id_and_class(self):
        instruction = 'p#id.class'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['elements']))
        self.assertEqual('p', match['elements'][0])
        self.assertEqual(1, len(match['classes']))
        self.assertEqual('class', match['classes'][0])
        self.assertEqual(1, len(match['ids']))
        self.assertEqual('id', match['ids'][0])

    def test_separate_class_element_id(self):
        instruction = '.class p #id'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(1, len(match['classes']))
        self.assertEqual('class', match['classes'][0])
        self.assertEqual(1, len(match['subMatch'].match['elements']))
        self.assertEqual('p', match['subMatch'].match['elements'][0])
        self.assertEqual(1, len(match['subMatch'].match['subMatch'].match['ids']))
        self.assertEqual('id', match['subMatch'].match['subMatch'].match['ids'][0])

    def test_single_attribute(self):
        instruction = '[src]'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(None, match['elements'])
        self.assertEqual(None, match['classes'])
        self.assertEqual(None, match['ids'])
        self.assertEqual(1, len(match['attributes']))
        self.assertIn('src', match['attributes'])
        self.assertEqual(None, match['subMatch'])

    def test_single_attribute_with_value(self):
        instruction = '[lang=en-us]'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(None, match['elements'])
        self.assertEqual(None, match['classes'])
        self.assertEqual(None, match['ids'])
        self.assertEqual(1, len(match['attributes']))
        self.assertIn('lang', match['attributes'])
        self.assertEqual('en-us', match['attributes']['lang'])
        self.assertEqual(None, match['subMatch'])

    def test_single_attribute_with_path_value(self):
        instruction = '[src=/bbbb.jpg]'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(None, match['elements'])
        self.assertEqual(None, match['classes'])
        self.assertEqual(None, match['ids'])
        self.assertEqual(1, len(match['attributes']))
        self.assertIn('src', match['attributes'])
        self.assertEqual('/bbbb.jpg', match['attributes']['src'])
        self.assertEqual(None, match['subMatch'])

    def test_attribute_value_set_before_name(self):
        instruction = '[=aaa]'
        self.assertRaises(ValueError, instructionSet.determinePattern, instruction)

    def test_attribute_value_has_spaces(self):
        instruction = '[style=font-weight: bold;]'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(None, match['elements'])
        self.assertEqual(None, match['classes'])
        self.assertEqual(None, match['ids'])
        self.assertEqual(1, len(match['attributes']))
        self.assertIn('style', match['attributes'])
        self.assertEqual('font-weight: bold;', match['attributes']['style'])
        self.assertEqual(None, match['subMatch'])

    def test_attribute_value_has_multiple_spaces(self):
        instruction = '[style=text-indent:0px; margin-left: 23px;list-style-position:outside;]'
        match = instructionSet.determinePattern(instruction)
        self.assertEqual(None, match['elements'])
        self.assertEqual(None, match['classes'])
        self.assertEqual(None, match['ids'])
        self.assertEqual(1, len(match['attributes']))
        self.assertIn('style', match['attributes'])
        self.assertEqual('text-indent:0px; margin-left: 23px;list-style-position:outside;',
                         match['attributes']['style'])
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


if __name__ == "__main__":
    unittest.main()