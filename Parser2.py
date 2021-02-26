# --------------- self.py ---------------
# Top down recursive descent parser implementation.
#
# Version:  Python 3.7
# Author:   Alex Hoke
# Date:		02/06/2021

from Core import Core as Token
from Scanner import Scanner
import sys


class Counter:
    new_line = False
    indent_level = 0


class Parser:
    # Sets containing print expectations
    NEW_LINE_TOKEN = {Token.PROGRAM.name, Token.BEGIN.name, Token.END.name,
                      Token.SEMICOLON.name, Token.ENDIF.name, Token.ENDWHILE.name,
                      Token.THEN.name, Token.ELSE.name}
    NO_SPACE_TOKEN = {Token.ID.name, Token.CONST.name, Token.ASSIGN.name,
                      Token.LPAREN.name, Token.RPAREN.name, Token.MULT.name,
                      Token.ADD.name, Token.SUB.name, Token.COMMA.name,
                      Token.LESS.name, Token.LESSEQUAL.name, Token.EQUAL.name,
                      Token.NEGATION.name}
    STM_INIT_TOKEN = {Token.ID.name, Token.IF.name, Token.ELSE.name, Token.WHILE.name,
                      Token.BEGIN.name, Token.INPUT.name, Token.OUTPUT.name,
                      Token.INT.name}
    counter = Counter

    # Default constructor
    def __init__(self):
        self.scanner = Scanner(sys.argv[1])
        self.scope = dict()
        self.first_begin = False

    # Accesses present token
    def token(self):
        return self.scanner.currentToken()

    # Get current token ID
    def get_id(self):
        return self.scanner.getID()

    # Get current token CONST
    def get_const(self):
        return self.scanner.getCONST()

    # Increments to the next token
    def next_token(self):
        self.scanner.nextToken()

    # Adjusts spacing based on scope
    def new_line_format(self):
        if self.counter.new_line and self.token().name not in {Token.BEGIN.name, Token.END.name}:
            if self.token().name in {Token.ELSE.name, Token.ENDIF.name, Token.ENDWHILE.name}:
                self.counter.indent_level -= 1
            for i in range(self.counter.indent_level):
                print(end='\t')

    # Prints the token and its correct formatting
    def print_token(self):
        self.new_line_format()
        if self.token().name in self.NEW_LINE_TOKEN:
            if self.token().name == Token.BEGIN.name and self.first_begin:
                print(end=' ')
            print(self.token().value, end='\n')
            self.counter.new_line = True
        else:
            self.counter.new_line = False
            if self.token().name in self.NO_SPACE_TOKEN:
                if self.token().name == Token.ID.name or self.token().name == Token.CONST.name:
                    self.print_const_id()
                else:
                    print(self.token().value, end='')
            else:
                print(self.token().value, end=' ')

    def print_const_id(self):
        if self.token().name == Token.ID.name:
            print(self.get_id(), end='')
        else:
            print(self.get_const(), end='')

    # Validates a token without consuming it
    def token_validate(self, expected):
        if self.token().name != expected.name:
            sys.exit(f'\nERROR: Token {self.token().name} was invalidly placed, expected {expected.name}')

    # Consumes a token after validating it
    def token_assert(self, expected):
        self.token_validate(expected)
        self.print_token()
        self.next_token()

    # Beings the parse sequence and descent
    def parse(self):
        self.counter.indent_level = 1
        self.token_assert(Token.PROGRAM)
        if self.token().name == Token.INT.name:
            self.decl_seq_parse()
        self.token_assert(Token.BEGIN)
        self.counter.indent_level = 1
        self.first_begin = True
        self.stmt_seq_parse()
        self.counter.indent_level = 0
        self.token_assert(Token.END, self.nodes)
        if self.token().name != Token.ERROR.name:
            sys.exit(f'\nERROR: Declarations following end statement.\n')

    # Validates the declaration does not already exist
    def validate_decl(self):
        if self.get_id() in self.scope:
            sys.exit(f'\nERROR: Variable {self.get_id()} was declared multiple times.')

    # Verifies if ID has been instantiated at scope
    def validate_instance(self):
        if self.get_id() not in self.scope:
            sys.exit(f'\nERROR: Variable {self.get_id()} not instantiated at scope')
        tid = self.get_id()
        self.token_assert(Token.ID)
        return tid

    # Adds declaration to variable scope
    def decl_to_scope(self):
        self.validate_decl()
        tid = self.get_id()
        self.scope.update({tid: False})
        self.print_token()
        self.next_token()
        return tid

    def decl_seq_parse(self):
        # Check for first declaration INT
        self.decl_parse()
        # Decl-seq is only called from program so it only will terminate on
        # begin or invalid input
        if self.token().name != Token.BEGIN.name:
            self.decl_seq_parse()

    def decl_parse(self, _local=None):
        if _local is None:
            _local = set()
        self.token_assert(Token.INT)
        self.token_validate(Token.ID)
        _local = self.id_list_parse(_local)
        self.token_assert(Token.SEMICOLON)
        # Returns variables declared to caller superclass
        return _local

    def id_list_parse(self, _local):
        if self.token().name == Token.COMMA.name:
            self.token_assert(Token.COMMA)
            self.id_list_parse(_local)
        elif self.token().name == Token.ID.name:
            # Insert first id into local scope
            self.token_validate(Token.ID)
            _local.add(self.decl_to_scope())
            self.id_list_parse(_local)
        return _local

    def stmt_seq_parse(self, _local=None):
        if _local is None:
            _local = set()
        if self.token().name != Token.END.name:
            self.stmt_parse(_local)
            if self.token().name in self.STM_INIT_TOKEN:
                self.stmt_seq_parse(_local)

    def stmt_parse(self, _local=None):
        if _local is None:
            _local = set()
        if self.token().name == Token.ID.name:
            self.assign_parse()
        elif self.token().name == Token.IF.name or self.token().name == Token.ELSE.name \
                or self.token().name == Token.ENDIF.name:
            if_scope = set()
            self.if_seq_parse(if_scope)
            for i in if_scope:
                self.scope.pop(i)
        elif self.token().name == Token.WHILE.name:
            loop_scope = set()
            self.loop_parse(loop_scope)
            for i in loop_scope:
                self.scope.pop(i)
        elif self.token().name == Token.INPUT.name:
            self.input_parse()
        elif self.token().name == Token.OUTPUT.name:
            self.output_parse()
        elif self.token().name == Token.INT.name:
            self.decl_parse(_local)

    def input_parse(self):
        # self.validate_instance()
        self.token_assert(Token.INPUT)
        self.validate_instance()
        self.token_assert(Token.SEMICOLON)

    def output_parse(self):
        self.token_assert(Token.OUTPUT)
        self.expr_parse()
        self.token_assert(Token.SEMICOLON)

    def cond_parse(self):
        if self.token().name == Token.NEGATION.name:
            self.token_assert(Token.NEGATION)
            self.cond_paren_parse()
        elif self.token().name == Token.OR.name:
            self.token_assert(Token.OR)
            self.cond_parse()
        else:
            self.cmpr_parse()

    def cmpr_parse(self):
        self.expr_parse()
        if self.token().name == Token.EQUAL.name:
            self.token_assert(Token.EQUAL)
        elif self.token().name == Token.LESS.name:
            self.token_assert(Token.LESS)
        else:
            self.token_assert(Token.LESSEQUAL)
        self.expr_parse()

    def expr_parse(self):
        self.term_parse()
        if self.token().name == Token.ADD.name:
            self.token_assert(Token.ADD)
            self.expr_parse()
        elif self.token().name == Token.SUB.name:
            self.token_assert(Token.SUB)
            self.expr_parse()

    def factor_parse(self):
        if self.token().name == Token.ID.name:
            self.validate_instance()
        elif self.token().name == Token.CONST.name:
            self.token_assert(Token.CONST)
        else:
            self.expr_paren_parse()

    def assign_parse(self):
        read_id = self.validate_instance()
        self.scope[read_id] = True
        self.token_assert(Token.ASSIGN)
        self.expr_parse()
        self.token_assert(Token.SEMICOLON)

    def term_parse(self):
        self.factor_parse()
        if self.token().name == Token.MULT.name:
            self.token_assert(Token.MULT)
            self.term_parse()

    def if_seq_parse(self, _local):
        if self.token().name == Token.IF.name:
            self.token_assert(Token.IF)
            self.counter.indent_level += 1
            self.cond_parse()
            self.token_assert(Token.THEN)
            self.stmt_seq_parse()
        elif self.token().name == Token.ELSE.name:
            self.token_assert(Token.ELSE)
            self.counter.indent_level += 1
            self.stmt_seq_parse()
            return
        self.token_assert(Token.ENDIF)
        # Remove variables from scope that were in the block
        # self.scope.pop(k for k in _local.keys())

    def loop_parse(self, _local):
        if self.token().name == Token.WHILE.name:
            self.token_assert(Token.WHILE)
            self.counter.indent_level += 1
            self.cond_parse()
            self.token_assert(Token.BEGIN)
            self.stmt_seq_parse(_local)
            self.token_assert(Token.ENDWHILE)
            # self.scope.pop(k for k in _local.keys())

    def cond_paren_parse(self):
        self.token_assert(Token.LPAREN)
        self.cond_parse()
        if self.token().name == Token.LPAREN.name:
            self.cond_paren_parse()
        self.token_assert(Token.RPAREN)

    def expr_paren_parse(self):
        self.token_assert(Token.LPAREN)
        self.expr_parse()
        if self.token().name == Token.LPAREN.name:
            self.expr_paren_parse()
        self.token_assert(Token.RPAREN)
