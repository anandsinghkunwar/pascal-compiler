import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lexer import tokens

# TODO: PRECEDENCE ERROR

class Rule(object):
    def __init__(self, name, production):
        self.name = name
        self.production = production

def p_start(p):
    'start : program_statement global_decs_defs block DOT'
    p[0] = Rule('start', get_production(p))

def p_program_statement(p):
    '''program_statement : KEYWORD_PROGRAM IDENTIFIER SEMICOLON
                         | empty'''
    p[0] = Rule('program_statement', get_production(p))

def p_global_decs_defs(p):
    '''global_decs_defs : global_decs_defs const_declarations
                        | global_decs_defs type_declarations
                        | global_decs_defs var_declarations
                        | global_decs_defs func_def
                        | global_decs_defs proc_def
                        | empty'''
    p[0] = Rule('global_decs_defs', get_production(p))

def p_const_declarations(p):
    '''const_declarations : KEYWORD_CONST const_statements'''
    p[0] = Rule('const_declarations', get_production(p))

def p_const_statements(p):
    '''const_statements : const_statements const_statement
                        | const_statement'''
    p[0] = Rule('const_statements', get_production(p))

def p_const_statement(p):
    'const_statement : IDENTIFIER EQUAL expression SEMICOLON'
    p[0] = Rule('const_statement', get_production(p))

def p_string(p):
    '''string : CONSTANT_STRING_LEADSPACE substring
              | CONSTANT_STRING_LEADSPACE
              | substring'''
    p[0] = Rule('string', get_production(p))

def p_substring(p):
    '''substring : CONSTANT_STRING substring
                 | CONSTANT_SPECIAL_CHAR substring
                 | CONSTANT_STRING
                 | CONSTANT_SPECIAL_CHAR'''
    p[0] = Rule('substring', get_production(p))

def p_type_declarations(p):
    '''type_declarations : KEYWORD_TYPE type_statements'''
    p[0] = Rule('type_declarations', get_production(p))

def p_type_statements(p):
    '''type_statements : type_statements type_statement
                       | type_statement'''
    p[0] = Rule('type_statements', get_production(p))

def p_type_statement(p):
    'type_statement : identifiers EQUAL type SEMICOLON'
    p[0] = Rule('type_statement', get_production(p))

def p_identifiers(p):
    '''identifiers : identifiers COMMA IDENTIFIER
                   | IDENTIFIER COMMA IDENTIFIER'''
    p[0] = Rule('identifiers', get_production(p))

def p_type(p):
    '''type : type_identifier
            | array_declaration
            | string_declaration
            | OP_POINTER type_identifier'''
    p[0] = Rule('type', get_production(p))

def p_type_identifier(p):
    '''type_identifier : IDENTIFIER
                       | KEYWORD_STRING'''
    p[0] = Rule('type_identifier', get_production(p))

def p_array_declaration(p):
    '''array_declaration : KEYWORD_ARRAY LEFT_SQUARE_BRACKETS array_ranges RIGHT_SQUARE_BRACKETS KEYWORD_OF type'''
    p[0] = Rule('array_declaration', get_production(p))

def p_array_ranges(p):
    '''array_ranges : array_ranges COMMA array_range
                    | array_range'''
    p[0] = Rule('array_ranges', get_production(p))

def p_array_range(p):
    '''array_range : CONSTANT_INTEGER DOTDOT CONSTANT_INTEGER

                   | char DOTDOT char

                   | CONSTANT_BOOLEAN_FALSE DOTDOT CONSTANT_BOOLEAN_FALSE
                   | CONSTANT_BOOLEAN_FALSE DOTDOT CONSTANT_BOOLEAN_TRUE
                   | CONSTANT_BOOLEAN_TRUE DOTDOT CONSTANT_BOOLEAN_TRUE'''
    p[0] = Rule('array_range', get_production(p))

def p_char(p):
    '''char : CONSTANT_STRING
            | CONSTANT_SPECIAL_CHAR
            | CONSTANT_STRING_LEADSPACE'''
    p[0] = Rule('char', get_production(p))

def p_string_declaration(p):
    '''string_declaration : KEYWORD_STRING LEFT_SQUARE_BRACKETS CONSTANT_INTEGER RIGHT_SQUARE_BRACKETS'''
    p[0] = Rule('string_declaration', get_production(p))


def p_var_declarations(p):
    '''var_declarations : KEYWORD_VAR var_statements'''
    p[0] = Rule('var_declarations', get_production(p))

def p_var_statements(p):
    '''var_statements : var_statements var_statement
                      | var_statement'''
    p[0] = Rule('var_statements', get_production(p))

