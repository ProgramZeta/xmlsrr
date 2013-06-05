import argparse
import os
import sys
import logging
import shutil
from lxml import html
from lxml import etree
from xmlsrr import instructionSet


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
        options['output'] = validateOutput(arguments.output)
    except NotADirectoryError:
        options['output'] = None
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


def matchElement(element, elements):
    if element.tag in elements:
        return True
    else:
        return False


def matchClass(element, classes):
    classMatch = True
    for name in classes:
        if classMatch:
            classMatch = False
            if element.get('class'):
                for eachClass in element.get('class').split(' '):
                    if eachClass == name:
                        classMatch = True
    return classMatch


def matchId(element, ids):
    if element.get('id') in ids:
        return True
    else:
        return False


def processInstructions(element, instruction):
    if instruction.match['elements']:
        elementMatch = matchElement(element, instruction.match['elements'])
    else:
        elementMatch = True

    if instruction.match['classes']:
        classMatch = matchClass(element, instruction.match['classes'])
    else:
        classMatch = True

    if instruction.match['ids']:
        idMatch = matchId(element, instruction.match['ids'])
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
    else:
        matchFound = False

    if not matchFound and len(element) > 0:
        for subElement in element:
            matchFound = processInstructions(subElement, instruction)
    if matchFound and instruction.match['subMatch']:
        for subElement in element:
            matchFound = processInstructions(subElement, instruction.match['subMatch'])

    if matchFound:
        if instruction.mode == 'search':
            pass
        elif instruction.mode == 'remove':
            pass
        elif instruction.mode == 'replace':
            pass
        return True
    else:
        return False


def removeElement(element, instruction):
    return element


def replaceElement(element, instruction):
    return element


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


def getFileList(targetFolder):
    fileList = []
    # For all files in the target folder
    for root, dirs, files in os.walk(targetFolder):
        # For each file
        for name in files:
            # If the file has '.htm' in the name (covers .htm and .html)
            if name.find('.htm') >= 0:
                # Create the full targetFile path
                targetFile = os.path.join(root, files)
                # Remove the target directory prefix
                targetFile = targetFile.split(targetFolder)[1]
                # Append new file name to our list of files
                fileList.append(targetFile)
    return fileList


if __name__ == '__main__':
    logging.debug("Starting script")
    arguments = argumentParser(sys.argv)
    options = validateOptions(arguments)
    if options['instructionFile']:
        with open(options['instructionFile']) as f:
            instructions = parseInstructions(f.read())
    else:
        instructions = parseInstructions(options['instructionList'])
    if options['verify'] == True:
        sys.exit(0)
    if options['output']:
        shutil.copytree(options['target'], options['output'])
        targetFolder = options['output']
    else:
        targetFolder = options['target']
    fileList = getFileList(targetFolder)
    for name in fileList:
        element = html.parse(name).getroot()
        for instruction in instructions:
            if instruction.mode == 'search':
                pass
            elif instruction.mode == 'remove':
                pass
            elif instruction.mode == 'replace':
                pass
            else:
                raise ValueError("Invalid instruction mode")
        with open(name, 'rwb') as f:
            f.write(etree.tostring(element))