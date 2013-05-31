class InstructionSet(object):
    def __init__(self, instruction=None):
        if instruction is not None:
            self.parseInstruction(instruction)

    def parseInstruction(self, instruction):
        """
        * determine if we have a removal: check first character for '/'
        * determine if we have a replacement: separate on '->'
        * separate on commas to break apart multiple selectors
        """
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
    pass

def determineMultipleInstructions(instruction):
    pass

def determineElements(instruction):
    pass

def determineClasses(instruction):
    pass

def determineIds(instruction):
    pass

def determineAttributes(instruction):
    pass