def p_var_statement(p):
    '''var_statement : identifiers COLON type SEMICOLON
                     | IDENTIFIER COLON type SEMICOLON
                     | IDENTIFIER COLON type EQUAL expression SEMICOLON'''
    p[0] = Rule('var_statement', get_production(p))

def p_proc_def(p):
    '''proc_def : proc_head SEMICOLON declarations block SEMICOLON'''
    p[0] = Rule('proc_def', get_production(p))

def p_proc_head(p):
    'proc_head : KEYWORD_PROCEDURE IDENTIFIER parameter_list'
    p[0] = Rule('proc_head', get_production(p))

def p_func_def(p):
    '''func_def : func_head SEMICOLON declarations block SEMICOLON'''
    p[0] = Rule('func_def', get_production(p))

def p_func_head(p):
    '''func_head : KEYWORD_FUNCTION IDENTIFIER parameter_list COLON type_identifier'''
    p[0] = Rule('func_head', get_production(p))

def p_declarations(p):
    '''declarations : declarations const_declarations
                    | declarations type_declarations
                    | declarations var_declarations
                    | empty'''
    p[0] = Rule('declarations', get_production(p))

def p_parameter_list(p):
    '''parameter_list : LEFT_PARENTHESIS parameter_declarations RIGHT_PARENTHESIS
                      | LEFT_PARENTHESIS RIGHT_PARENTHESIS'''
    p[0] = Rule('parameter_list', get_production(p))

def p_parameter_declarations(p):
    '''parameter_declarations : parameter_declarations SEMICOLON value_parameter
                              | value_parameter'''
    p[0] = Rule('parameter_declarations', get_production(p))

def p_value_parameter(p):
    '''value_parameter : identifiers COLON type_identifier
                       | IDENTIFIER COLON type_identifier
                       | identifiers COLON KEYWORD_ARRAY KEYWORD_OF type_identifier
                       | IDENTIFIER COLON KEYWORD_ARRAY KEYWORD_OF type_identifier
                       | IDENTIFIER COLON type_identifier EQUAL unsigned_constant'''
    p[0] = Rule('value_parameter', get_production(p))

def p_block(p):
    'block : KEYWORD_BEGIN statements KEYWORD_END'
    p[0] = Rule('block', get_production(p))

def p_statements(p):
    '''statements : statements SEMICOLON statement
                  | statement'''
    p[0] = Rule('statements', get_production(p))

def p_statement(p):
    '''statement : matched_statement
                 | unmatched_statement'''
    p[0] = Rule('statement', get_production(p))

def p_matched_statement(p):
    '''matched_statement : simple_statement
                         | structured_statement
                         | KEYWORD_IF expression KEYWORD_THEN matched_statement KEYWORD_ELSE matched_statement
                         | loop_header matched_statement
                         | empty'''
    p[0] = Rule('matched_statement', get_production(p))

def p_unmatched_statement(p):
    '''unmatched_statement : KEYWORD_IF expression KEYWORD_THEN statement
                           | KEYWORD_IF expression KEYWORD_THEN matched_statement KEYWORD_ELSE unmatched_statement
                           | loop_header unmatched_statement'''
    p[0] = Rule('unmatched_statement', get_production(p))

def p_loop_header(p):
    '''loop_header : for_loop_header
                   | while_loop_header'''
    p[0] = Rule('loop_header', get_production(p))

def p_for_loop_header(p):
    '''for_loop_header : KEYWORD_FOR IDENTIFIER COLON_EQUAL expression KEYWORD_TO expression KEYWORD_DO
                       | KEYWORD_FOR IDENTIFIER COLON_EQUAL expression KEYWORD_DOWNTO expression KEYWORD_DO'''
    p[0] = Rule('for_loop_header', get_production(p))

def p_while_loop_header(p):
    '''while_loop_header : KEYWORD_WHILE expression KEYWORD_DO'''
    p[0] = Rule('while_loop_header', get_production(p))

def p_simple_statement(p):
    '''simple_statement : assignment_statement
                        | func_proc_statement'''
    p[0] = Rule('simple_statement', get_production(p))

def p_assignment_statement(p):
    '''assignment_statement : variable_reference COLON_EQUAL expression'''
    p[0] = Rule('assignment_statement', get_production(p))

def p_expression(p):
    '''expression : simple_expression relational_operator simple_expression
                  | simple_expression'''
    p[0] = Rule('expression', get_production(p))

def p_simple_expression(p):
    '''simple_expression : term OP_PLUS simple_expression
                         | term OP_MINUS simple_expression
                         | term OP_OR simple_expression
                         | term OP_XOR simple_expression
                         | term'''
    p[0] = Rule('simple_expression', get_production(p))

