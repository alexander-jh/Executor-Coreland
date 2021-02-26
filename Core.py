# --------------- Core.py ---------------
# Supplied enum library for Scanner.py
#
# Version:  Python 3.8
# Author:   Alex Hoke
# Date:		01/20/2021

from enum import Enum


class Core(Enum):
    PROGRAM = 'program'
    BEGIN = 'begin'
    END = 'end'
    NEW = 'new'
    DEFINE = 'define'
    EXTENDS = 'extends'
    CLASS = 'class'
    ENDCLASS = 'endclass'
    INT = 'int'
    ENDFUNC = 'endfunc'
    IF = 'if'
    THEN = ' then'
    ELSE = 'else'
    WHILE = 'while'
    ENDWHILE = 'endwhile'
    ENDIF = 'endif'
    SEMICOLON = ';'
    LPAREN = '('
    RPAREN = ')'
    COMMA = ','
    ASSIGN = '='
    NEGATION = '!'
    OR = 'or'
    EQUAL = '=='
    LESS = '<'
    LESSEQUAL = '<='
    ADD = '+'
    SUB = '-'
    MULT = '*'
    INPUT = 'input'
    OUTPUT = 'output'
    CONST = 'const'
    ID = 'id'
    EOF = 'eof'
    ERROR = 'error'

