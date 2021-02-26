# --------------- Parser.py ---------------
# Top down recursive descent parser implementation.
# Modified from previous version to include the executor
# functionality built into each sub-class of
# parser instructions.
#
# Version:  Python 3.7
# Author:   Alex Hoke
# Date:		02/26/2021

from Core import Core as Token
from Scanner import Scanner
import sys


class Parser:

    # Default constructor
    #   scanner         -   holds scanner object
    #   tree            -   parse tree representation through program.nodes
    #   global_scope    -   root of the present scope of the tree
    #   data            -   holds queue from user data file
    def __init__(self, f_name):
        self.scanner = Scanner(f_name)
        self.tree = Program()
        self.global_scope = scope_tree()
        self.data = None

    # Constructs the parse tree and runs semantic checks
    def build_tree(self):
        self.tree.parse(self)
        self.tree.semantics(self)

    # Prints the token and its correct formatting
    def print_tree(self):
        self.tree.print()

    # Starts the executor
    def execute_tree(self, f_name):
        # Read data and reset global scope
        self.data = Parser.clean_data(f_name)
        self.global_scope = scope_tree()
        self.tree.execute(self)

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

    # Validates a token without consuming it
    def token_validate(self, expected):
        if self.token() != expected:
            sys.exit(f'\nERROR: Token {self.token().name} was invalidly placed, expected {expected.name}')

    # Consumes a token after validating it, additionally add the node
    # to the parse tree
    #   expected            -   expected Token enum reference
    #   nodes               -   reference to the calling parsing class
    def token_assert(self, expected, nodes):
        self.token_validate(expected)
        nodes.append(expected)
        self.next_token()

    @staticmethod
    # DFS search of the present nested scopes. Starts from root
    # and works down the tree returning the deepest element which
    # contains the variable of interest. Else returns None.
    #   tree    -   root of parse tree
    #   var     -   id to query
    def dfs_scope(tree, var):
        sub = None
        if tree.child is not None:
            sub = Parser.dfs_scope(tree.child, var)
        if sub is not None and var in sub.dict:
            return sub
        if var in tree.dict:
            return tree
        return None

    @staticmethod
    # Quickly read out the consts from the user file
    # and tokenizes into integer representation
    def clean_data(f_name):
        scan = open(f_name, 'r')
        text = scan.read()
        scan.close()
        consts = text.split(' ')
        for c in consts:
            c = int(c)
        return consts


# Class for the program grammar portion. Will address all variables
# for the parse and semantics section since they're homogenized across
# all of the classes.
class Program:
    # Default constructor
    #   nodes           -   nested queue representation of parse tree
    #   program_scope   -   first nested scope for after begin
    #   space           -   counter for indentation printing
    def __init__(self):
        self.nodes = []
        self.program_scope = scope_tree()
        self.space = 0

    # Parses the program grammar portion
    #   parser          -   parser object
    def parse(self, parser):
        parser.token_assert(Token.PROGRAM, self.nodes)
        # Works by pushing the current class object into the node queue,
        # then calling the parse function of the newly added object
        self.nodes.append(DeclSeq())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.BEGIN, self.nodes)
        self.nodes.append(StmtSeq())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.END, self.nodes)
        if parser.token() != Token.ERROR:
            sys.exit(f'\nERROR: Declarations following end statement.\n')

    # Semantic analysis of parse tree
    #   parser          -   parser object
    #   parent          -   one of three labels {get, assign, declare},
    #                       which are used for more easily classifying
    #                       scope checks
    #   scope           -   scope from parent class like program, if, or
    #                       while to simply string out of scope variables
    def semantics(self, parser, parent=None, scope=None):
        scope = parser.global_scope
        for node in self.nodes:
            if node is Token.BEGIN:
                scope = self.program_scope
                parser.global_scope.child = scope
            if type(node) != Token:
                node.semantics(parser, None, scope)

    # Prints the representation of the parse tre
    def print(self):
        for node in self.nodes:
            if type(node) == DeclSeq:
                node.print(self.space + 1)
            elif type(node) == StmtSeq:
                node.print(self.space + 1)
            elif type(node) == Token:
                print(f'{node.value}')

    # Executes the program from the parse tree.
    #   parser          -   parser object
    #   caller          -   analog to the parent variable in semantics
    #   scope           -   analog to scope variable in semantics
    def execute(self, parser, caller=None, scope=None):
        scope = parser.global_scope
        self.program_scope = scope_tree()
        for node in self.nodes:
            if node is Token.BEGIN:
                scope = self.program_scope
                parser.global_scope.child = scope
            if type(node) is not Token:
                node.execute(parser, caller, scope)


