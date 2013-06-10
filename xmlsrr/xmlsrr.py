#!/usr/bin/python3
# coding=utf-8
"""
Search, remove, and replace content in a set of XML documents
"""
import argparse
import os
import sys
import logging
import shutil
from lxml import html
from lxml import etree
import instructionSet


def argumentParser():
    logging.debug("Parsing provided arguments")
    #if arguments is None or arguments == '':
    #    raise ValueError('Must provide at least one argument')
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
    return parser.parse_args()


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
        logging.debug("Instruction: {0}".format(instruction))
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
    logging.debug("Validating target folder: {0}".format(targetFolder))
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
    logging.debug("Validating output folder: {0}".format(outputDirectory))
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


def matchElement(element, instruction) -> bool:
    elementMatch = True
    if instruction.match['elements']:
        if element.tag not in instruction.match['elements']:
            elementMatch = False
    return elementMatch


def matchClass(element, instruction) -> bool:
    classMatch = True
    if instruction.match['classes']:
        for name in instruction.match['classes']:
            if classMatch:
                classMatch = False
                if element.get('class'):
                    for eachClass in element.get('class').split(' '):
                        if eachClass == name:
                            classMatch = True
    return classMatch


def matchId(element, instruction) -> bool:
    idMatch = True
    if instruction.match['ids']:
        if element.get('id') not in instruction.match['ids']:
            idMatch = False
    return idMatch


def matchAttribute(element, instruction) -> bool:
    attributeMatch = True
    if instruction.match['attributes']:
        for key, value in instruction.match['attributes'].items():
            if attributeMatch:
                attributeMatch = False
                if value:
                    if element.get(key) == value:
                        attributeMatch = True
                else:
                    if element.get(key):
                        attributeMatch = True
    return attributeMatch


def processInstructions(element, instruction):
    if matchElement(element, instruction) \
        and matchClass(element, instruction) \
        and matchId(element, instruction) \
        and matchAttribute(element, instruction):
        matchFound = True
    else:
        matchFound = False

    if not matchFound and len(element) > 0:
        [processInstructions(elem, instruction) for elem in element]
    if matchFound and not instruction.match['subMatch']:
        # Output we found a match
        if instruction.mode == 'search':
            # That's all we have to do for a search
            pass
        elif instruction.mode == 'remove':
            element.getparent().remove(element)
        elif instruction.mode == 'replace':
            # Replace the element with the new element
            newElement = element
            if instruction.match['elements']:
                newElement.tag = instruction.replace['elements'][0]
            if instruction.match['classes']:
                newElement.set('class', replaceClasses(newElement.get('class'), instruction))
            if instruction.match['ids']:
                newElement.set('id', instruction.replace['ids'][0])
            if instruction.match['attributes']:
                for key, value in instruction.match['attributes'].items():
                    if element.get(key):
                        if value == '' or (value != '' and element.attrib[key] == value):
                            element.attrib.pop(key)
            if instruction.replace['attributes']:
                for attribute in instruction.replace['attributes']:
                    for key, value in attribute:
                        element.set(key, value)

            element.getparent().replace(element, newElement)

    if matchFound and instruction.match['subMatch']:
        [processInstructions(elem, instruction.match['subMatch']) for elem in element]

    return element


def replaceClasses(classList, instruction):
    classes = classList.split(" ")
    if instruction.match['classes']:
        for name in classes:
            if name in instruction.match['classes']:
                classes.remove(name)
    if instruction.replace['classes']:
        for name in instruction.replace['classes']:
            if name not in classes:
                classes.append(name)
    return ' '.join(classes)


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
    logging.debug("Loading files from folder")
    fileList = []
    # For all files in the target folder
    for root, dirs, files in os.walk(targetFolder):
        # For each file
        for name in files:
            # If the file has '.htm' in the name (covers .htm and .html)
            if name.find('.htm') >= 0:
                logging.debug("Found htm/l file: {0}".format(os.path.join(root, name)))
                # Create the full targetFile path
                targetFile = os.path.join(root, name)
                # Remove the target directory prefix
                targetFile = targetFile.split(targetFolder)[1]
                # Append new file name to our list of files
                fileList.append(targetFile)
    logging.debug("Finished getting file list")
    return fileList


if __name__ == '__main__':
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s  %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug("Starting script")
    arguments = argumentParser()
    options = validateOptions(arguments)
    if options['instructionFile']:
        with open(options['instructionFile']) as f:
            logging.debug("Reading instruction file: {0}".format(options['instructionFile']))
            instructions = parseInstructions(f.readlines())
    else:
        instructions = parseInstructions(options['instructionList'])
    if options['verify']:
        sys.exit(0)
    if options['output']:
        logging.debug("Copying file tree in {0} to {1}".format(options['target'], options['output']))
        shutil.copytree(options['target'], options['output'])
        targetFolder = options['output']
    else:
        targetFolder = options['target']
    fileList = getFileList(targetFolder)
    for name in fileList:
        logging.debug("Processing file: {0}".format(targetFolder + name))
        element = html.parse(targetFolder + name).getroot()
        for instruction in instructions:
            processInstructions(element, instruction)
        with open(targetFolder + name, 'wb') as f:
            logging.debug("Writing file to {0}".format(targetFolder + name))
            f.write(etree.tostring(element))