# --------------- Scanner.py ---------------
# Interfaces with C++ dynamic library lib_token.so, using
# externally wrapped C++ functions to implement.
#
# Version:  Python 3.7
# Author:   Alex Hoke
# Date:		01/20/2021

from ctypes import *
from Core import Core
import sys

# Path constant for C++ dynamic library
cpp_lib_path = "./lib_token.so"


# Template format for expected struct specifying data typers
class LibScanStruct(Structure):
    _fields_ = [("token", c_char_p),
                ("attr", c_char_p),
                ("index", c_long)]


# Implementation of Scanner class
class Scanner:
    # Class member variables:
    #   c_lib     -     Loads dynamic C++ library
    #   __fp      -     Current index of input file
    #   __f_name  -     Private reference to file name
    #   token     -     Current token
    #   name      -     If current token has a value holds value, else None
    c_lib = CDLL(cpp_lib_path)
    __fp, __f_name, token, attr = 0, None, None, None
    # Sets expected return type from next_token function to the pre-declared
    # struct
    c_lib.next_token.restype = LibScanStruct

    # Constructor should open the file and find the first token
    def __init__(self, filename):
        # Save file name into memory and normalize string into utf-8
        Scanner.__f_name = bytes(filename, 'utf-8')
        # Return struct from external lib
        struct = self.c_lib.next_token(Scanner.__f_name, c_long(Scanner.__fp))
        # Decode return c_string to utf-8
        self.token, self.attr = Core[struct.token.decode('utf-8')], struct.attr.decode('utf-8')
        Scanner.__fp = struct.index

    # nextToken should advance the scanner to the next token
    def nextToken(self):
        struct = self.c_lib.next_token(Scanner.__f_name, c_long(Scanner.__fp))
        self.token, self.attr = Core[struct.token.decode('utf-8')], struct.attr.decode('utf-8')
        Scanner.__fp = struct.index

    # currentToken should return the current token
    def currentToken(self):
        return self.token

    # If the current token is ID, return the string value of the identifier
    # Otherwise, return value does not matter
    def getID(self):
        value = None
        if self.token == Core['ID']:
            value = self.attr
        return value

    # If the current token is CONST, return the numerical value of the constant
    # Otherwise, return value does not matter
    def getCONST(self):
        const = None
        if self.token == Core['CONST']:
            const = self.attr
        return const