# Redirects to Decl
class DeclSeq:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        self.nodes.append(Decl())
        self.nodes[-1].parse(parser)
        if parser.token() != Token.BEGIN:
            self.nodes.append(DeclSeq())
            self.nodes[-1].parse(parser)

    def semantics(self, parser, parent=None, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, scope)

    def print(self, indent):
        for node in self.nodes:
            if type(node) is not Token:
                node.print(indent)

    def execute(self, parser, caller=None, local=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.execute(parser, caller, local)


# Redirects to IdList
class Decl:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        parser.token_assert(Token.INT, self.nodes)
        self.nodes.append(IdList())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.SEMICOLON, self.nodes)

    def semantics(self, parser, parent=None, scope=None):
        for node in self.nodes:
            if type(node) is IdList:
                # declare tag used here to differentiate how
                # the id request will be resolved
                node.semantics(parser, 'declare', scope)

    def print(self, indent):
        for i in range(indent):
            print('\t', end='')
        for node in self.nodes:
            if type(node) is not Token:
                node.print(indent)
            elif node == Token.INT:
                print(f'{node.value} ', end='')
            else:
                print(f'{node.value}')

    def execute(self, parser, caller=None, local=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.execute(parser, 'declare', local)


class IdList:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        self.nodes.append(Id())
        self.nodes[-1].parse(parser)
        if parser.token() == Token.COMMA:
            parser.token_assert(Token.COMMA, self.nodes)
            self.nodes.append(IdList())
            self.nodes[-1].parse(parser)

    def semantics(self, parser, parent=None, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, scope)

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.print(indent)
            else:
                print(f'{node.value}', end='')

    def execute(self, parser, caller=None, local=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.execute(parser, caller, local)


class Id:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        parser.token_validate(Token.ID)
        self.nodes.append(Token.ID)
        self.nodes.append(parser.get_id())
        parser.next_token()

    def semantics(self, parser, parent, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                # Find lowest scope of declaration
                tree = Parser.dfs_scope(parser.global_scope, node)
                # Verify variable has been declared and instantiated
                if parent == 'get':
                    if tree is None or not tree.dict[node]:
                        sys.exit(f'ERROR: Variable {node} not instantiated')
                # Verify variable doesn't exist in current scope
                elif parent == 'declare':
                    if node not in scope.dict:
                        scope.dict[node] = False
                    else:
                        sys.exit(f'ERROR: Variable {node} declared twice within the same scope.')
                # Assign lowest possible scope or raise flag
                elif parent == 'assign':
                    if tree is None:
                        sys.exit(f'ERROR: Variable {node} not declared in any scope.')
                    tree.dict[node] = True

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is not Token:
                print(node, end='')

    def execute(self, parser, caller=None, local=None):
        for node in self.nodes:
            if type(node) is not Token:
                tree = Parser.dfs_scope(parser.global_scope, node)
                if caller == 'get':
                    if tree is None or tree.dict[node] is None:
                        sys.exit(f'ERROR: Variable {node} not instantiated')
                    return tree.dict[node]
                elif caller == 'declare':
                    if node not in local.dict:
                        local.dict[node] = None
                    else:
                        sys.exit(f'ERROR: Variable {node} declared twice within the same scope.')
                elif caller == 'assign':
                    if tree is None:
                        sys.exit(f'ERROR: Variable {node} not declared in any scope.')
                    return node, tree


class StmtSeq:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        if parser.token() == Token.ID:
            self.nodes.append(Assign())
        elif parser.token() == Token.INPUT:
            self.nodes.append(Input())
        elif parser.token() == Token.OUTPUT:
            self.nodes.append(Output())
        elif parser.token() == Token.IF:
            self.nodes.append(If())
        elif parser.token() == Token.WHILE:
            self.nodes.append(While())
        elif parser.token() == Token.INT:
            self.nodes.append(Decl())
        else:
            sys.exit("ERROR: Bad start to statement: " + parser.scanner.token().name + "\n")
        self.nodes[-1].parse(parser)
        if (not parser.token() == Token.END
                and not parser.token() == Token.ENDIF
                and not parser.token() == Token.ENDWHILE
                and not parser.token() == Token.ELSE):
            self.nodes.append(StmtSeq())
            self.nodes[-1].parse(parser)

    def semantics(self, parser, parent=None, scope=None):
        for node in self.nodes:
            node.semantics(parser, parent, scope)

    def print(self, indent):
        for node in self.nodes:
            node.print(indent)

    def execute(self, parser, caller=None, local=None):
        for node in self.nodes:
            node.execute(parser, caller, local)


class Assign:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        self.nodes.append(Id())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.ASSIGN, self.nodes)
        self.nodes.append(Expr())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.SEMICOLON, self.nodes)

    def semantics(self, parser, parent=None, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, 'assign', scope)

    def print(self, indent):
        for i in range(indent):
            print('\t', end='')
        for node in self.nodes:
            if type(node) is Token:
                if node == Token.ASSIGN:
                    print(f'{node.value}', end='')
                else:
                    print(f'{node.value}')
            else:
                node.print(indent)

    def execute(self, parser, caller=None, local=None):
        var, tree, expr = '', None, 0
        for node in self.nodes:
            if type(node) is Id:
                var, tree = node.execute(parser, 'assign', local)
            elif type(node) is Expr:
                expr = node.execute(parser, caller, local)
        tree.dict[var] = expr


class If:
    def __init__(self):
        self.nodes = []
        self.local = scope_tree()

    def parse(self, parser):
        parser.token_assert(Token.IF, self.nodes)
        self.nodes.append(Cond())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.THEN, self.nodes)
        self.nodes.append(StmtSeq())
        self.nodes[-1].parse(parser)
        if parser.token() == Token.ELSE:
            parser.token_assert(Token.ELSE, self.nodes)
            self.nodes.append(StmtSeq())
            self.nodes[-1].parse(parser)
        parser.token_assert(Token.ENDIF, self.nodes)

    def semantics(self, parser, parent=None, scope=None):
        scope.child = self.local
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, self.local)
            elif node is Token.ENDIF:
                scope.child = None

    def print(self, indent):
        for i in range(indent):
            print('\t', end='')
        for node in self.nodes:
            if type(node) is not Token:
                node.print(indent)
            else:
                if node == Token.IF:
                    print(f'{node.value} ', end='')
                elif node == Token.THEN:
                    indent += 1
                    print(f'{node.value}')
                elif node == Token.ELSE:
                    indent -= 1
                    for i in range(indent):
                        print('\t', end='')
                    indent += 1
                    print(f'{node.value}')
                elif node == Token.ENDIF:
                    indent -= 1
                    for i in range(indent):
                        print('\t', end='')
                    print(f'{node.value}')

    def execute(self, parser, caller=None, local=None):
        self.local = scope_tree()
        local.child = self.local
        truth, index = True, 1
        truth = self.nodes[index].execute(parser, caller, self.local)
        index += 2
        if truth:
            self.nodes[index].execute(parser, caller, self.local)
        elif self.nodes[index+1] == Token.ELSE:
            index += 2
            self.nodes[index].execute(parser, caller, self.local)
        local.child = None


