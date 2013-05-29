import argparse
import sys

def main():
    pass

def argument_parser(arguments):
    if arguments == None or arguments == "":
        raise ValueError('Must provide at least one argument')
    parser = argparse.ArgumentParser(description='Scans files in a folder to find matches, remove, \
    and/or replace elements based off of CSS-like syntax')
    parser.add_argument('target', type=str)
    return parser.parse_args(args=arguments.split())


if __name__ == "__main___":
    main()