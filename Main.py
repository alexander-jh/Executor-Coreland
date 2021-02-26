# --------------- Main.py ---------------
# Updated main function to launch parser,
# build tree, then execute the program.
#
# Version:  Python 3.7
# Author:   Alex Hoke
# Date:		02/26/2021

from Parser import Parser
import sys


def main():
    # Initializes the parser class
    parser = Parser(sys.argv[1])
    parser.build_tree()
    #parser.print_tree()
    parser.execute_tree(sys.argv[2])


if __name__ == '__main__':
    main()