class While:
    def __init__(self):
        self.nodes = []
        self.local = scope_tree()

    def parse(self, parser):
        parser.token_assert(Token.WHILE, self.nodes)
        self.nodes.append(Cond())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.BEGIN, self.nodes)
        self.nodes.append(StmtSeq())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.ENDWHILE, self.nodes)

    def semantics(self, parser, parent=None, scope=None):
        scope.child = self.local
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, self.local)
            elif node is Token.ENDWHILE:
                scope.child = None

    def print(self, indent):
        for i in range(indent):
            print('\t', end='')
        for node in self.nodes:
            if type(node) is not Token:
                node.print(indent)
            else:
                if node == Token.WHILE:
                    print(f'{node.value} ', end='')
                elif node == Token.BEGIN:
                    indent += 1
                    print(f' {node.value}')
                elif node == Token.ENDWHILE:
                    indent -= 1
                    for i in range(indent):
                        print('\t', end='')
                    print(f'{node.value}')

    def execute(self, parser, caller=None, local=None):
        self.local = scope_tree()
        local.child = self.local
        index = 1
        cond = self.nodes[1]
        index += 2
        stmt = self.nodes[index]
        while cond.execute(parser, caller, self.local):
            stmt.execute(parser, caller, local)
        local.child = None


class Input:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        parser.token_assert(Token.INPUT, self.nodes)
        self.nodes.append(Id())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.SEMICOLON, self.nodes)

    def semantics(self, parser, parent=None, scope=None):
        for node in self.nodes:
            if type(node) is Id:
                node.semantics(parser, 'assign', scope)

    def print(self, indent):
        for i in range(indent):
            print('\t', end='')
        for node in self.nodes:
            if type(node) is not Token:
                node.print(indent)
            elif node is Token.INPUT:
                print(f'{node.value} ', end='')
            else:
                print(f'{node.value}')

    def execute(self, parser, caller=None, local=None):
        var, tree = '', None
        for node in self.nodes:
            if type(node) is Id:
                var, tree = node.execute(parser, 'assign', local)
        if len(parser.data) > 0:
            tree.dict[var] = parser.data.pop(0)
        else:
            sys.exit('ERROR: Insufficient entries in data file to complete.')


