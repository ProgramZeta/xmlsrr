import argparse

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

def validateTarget(targetFolder):
    pass

if __name__ == '__main__':
    main()