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
    if len(instruction.split('->')[1].split(' ')) > 1:
        raise ValueError("Replacement can only specify one match")
    search, replace = instruction.split('->')
    searchInstruction = determinePattern(search)
    replaceInstruction = determinePattern(replace)


def determinePattern(instruction):
    if instruction.strip() == '':
        raise ValueError("Pattern does not contain any values")
    match = {}
    if instruction.find('.') >= 0:
        match['classes'] = [instruction[1:]]
        match['elements'] = []
    else:
        if len(instruction.split(' ')) > 1:
            match['elements'] = [instruction.split(' ')[0]]
            match['subMatch'] = determinePattern(instruction.split(' ')[1])
        else:
            match['elements'] = [instruction]
            match['subMatch'] = None
        match['classes'] = []
    return match