class Output:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        parser.token_assert(Token.OUTPUT, self.nodes)
        self.nodes.append(Expr())
        self.nodes[-1].parse(parser)
        parser.token_assert(Token.SEMICOLON, self.nodes)

    def semantics(self, parser, parent=None, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, 'call', scope)

    def print(self, indent):
        for i in range(indent):
            print('\t', end='')
        for node in self.nodes:
            if type(node) is not Token:
                node.print()
            elif node is Token.OUTPUT:
                print(f'{node.value} ', end='')
            else:
                print(f'{node.value}')

    def execute(self, parser, caller=None, local=None):
        print(self.nodes[1].execute(parser, 'get', local))


class Expr:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        self.nodes.append(Term())
        self.nodes[-1].parse(parser)
        if parser.token() == Token.ADD:
            parser.token_assert(Token.ADD, self.nodes)
            self.nodes.append(Expr())
            self.nodes[-1].parse(parser)
        elif parser.token() == Token.SUB:
            parser.token_assert(Token.SUB, self.nodes)
            self.nodes.append(Expr())
            self.nodes[-1].parse(parser)

    def semantics(self, parser, parent, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, scope)

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is Token:
                print(f'{node.value}', end='')
            else:
                node.print()

    def execute(self, parser, caller=None, local=None):
        val = self.nodes[0].execute(parser, 'expr', local)
        if len(self.nodes) > 1:
            if self.nodes[1] is Token.ADD:
                val += self.nodes[2].execute(parser, caller, local)
            elif self.nodes[1] is Token.SUB:
                val -= self.nodes[2].execute(parser, caller, local)
        return val


class Term:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        self.nodes.append(Factor())
        self.nodes[-1].parse(parser)
        if parser.token() == Token.MULT:
            parser.token_assert(Token.MULT, self.nodes)
            self.nodes.append(Term())
            self.nodes[-1].parse(parser)

    def semantics(self, parser, parent, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, scope)

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.print()
            else:
                print(f'{node.value}', end='')

    def execute(self, parser, caller=None, local=None):
        val = self.nodes[0].execute(parser, caller, local)
        if len(self.nodes) > 1 and self.nodes[1] is Token.MULT:
            val *= self.nodes[2].execute(parser, caller, local)
        return val


