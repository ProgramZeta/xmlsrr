import argparse
import os
import sys
import logging
from lxml import html
from xmlsrr import instructionSet


def main():
    logging.debug("Starting script")
    arguments = argumentParser(sys.argv)
    options = validateOptions(arguments)


def argumentParser(arguments):
    logging.debug("Parsing provided arguments")
    if arguments is None or arguments == '':
        raise ValueError('Must provide at least one argument')
    parser = argparse.ArgumentParser(description='Scans files in a folder to find matches, remove, \
    and/or replace elements based off of CSS-like syntax', prog='xmlsrr')
    parser.add_argument('target')
    parser.add_argument('-i', '--instructions')
    parser.add_argument('-l', '--log')
    parser.add_argument('-o', '--output')
    parser.add_argument('-V', '--verify', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--silent', action='store_true')
    group.add_argument('-v', '--verbose', action='count')
    return parser.parse_args(args=arguments)


def validateOptions(arguments):
    logging.debug("Validating option settings")
    options = {'verbosity': validateVerbosity(arguments.verbose, arguments.silent),
               'target': validateTarget(arguments.target, arguments.output)}
    try:
        options['instructionFile'] = validateInstructionFile(arguments.instructions)
    except ValueError:
        print("No instruction file provided, please provide search, remove, and replace instructions")
        options['instructionList'] = getInstructions()
    options['verify'] = arguments.verify
    return options


def parseInstructions(instructionList):
    logging.debug("Parsing instructions")
    instructions = []
    for instruction in instructionList:
        instructions.append(instructionSet.InstructionSet(instruction))
    return instructions


def validateInstructionFile(instructionFile):
    logging.debug("Validating instruction file exists")
    if instructionFile is None:
        raise ValueError("No instruction file provided")
    if os.access(instructionFile, os.F_OK):
        if os.access(instructionFile, os.R_OK):
            return instructionFile
        else:
            raise PermissionError("Unable to read from instruction file {0}".format(instructionFile))
    else:
        raise FileNotFoundError("Did not fine instruction file {0}".format(instructionFile))


def validateVerbosity(verbosity, silent):
    logging.debug("Validating silent/verbose statements")
    if silent:
        return None
    else:
        if verbosity == 0 or verbosity is None:
            return logging.WARNING
        elif verbosity == 1:
            return logging.INFO
        elif verbosity >= 2:
            return logging.DEBUG


def validateTarget(targetFolder, outputFolder):
    logging.debug("Validating target folder")
    if os.access(targetFolder, os.F_OK):
        if targetFolder == outputFolder or outputFolder is None:
            if os.access(targetFolder, os.R_OK):
                return targetFolder
            else:
                raise PermissionError
        else:
            if os.access(targetFolder, os.W_OK):
                return targetFolder
            else:
                raise PermissionError
    else:
        raise NotADirectoryError


def validateOutput(outputDirectory):
    logging.debug("Validating output folder")
    if os.access(outputDirectory, os.F_OK):
        if os.access(outputDirectory, os.W_OK):
            return outputDirectory
        else:
            raise PermissionError
    else:
        raise NotADirectoryError


def validateLog(logFile):
    logging.debug("Validating log file")
    if os.access(logFile, os.F_OK):
        if os.access(logFile, os.W_OK):
            return logFile
        else:
            raise PermissionError("Unable to write to log file {0}".format(logFile))
    else:
        raise FileNotFoundError("Log File")


def validateInstructionsExist(instructionsList):
    logging.debug("Validating provided instructions aren't empty lines")
    instructions = []
    if instructionsList == [] or instructionsList is None:
        raise ValueError("No instructions found")
    for instruction in instructionsList:
        if instruction.strip() == '':
            pass
        else:
            instructions.append(instruction)
    if not instructions:
        raise ValueError("No instructions found")
    return instructions


def getListOfFiles(targetFolder):
    logging.debug("Getting list of files from target folder")
    fileList = []
    for root, dirs, files in os.walk(targetFolder):
        for name in files:
            if name.find('.htm') > 0:
                fileList.append(os.path.join(root, name))
    return fileList


def scanFile(fileName, instructions):
    element = html.parse(fileName).getRoot()
    for instruction in instructions:
        matchInstruction(element, instruction)


def matchInstruction(element, instruction):
    elementMatch = False
    classMatch = False
    idMatch = False
    attributeMatch = False
    matchFound = False
    if instruction.match['elements']:
        if element.tag in instruction.match['elements']:
            elementMatch = True
        else:
            elementMatch = False
    else:
        elementMatch = True
    if instruction.match['classes']:
        # See if we need to match against classes
        classMatch = True
        for className in instruction.match['classes']:
            # For each class we need to match
            if classMatch:
                classMatch = False
                if element.get('class'):
                    for eachClass in element.get('class').split(' '):
                        if eachClass == className:
                            classMatch = True
    else:
        classMatch = True
    if instruction.match['ids']:
        if element.get('id') in instruction.match['ids']:
            idMatch = True
        else:
            idMatch = False
    else:
        idMatch = True

    if instruction.match['attributes']:
        attributeMatch = True
        for key, value in instruction.match['attributes'].items():
            if attributeMatch:
                attributeMatch = False
                if value:
                    if element.get(key) == value:
                        attributeMatch = True
                else:
                    if element.get(key):
                        attributeMatch = True
    else:
        attributeMatch = True

    if elementMatch and classMatch and idMatch and attributeMatch:
        matchFound = True

    if not matchFound and len(element) > 0:
        matchFound = matchInstruction(element[0], instruction)
    if matchFound and instruction.match['subMatch']:
        matchFound = matchInstruction(element, instruction.match['subMatch'])
    return matchFound


def getInstructions():
    logging.debug("Getting list of instructions from user input")
    instructionList = []
    while True:
        newInstruction = input('Instruction: ')
        if newInstruction == '':
            break
        else:
            instructionList.append(newInstruction)
    try:
        instructionList = validateInstructionsExist(instructionList)
    except ValueError:
        print("No valid instructions provided")
        sys.exit(1)
    return instructionList


if __name__ == '__main__':
    main()