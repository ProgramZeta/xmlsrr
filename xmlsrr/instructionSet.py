class InstructionSet(object):
    def __init__(self, instruction=None):
        if instruction is not None:
            self.parseInstruction(instruction)

    def parseInstruction(self, instruction):
        self.mode = determineType(instruction)


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
            mode= 'replace'
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
        raise ValueError("Pattern does not contain any values")
    else:
        instruction = instruction.strip()
    match = {}
    match['elements'] = []
    match['classes'] = []
    match['ids'] = []
    match['attributes'] = []
    if len(instruction.split(' ')) > 1:
        match = determinePattern(instruction.split(' ', 1)[0])
        match['subMatch'] = determinePattern(instruction.split(' ', 1)[1])
    else:
        currentType = 'element'
        currentName = ''
        currentAttribute = ''
        for c in instruction:
            if c in '.#[=]':
                if currentName != '':
                    if currentType == 'element':
                        match['elements'].append(currentName)
                    elif currentType == 'class':
                        match['classes'].append(currentName)
                    elif currentType == 'id':
                        match['ids'].append(currentName)
                    elif currentType == 'attributeName':
                        match['attributes'] = {currentName : ''}
                        currentAttribute = currentName
                    elif currentType == 'attributeValue':
                        if currentAttribute != '':
                            match['attributes'][currentAttribute] = currentName
                        else:
                            raise ValueError('Attribute value set before attribute name')
                    currentName = ''

                if c == '.':
                    currentType = 'class'
                elif c == '#':
                    currentType = 'id'
                elif c == '[':
                    currentType = 'attributeName'
                else:
                    if currentType == 'attributeName' or currentType == 'attributeValue':
                        if c == ']':
                            pass
                        elif c == '=':
                            currentType = 'attributeValue'
            else:
                currentName = currentName + c

        if currentName != '':
            if currentType == 'element':
                match['elements'].append(currentName)
            elif currentType == 'class':
                match['classes'].append(currentName)
            elif currentType == 'id':
                match['ids'].append(currentName)
            elif currentType == 'attributeName':
                match['attributes'] = {currentName : ''}
            elif currentType == 'attributeValue':
                if currentAttribute != '':
                    match['attributes'][currentAttribute] = currentName
                else:
                    raise ValueError('Attribute value set before attribute name')

        if match['elements'] == []:
            match['elements'] = None

        if match['classes'] == []:
            match['classes'] = None

        if match['ids'] == []:
            match['ids'] = None

        if match['attributes'] == []:
            match['attributes'] = None

        match['subMatch'] = None

    return match