class Factor:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        if parser.token() == Token.ID:
            self.nodes.append(Id())
            self.nodes[-1].parse(parser)
        elif parser.token() == Token.CONST:
            self.nodes.append(Const())
            self.nodes[-1].parse(parser)
        elif parser.token() == Token.LPAREN:
            self.expr_paren_parse(parser)
        else:
            sys.exit('ERROR: Invalid operator received.')

    def semantics(self, parser, parent, scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, scope)

    def expr_paren_parse(self, parser):
        parser.token_assert(Token.LPAREN, self.nodes)
        self.nodes.append(Expr())
        self.nodes[-1].parse(parser)
        if parser.token() == Token.LPAREN:
            self.expr_paren_parse(parser)
        parser.token_assert(Token.RPAREN, self.nodes)

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.print()
            else:
                print(f'{node.value}', end='')

    def execute(self, parser, caller=None, local=None):
        if type(self.nodes[0]) is Const:
            return self.nodes[0].execute(parser, caller, local)
        elif type(self.nodes[0]) is Id:
            return self.nodes[0].execute(parser, 'get', local)
        else:
            return self.nodes[1].execute(parser, caller, local)


class Cond:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        if parser.token() == Token.NEGATION:
            parser.token_assert(Token.NEGATION, self.nodes)
            self.cond_paren_parse(parser)
        else:
            self.nodes.append(Cmpr())
            self.nodes[-1].parse(parser)
            if parser.token() == Token.OR:
                parser.token_assert(Token.OR, self.nodes)
                self.nodes.append(Cond())
                self.nodes[-1].parse(parser)

    def cond_paren_parse(self, parser):
        parser.token_assert(Token.LPAREN, self.nodes)
        self.nodes.append(Cond())
        self.nodes[-1].parse(parser)
        if parser.token() == Token.LPAREN:
            self.cond_paren_parse(parser)
        parser.token_assert(Token.RPAREN, self.nodes)

    def semantics(self, parser, parent='call', scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, scope)

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.print()
            else:
                print(f'{node.value}', end='')

    def execute(self, parser, caller=None, local=None):
        val = None
        if self.nodes[0] is not Token.NEGATION:
            val = self.nodes[0].execute(parser, caller, local)
            if len(self.nodes) > 1 and self.nodes[1] is Token.OR:
                val |= self.nodes[2].execute(parser, caller, local)
        else:
            val = not (self.nodes[2].execute(parser, caller, local))
        return val


class Cmpr:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        self.nodes.append(Expr())
        self.nodes[-1].parse(parser)
        if parser.token() == Token.EQUAL:
            parser.token_assert(Token.EQUAL, self.nodes)
        elif parser.token() == Token.LESS:
            parser.token_assert(Token.LESS, self.nodes)
        elif parser.token() == Token.LESSEQUAL:
            parser.token_assert(Token.LESSEQUAL, self.nodes)
        self.nodes.append(Expr())
        self.nodes[-1].parse(parser)

    def semantics(self, parser, parent='call', scope=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.semantics(parser, parent, scope)

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is not Token:
                node.print()
            else:
                print(f'{node.value}', end='')

    def execute(self, parser, caller=None, local=None):
        expr = self.nodes[0].execute(parser, caller, local)
        if self.nodes[1] is Token.LESS:
            return expr < self.nodes[2].execute(parser, caller, local)
        elif self.nodes[1] is Token.EQUAL:
            return expr == self.nodes[2].execute(parser, caller, local)
        else:
            return expr <= self.nodes[2].execute(parser, caller, local)


class Const:
    def __init__(self):
        self.nodes = []

    def parse(self, parser):
        parser.token_validate(Token.CONST)
        self.nodes.append(parser.get_const())
        parser.next_token()

    @staticmethod
    # Placeholder function, not applicable since const
    # value is already screened
    def semantics(parser, parent, scope=None):
        return True

    def print(self, indent=None):
        for node in self.nodes:
            if type(node) is not Token:
                print(f'{node}', end='')

    def execute(self, parser, caller=None, local=None):
        for node in self.nodes:
            if node is not Token:
                return int(node)


# Class representation of the nested scopes. Each layer consists of
# two member elements, a dictionary to access by variable name and
# a key. Child points to the next scope in the stack
#   dict        -   dictionary of variable:value pairs
#   child       -   reference to the next tuple, instantiated as None
class scope_tree:
    def __init__(self):
        self.dict = dict()
        self.child = None
