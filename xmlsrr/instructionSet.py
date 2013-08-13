# coding=utf-8
import logging


class InstructionSet:
    """
    Get an instruction from a given string
    """

    def __init__(self, instruction=None):
        if instruction is not None:
            self.parseInstruction(instruction)

    def parseInstruction(self, instruction):
        self.mode = determineType(instruction)
        if self.mode == 'replace':
            self.match, self.replace = determineReplacement(instruction)
        elif self.mode == 'remove':
            self.match = determinePattern(instruction[1:])
        else:
            self.match = determinePattern(instruction)


def determineType(instruction):
    remove = False
    replace = False
    if instruction[0] == '/':
        remove = True
    if instruction.find('->') > 0:
        replace = True
    if remove and replace:
        raise ValueError
    elif remove:
        mode = 'remove'
    elif replace:
        mode = 'replace'
    else:
        mode = 'search'
    return mode


def determineReplacement(instruction):
    if len(instruction.split('->')) != 2:
        raise ValueError("Only one replacement per instruction")
    if len(instruction.split('->')[1].strip().split(' ')) > 1:
        raise ValueError("Replacement can only specify one match")
    search, replace = instruction.split('->')
    searchInstruction = determinePattern(search)
    replaceInstruction = determinePattern(replace)
    return searchInstruction, replaceInstruction


def determinePattern(instruction):
    if instruction.strip() == '':
        logging.error("Pattern does not contain any values: {0}".format(instruction))
        raise ValueError
    else:
        instruction = instruction.strip()
    match = {'elements': [], 'classes': [], 'ids': [], 'attributes': [], 'subMatch': None}
    currentType = 'element'
    currentAttribute = ''
    nextType = ''
    charCount = 0
    currentValue = ''
    for c in instruction:
        charCount += 1
        if currentType == 'attributeName':
            if c == '=':
                nextType = 'attributeValue'
            elif c == ']':
                nextType = 'element'
            else:
                currentValue += c
        elif currentType == 'attributeValue':
            if c == ']':
                nextType = 'element'
            else:
                currentValue += c
        else:
            if c == '.':
                nextType = 'class'
            elif c == '#':
                nextType = 'id'
            elif c == '[':
                nextType = 'attributeName'
            elif c == ' ':
                nextType = 'subMatch'
            else:
                currentValue += c

        if nextType != '':
            if currentValue != '':
                if currentType == 'element':
                    match['elements'].append(currentValue)
                if currentType == 'class':
                    match['classes'].append(currentValue)
                if currentType == 'id':
                    match['ids'].append(currentValue)
                if currentType == 'attributeName':
                    match['attributes'] = {currentValue: ''}
                    currentAttribute = currentValue
                if currentType == 'attributeValue':
                    match['attributes'][currentAttribute] = currentValue
                    currentAttribute = ''
                currentValue = ''
            else:
                if currentType == 'attributeName':
                    raise ValueError
            if nextType == 'subMatch':
                match['subMatch'] = InstructionSet(instruction[charCount:])
                break
            else:
                currentType = nextType
                currentValue = ''
                nextType = ''

    if currentValue != '':
        if currentType == 'element':
            match['elements'].append(currentValue)
        if currentType == 'class':
            match['classes'].append(currentValue)
        if currentType == 'id':
            match['ids'].append(currentValue)

    if match['elements'] == []:
        match['elements'] = None
    if match['classes'] == []:
        match['classes'] = None
    if match['ids'] == []:
        match['ids'] = None
    return match