import argparse
import os


def main():
    pass


def argumentParser(arguments):
    if arguments == None or arguments == '':
        raise ValueError('Must provide at least one argument')
    parser = argparse.ArgumentParser(description='Scans files in a folder to find matches, remove, \
    and/or replace elements based off of CSS-like syntax', prog='xmlsrr')
    parser.add_argument('target', type=str)
    parser.add_argument('-i', '--instructions')
    parser.add_argument('-l', '--log')
    parser.add_argument('-o', '--output')
    parser.add_argument('-s', '--silent', action='store_true')
    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('-V', '--verify', action='store_true')
    return parser.parse_args(args=arguments.split())


def validateTarget(targetFolder, read_only=True):
    if os.access(targetFolder, os.F_OK):
        if read_only:
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


def validateInstructions(instructionsList):
    instructions = []
    if instructionsList == [] or instructionsList == None:
        raise ValueError
    for instruction in instructionsList:
        if instruction == '':
            pass
        else:
            instructions.append(instruction)
    if instructions == []:
        raise ValueError
    return instructions

if __name__ == '__main__':
    main()