def p_term(p):
    '''term : factor OP_MULT term
            | factor OP_DIV term
            | factor OP_MOD term
            | factor OP_AND term
            | factor OP_SHIFTLEFT term
            | factor OP_SHIFTRIGHT term
            | factor'''
    p[0] = Rule('term', get_production(p))

def p_factor(p):
    '''factor : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
              | sign factor
              | OP_NOT factor
              | function_call
              | variable_reference
              | unsigned_constant'''
    p[0] = Rule('factor', get_production(p))

def p_function_call(p):
    '''function_call : IDENTIFIER LEFT_PARENTHESIS expression_list RIGHT_PARENTHESIS
                     | IDENTIFIER LEFT_PARENTHESIS RIGHT_PARENTHESIS'''
    p[0] = Rule('function_call', get_production(p))

def p_expression_list(p):
    '''expression_list : expression_list COMMA expression
                       | expression'''
    p[0] = Rule('expression_list', get_production(p))

def p_variable_reference(p):
    '''variable_reference : IDENTIFIER
                          | IDENTIFIER LEFT_SQUARE_BRACKETS array_index RIGHT_SQUARE_BRACKETS
                          | IDENTIFIER array_index_cstyle'''
    p[0] = Rule('variable_reference', get_production(p))

def p_array_index(p):
    '''array_index : array_index COMMA expression
                   | expression COMMA expression'''
    p[0] = Rule('array_index', get_production(p))

def p_array_index_cstyle(p):
    '''array_index_cstyle : array_index_cstyle LEFT_SQUARE_BRACKETS expression RIGHT_SQUARE_BRACKETS
                   | LEFT_SQUARE_BRACKETS expression RIGHT_SQUARE_BRACKETS'''
    p[0] = Rule('array_index_cstyle', get_production(p))

def p_sign(p):
    '''sign : OP_PLUS
            | OP_MINUS'''
    p[0] = Rule('sign', get_production(p))

def p_unsigned_constant(p):
    '''unsigned_constant : CONSTANT_INTEGER
                         | CONSTANT_HEX
                         | CONSTANT_BINARY
                         | CONSTANT_OCTAL
                         | CONSTANT_NIL
                         | CONSTANT_BOOLEAN_TRUE
                         | CONSTANT_BOOLEAN_FALSE
                         | string'''
    p[0] = Rule('unsigned_constant', get_production(p))

def p_relational_operator(p):
    '''relational_operator : OP_NEQ
                           | OP_GT
                           | OP_LT
                           | OP_GEQ
                           | OP_LEQ
                           | EQUAL'''
    p[0] = Rule('relational_operator', get_production(p))

def p_func_proc_statement(p):
    '''func_proc_statement : IDENTIFIER LEFT_PARENTHESIS expression_list RIGHT_PARENTHESIS
                           | IDENTIFIER LEFT_PARENTHESIS RIGHT_PARENTHESIS
                           | IDENTIFIER'''
    p[0] = Rule('func_proc_statement', get_production(p))

def p_structured_statement(p):
    '''structured_statement : block
                            | repeat_statement'''
    p[0] = Rule('structured_statement', get_production(p))

def p_repeat_statement(p):
    '''repeat_statement : KEYWORD_REPEAT statements KEYWORD_UNTIL expression'''
    p[0] = Rule('repeat_statement', get_production(p))

def p_empty(p):
    'empty :'
    p[0] = Rule('empty', get_production(p))

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!", p.lineno, p.type)

def get_production(p):
    production = []
    for i in xrange(1, len(p)):
        production.append(p[i])
    return production

def print_derivation(form):
    nonterm_to_reduce = None
    for item in reversed(form):
        if type(item) is Rule:
            nonterm_to_reduce = item
            nonterm_index = form.index(item)
            break

    if not nonterm_to_reduce:
        return

    left_list = form[:nonterm_index]
    right_list = form[nonterm_index+1:]

    derived_form = left_list + nonterm_to_reduce.production + right_list

    # Print the LHS of the derivation
    print '<span style="color:blue">',
    for item in form:
        if type(item) is Rule:
            if item == nonterm_to_reduce:
                print '<b>', item.name, '</b>',
            else:
                print item.name,
        else:
            print item,
    print '</span>',
    print '<b>==></b>',

    # Print the RHS of the derivation
    for item in derived_form:
        if type(item) is Rule:
            print item.name,
        else:
            print item,

    print '<br><br>'

    print_derivation(derived_form)

def generate_html(start):
    print '<html>'
    print '<body>'
    print_derivation([start])
    print '</body>'
    print '</html>'

# Build the parser
parser = yacc.yacc()
