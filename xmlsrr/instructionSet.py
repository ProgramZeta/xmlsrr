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
    if len(instruction.split(' ')) > 1:
        match = determinePattern(instruction.split(' ', 1)[0])
        match['subMatch'] = determinePattern(instruction.split(' ', 1)[1])
    else:
        if instruction.find('.') >= 0:
            # Class in instruction
            if instruction[0] == '.':
                # Class is first instruction
                if instruction.count('.') == 1:
                    # Only one class
                    match['classes'] = [instruction[1:]]
                else:
                    # Multiple classes
                    match['classes'] = instruction[1:].split('.')
                match['elements'] = None
            else:
                match['elements'] = [instruction.split('.')[0]]
                match['classes'] = instruction.split('.')[1:]
        else:
            match['classes'] = None
            match['elements'] = [instruction]

        match['subMatch'] = None

    return match