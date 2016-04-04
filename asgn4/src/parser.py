import ply.yacc as yacc
import sys
import symbol_table as ST
import ircodegen as IG

# Get the token map from the lexer. This is required.
from lexer import tokens

# Global Variables, Functions
nextQuad = 1

def backpatch(instrList, target):
    for instr in instrList:
        if instr == IG.InstrList[instr].LineNo:
            IG.InstrList[instr].Target = target
        else:
            print 'Why is this happening!', instr

def p_start(p):
    'start : program_statement global_decs_defs block DOT'
    p[0] = IG.Node()
    p[0].code = p[2].code + p[3].code
    p[0].genCode(IG.TACInstr(IG.TACInstr.RETURN, lineNo=nextQuad))
    nextQuad += 1

def p_program_statement(p):
    '''program_statement : KEYWORD_PROGRAM IDENTIFIER SEMICOLON
                         | empty'''
    if len(p) == 4:
        ST.currSymTab.addVar(p[2], ST.Type('program', ST.Type.PROGRAM))
    elif len(p) == 2:
        pass
    # TODO Check if anything else required

def p_program_statement_error(p):
    '''program_statement : KEYWORD_PROGRAM IDENTIFIER'''
    # Line number reported from IDENTIFIER token
    print_error("Syntax error at line", p.lineno(2))
    print_error("\tMissing ';'")

def p_global_decs_defs(p):
    '''global_decs_defs : global_decs_defs const_declarations
                        | global_decs_defs type_declarations
                        | global_decs_defs var_declarations
                        | global_decs_defs marker_fpdef func_def
                        | global_decs_defs marker_fpdef proc_def
                        | empty'''
    p[0] = IG.Node()
    if len(p) == 3:
        p[0].code = p[1].code + p[2].code   # Assuming type_declarations
                                            # is also a node with code
    elif len(p) == 4:
        backpatch([p[2].code.LineNo], nextQuad)
        p[0].code = p[1].code + p[2].code + p[3].code

def p_marker_fpdef(p):
    '''marker_fpdef : '''
    p[0] = IG.Node()
    p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=nextQuad))
    nextQuad += 1
    ST.currSymTab = ST.SymTab(ST.currSymTab)


def p_const_declarations(p):
    '''const_declarations : KEYWORD_CONST const_statements'''
    p[0] = p[1]

def p_const_statements(p):
    '''const_statements : const_statements const_statement
                        | const_statement'''
    p[0] = IG.Node()
    if len(p) == 3:
        p[0].code = p[1].code + p[2].code
    elif len(p) == 2:
        p[0].code = p[1].code

def p_const_statement(p):
    'const_statement : IDENTIFIER EQUAL expression SEMICOLON'
    STEntry = ST.currSymTab.addVar(p[1], p[3].type, isConst=True)
    p[0] = IG.Node()
    p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, dest=STEntry, src1=p[3].place, lineNo=nextQuad))
    nextQuad += 1

def p_const_statement_error(p):
    'const_statement : IDENTIFIER EQUAL expression'
    #Line number reported from expression nonterminal
    print_error("Syntax error at line", p.linespan(3)[1])
    print_error("\tMissing ';'")

def p_string(p):
    '''string : CONSTANT_STRING_LEADSPACE substring
              | CONSTANT_STRING_LEADSPACE
              | substring'''
    p[0] = IG.Node()

    if len(p) == 3:
        p[0].value = p[1] + p[2].value
    elif len(p) == 2:
        if type(p[1]) == IG.Node:
            p[0].value = p[1].value
        else:
            p[0].value = p[1]

def p_substring(p):
    '''substring : CONSTANT_STRING substring
                 | CONSTANT_SPECIAL_CHAR substring
                 | CONSTANT_STRING
                 | CONSTANT_SPECIAL_CHAR'''
    p[0] = IG.Node()

    if len(p) == 3:
        if type(p[1]) == str:
            p[0].value = p[1] + p[2].value
        else:
            p[0].value = chr(p[1]) + p[2].value
    elif len(p) == 2:
        if type(p[1]) == str:
            p[0].value = p[1]
        else:
            p[0].value = chr(p[1])

def p_type_declarations(p):
    '''type_declarations : KEYWORD_TYPE type_statements'''
    p[0] = IG.Node()    # This is being created for uniformity
                        # in creating code in global_decs_defs

def p_type_statements(p):
    '''type_statements : type_statements type_statement
                       | type_statement'''

def p_type_statement(p):
    '''type_statement : identifiers EQUAL type SEMICOLON
                      | IDENTIFIER EQUAL type SEMICOLON'''
    if type(p[1]) == IG.Node:
        for item in p[1].items:
            ST.currSymTab.addVar(item, p[3].type)
            # TODO Handle arrays FIXME
    else:
        ST.currSymTab.addVar(p[1], p[3].type)

def p_type_statement_error(p):
    '''type_statement : identifiers EQUAL type
                      | IDENTIFIER EQUAL type'''
    #Line number reported from type nonterminal
    print_error("Syntax error at line", p.linespan(3)[1])
    print_error("\tMissing ';'")

def p_identifiers(p):
    '''identifiers : identifiers COMMA IDENTIFIER
                   | IDENTIFIER COMMA IDENTIFIER'''
    p[0] = IG.Node()
    if type(p[1]) == IG.Node:
        p[0].items = p[1].items + [p[3]]
    else:
        p[0].items = [p[1], p[3]]

def p_type(p):
    '''type : type_identifier
            | array_declaration
            | string_declaration'''
    p[0] = p[1]

def p_type_identifier(p):
    '''type_identifier : IDENTIFIER
                       | KEYWORD_STRING'''
    p[0] = IG.Node()
    p[0].type = ST.Type(p[1], ST.Type.TYPE)

def p_array_declaration(p):
    '''array_declaration : KEYWORD_ARRAY LEFT_SQUARE_BRACKETS array_ranges RIGHT_SQUARE_BRACKETS KEYWORD_OF type'''
    p[0] = IG.Node()
    p[0].type = ST.Type('array', ST.Type.ARRAY, arrayBeginList=p[3].arrayBeginList,
                        arrayEndList=p[3].arrayEndList, arrayBaseType=p[6].type)

def p_array_ranges(p):
    '''array_ranges : array_ranges COMMA array_range
                    | array_range'''
    p[0] = IG.Node()
    if len(p) == 4:
        p[0].arrayBeginList = p[1].arrayBeginList + p[3].arrayBeginList
    else:
        p[0].arrayBeginList = p[1].arrayBeginList

def p_array_range(p):
    '''array_range : integer_range
                   | char_range
                   | boolean_range'''
    p[0] = p[1]

def p_integer_range(p):
    '''integer_range : CONSTANT_INTEGER DOTDOT CONSTANT_INTEGER'''

    p[0] = IG.Node()
    if (p[1] <= p[3]):
        p[0].arrayBeginList = [p[1]]
        p[0].arrayEndList = [p[3]]
    else:
        print_error("Semantic error at line", p.lineno(3))
        print_error("\tEnd index is less than start index")

def p_char_range(p):
    '''char_range : char DOTDOT char'''

    p[0] = IG.Node()
    if (p[1] <= p[3]):
        p[0].arrayBeginList = [p[1]]
        p[0].arrayEndList = [p[3]]
    else:
        print_error("Semantic error at line", p.lineno(3))
        print_error("\tEnd index is less than start index")

def p_boolean_range(p):
    '''boolean_range : CONSTANT_BOOLEAN_FALSE DOTDOT CONSTANT_BOOLEAN_FALSE
                     | CONSTANT_BOOLEAN_FALSE DOTDOT CONSTANT_BOOLEAN_TRUE
                     | CONSTANT_BOOLEAN_TRUE DOTDOT CONSTANT_BOOLEAN_TRUE'''

    p[0] = IG.Node()
    p[0].arrayBeginList = [p[1]]
    p[0].arrayEndList = [p[3]]

def p_char(p):
    '''char : CONSTANT_STRING
            | CONSTANT_SPECIAL_CHAR
            | CONSTANT_STRING_LEADSPACE'''
    #p[0] = Rule('char', get_production(p))
    if type(p[1]) == int:
        p[0] = chr(p[1])
    else:
        if len(p[1]) == 1:
            p[0] = p[1]
        else:
            print_error("Semantic error at line", p.lineno(1))
            print_error("\tExpected character got string")

def p_string_declaration(p):
    '''string_declaration : KEYWORD_STRING LEFT_SQUARE_BRACKETS CONSTANT_INTEGER RIGHT_SQUARE_BRACKETS'''
    p[0] = IG.Node()
    p[0].type = ST.Type('string', ST.Type.STRING, strLen=p[3])

def p_var_declarations(p):
    '''var_declarations : KEYWORD_VAR var_statements'''
    p[0] = p[2]

def p_var_statements(p):
    '''var_statements : var_statements var_statement
                      | var_statement'''
    p[0] = IG.Node()
    if len(p) == 3:
        p[0].code = p[1].code + p[2].code
    elif len(p) == 2:
        p[0].code = p[1].code

def p_var_statement(p):
    '''var_statement : identifiers COLON type SEMICOLON
                     | IDENTIFIER COLON type SEMICOLON
                     | IDENTIFIER COLON type EQUAL expression SEMICOLON'''
    #p[0] = Rule('var_statement', get_production(p))
    # TODO p[0] ???
    if len(p) == 5:
        if type(p[1]) == IG.Node:
            for item in p[1].items:
                ST.currSymTab.addVar(item, p[3].type)
                # TODO Handle arrays
        else:
            ST.currSymTab.addVar(p[1], p[3].type)
    else:
        STEntry = ST.currSymTab.addVar(p[1], p[3].type)
        p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, dest=STEntry, src1=p[5].place, lineNo=nextQuad))
        nextQuad += 1

def p_var_statement_colon_error(p):
    '''var_statement : identifiers error type SEMICOLON
                     | IDENTIFIER error type SEMICOLON
                     | IDENTIFIER error type EQUAL expression SEMICOLON'''
    print_error("\tExpected ':'")

def p_var_statement_semicolon_error(p):
    '''var_statement : identifiers COLON type
                     | IDENTIFIER COLON type
                     | IDENTIFIER COLON type EQUAL expression'''
    if len(p) == 4:
        #Line number reported from type nonterminal
        print_error("Syntax error at line", p.linespan(3)[1])
    elif len(p) == 6:
        #Line number reported from expression
        print_error("Syntax error at line", p.linespan(5)[1])
    print_error("\tMissing ';'")

def p_var_statement_error(p):
    '''var_statement : identifiers type
                     | IDENTIFIER type
                     | IDENTIFIER type EQUAL expression'''
    if len(p) == 4:
        #Line number reported from type nonterminal
        print_error("Syntax error at line", p.linespan(3)[1])
    elif len(p) == 6:
        # Line number reported from expression
        print_error("Syntax error at line", p.linespan(5)[1])
    print_error("\tMissing ':' and ';'")

def p_proc_def(p):
    '''proc_def : proc_head SEMICOLON declarations block SEMICOLON'''
    ST.currSymTab = ST.currSymTab.previousTable
    p[0] = IG.Node()
    p[0].code = p[1].code + p[3].code + p[4].code
    p[0].genCode(IG.TACInstr(IG.TACInstr.RETURN))
    nextQuad += 1

def p_proc_def_head_error(p):
    '''proc_def : proc_head declarations block SEMICOLON'''
    #Line number reported from proc_head
    print_error("Syntax error at line", p.linespan(1)[1])
    print_error("\tMissing ';'")

def p_proc_def_block_error(p):
    '''proc_def : proc_head SEMICOLON declarations block'''
    #Line number reported from block
    print_error("Syntax error at line", p.linespan(4)[1])
    print_error("\tMissing ';'")

def p_proc_def_head_block_error(p):
    '''proc_def : proc_head declarations block'''
    #Line number reported from proc_head and block
    print_error("Syntax error at line", p.linespan(1)[1])
    print_error("\tMissing ';'")
    print_error("Syntax error at line", p.linespan(3)[1])
    print_error("\tMissing ';'")

def p_proc_head(p):
    'proc_head : KEYWORD_PROCEDURE IDENTIFIER parameter_list'
    ST.currSymTab.previousTable.addProcedure(p[2], len(p[3].items))
    p[0] = IG.Node()
    p[0].genCode(IG.TACInstr(IG.TACInstr.LABEL, label=p[2], paramList=p[3].items, lineNo=nextQuad))
    nextQuad += 1

def p_func_def(p):
    '''func_def : func_head SEMICOLON declarations block SEMICOLON'''
    ST.currSymTab = ST.currSymTab.previousTable
    p[0] = IG.Node()
    p[0].code = p[1].code + p[3].code + p[4].code
    p[0].genCode(IG.TACInstr(IG.TACInstr.RETURN, src1=p[1].place))

def p_func_def_head_error(p):
    '''func_def : func_head declarations block SEMICOLON'''
    #Line number reported from func_head
    print_error("Syntax error at line", p.linespan(1)[1])
    print_error("\tMissing ';'")

def p_func_def_block_error(p):
    '''func_def : func_head SEMICOLON declarations block'''
    #Line number reported from block
    print_error("Syntax error at line", p.linespan(4)[1])
    print_error("\tMissing ';'")

def p_func_def_head_block_error(p):
    '''func_def : func_head declarations block'''
    #Line number reported from func_head and block
    print_error("Syntax error at line", p.linespan(1)[1])
    print_error("\tMissing ';'")
    print_error("Syntax error at line", p.linespan(3)[1])
    print_error("\tMissing ';'")

def p_func_head(p):
    '''func_head : KEYWORD_FUNCTION IDENTIFIER parameter_list COLON type_identifier'''
    ST.currSymTab.previousTable.addFunction(p[2], p[5].type, len(p[3].items))
    STEntry = ST.currSymTab.addVar(p[2], p[5].type)
    # TODO Type identifier must be builtin/already defined
    # Generate code
    p[0] = IG.Node()
    p[0].place = STEntry
    p[0].genCode(IG.TACInstr(IG.TACInstr.LABEL, label=p[2], paramList=p[3].items, lineNo=nextQuad))
    nextQuad += 1

def p_func_head_error(p):
    '''func_head : KEYWORD_FUNCTION IDENTIFIER parameter_list error type_identifier'''
    #Line number reported from KEYWORD_FUNCTION token
    print_error("\tExpected :'")

def p_declarations(p):
    '''declarations : declarations const_declarations
                    | declarations type_declarations
                    | declarations var_declarations
                    | empty'''
    p[0] = IG.Node()
    p[0].code = p[1].code + p[2].code

def p_parameter_list(p):
    '''parameter_list : LEFT_PARENTHESIS parameter_declarations RIGHT_PARENTHESIS
                      | LEFT_PARENTHESIS RIGHT_PARENTHESIS'''
    if len(p) == 4:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = IG.Node()

def p_parameter_declarations(p):
    '''parameter_declarations : parameter_declarations SEMICOLON value_parameter
                              | value_parameter'''
    p[0] = IG.Node()
    if len(p) == 4:
        p[0].items = p[1].items + p[3].items
        p[0].code = p[1].code + p[3].code
    elif len(p) == 2:
        p[0] = p[1]

def p_parameter_declarations_error(p):
    '''parameter_declarations : parameter_declarations error value_parameter'''
    print_error("\tExpected ';', Found " + p[2].type)

def p_value_parameter(p):
    '''value_parameter : identifiers COLON type_identifier
                       | IDENTIFIER COLON type_identifier
                       | identifiers COLON KEYWORD_ARRAY KEYWORD_OF type_identifier
                       | IDENTIFIER COLON KEYWORD_ARRAY KEYWORD_OF type_identifier'''
    p[0] = IG.Node()
    if len(p) == 4:
        if type(p[1]) == IG.Node:
            p[0].items = p[1].items
            for item in p[1].items:
                ST.currSymTab.addVar(item, p[3].type, isParameter=True)
        else:
            p[0].items.append(p[1])
            ST.currSymTab.addVar(p[1], p[3].type, isParameter=True)
    elif len(p) == 5:
        if type(p[1]) == IG.Node:
            p[0].items = p[1].items
            for item in p[1].items:
                ST.currSymTab.addVar(item, ST.Type('array', ST.Type.ARRAY, arrayBaseType=p[5].type), isParameter=True)
        else:
            p[0].items.append(p[1])
            ST.currSymTab.addVar(p[1], ST.Type('array', ST.Type.ARRAY, arrayBaseType=p[5].type), isParameter=True)

def p_value_parameter_error(p):
    '''value_parameter : identifiers error type_identifier
                       | IDENTIFIER error type_identifier
                       | identifiers error KEYWORD_ARRAY KEYWORD_OF type_identifier
                       | IDENTIFIER error KEYWORD_ARRAY KEYWORD_OF type_identifier
                       | IDENTIFIER error type_identifier EQUAL unsigned_constant'''
    if len(p) == 6:
        if p[4] == '=':
            print_error("\tDefault parameter values are unsupported.")
    print_error("\tExpected ':', Found " + p[2].type)

def p_block(p):
    'block : KEYWORD_BEGIN statements KEYWORD_END'
    p[0] = p[1]

def p_statements(p):
    '''statements : statements SEMICOLON statement
                  | statement'''
    p[0] = IG.Node()
    if len(p) == 4:
        p[0].code = p[1].code + p[3].code
    elif len(p) == 2:
        p[0].code = p[1].code

def p_statements_error(p):
    '''statements : statements error statement'''
    print_error("\tExpected ';', Found " + p[2].type)

def p_statement(p):
    '''statement : matched_statement
                 | unmatched_statement'''
    p[0] = p[1]

def p_matched_statement(p):
    '''matched_statement : simple_statement
                         | structured_statement
                         | KEYWORD_IF expression KEYWORD_THEN marker_if matched_statement \
                           marker_if_end KEYWORD_ELSE marker_else matched_statement
                         | loop_header matched_statement
                         | KEYWORD_BREAK
                         | KEYWORD_CONTINUE
                         | empty'''
    p[0] = IG.Node()
    if len(p) == 2:
        if type(p[1]) == IG.Node:
            p[0] = p[1]
        else:
            pass
            # TODO: Handle empty production
            # TODO: Generate code for break and continue
    elif len(p) == 10:
        p[0].code = p[2].code + p[4].code + p[5].code + p[6].code + p[9].code
        backpatch([p[4].quad], p[7].quad)
        backpatch([p[6].quad], nextQuad)

    elif len(p) == 3:
        p[0].code = p[1].code + p[2].code

def p_unmatched_statement(p):
    '''unmatched_statement : KEYWORD_IF expression KEYWORD_THEN marker_if statement
                           | KEYWORD_IF expression KEYWORD_THEN marker_if matched_statement \
                             marker_if_end KEYWORD_ELSE marker_else unmatched_statement
                           | loop_header unmatched_statement'''
    #p[0] = Rule('unmatched_statement', get_production(p))
    p[0] = IG.Node()
    if len(p) == 6:
        p[0].code = p[2].code + p[4].code + p[5].code
        backpatch([p[4].quad], nextQuad)

    elif len(p) == 10:
        p[0].code = p[2].code + p[4].code + p[5].code + p[6].code + p[9].code
        backpatch([p[4].quad], p[7].quad)
        backpatch([p[6].quad], nextQuad)

    elif len(p) == 3:
        p[0].code = p[1].code + p[2].code

def p_marker_if(p):
    '''marker_if : '''
    p[0] = IG.Node()
    p[0].genCode(IG.TACInstr(IG.TACInstr.IFGOTO, src1=p[-2].place, src2=False, op=IG.TACInstr.EQ, lineNo=nextQuad))
    p[0].quad = nextQuad
    nextQuad += 1

def p_marker_if_end(p):
    '''marker_if_end : '''
    p[0].IG.Node()
    p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=nextQuad))
    p[0].quad = nextQuad
    nextQuad += 1

def p_marker_else(p):
    '''marker_else : '''
    p[0] = IG.Node()
    p[0].quad = nextQuad

def p_loop_header(p):
    '''loop_header : for_loop_header
                   | while_loop_header'''
    # p[0] = Rule('loop_header', get_production(p))
    p[0] = p[1]

def p_for_loop_header(p):
    '''for_loop_header : for_loop_to
                       | for_loop_downto'''
    # p[0] = Rule('for_loop_header', get_production(p))
    p[0] = p[1]

def p_for_loop_to(p):
    '''for_loop_to : KEYWORD_FOR IDENTIFIER COLON_EQUAL expression KEYWORD_TO expression KEYWORD_DO'''
    p[0] = IG.Node()
    # TODO generate code

def p_for_loop_downto(p):
    '''for_loop_downto : KEYWORD_FOR IDENTIFIER COLON_EQUAL expression KEYWORD_DOWNTO expression KEYWORD_DO'''
    p[0] = IG.Node()
    # TODO generate code

def p_for_loop_header_error(p):
    '''for_loop_header : KEYWORD_FOR IDENTIFIER error expression KEYWORD_TO expression KEYWORD_DO
                       | KEYWORD_FOR IDENTIFIER error expression KEYWORD_DOWNTO expression KEYWORD_DO'''
    p[0] = Rule('for_loop_header', get_production(p))
    print_error("\tExpected ':=', Found " + p[3].type)

def p_while_loop_header(p):
    '''while_loop_header : KEYWORD_WHILE expression KEYWORD_DO'''
    # p[0] = Rule('while_loop_header', get_production(p))
    p[0] = IG.Node()
    # TODO generate code

def p_simple_statement(p):
    '''simple_statement : assignment_statement
                        | func_proc_statement'''
    p[0] = p[1]

def p_assignment_statement(p):
    '''assignment_statement : variable_reference COLON_EQUAL expression'''
    p[0] = IG.Node()
    p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, src1=p[3].place, dest=p[1].place, lineNo=nextQuad))
    nextQuad += 1

def p_assignment_statement_error(p):
    '''assignment_statement : variable_reference error expression'''
    print_error("\tIllegal Expression")

def p_expression(p):
    '''expression : simple_expression relational_operator simple_expression
                  | simple_expression'''
    p[0] = IG.Node()
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0].code = p[1].code + p[3].code
        p[0].place = IG.newTempBool()
        p[0].type = p[0].place.type
        p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[2]], src1=p[1].place,
                                 src2=p[3].place, dest=p[0].place, lineNo=nextQuad))
        nextQuad += 1

def p_simple_expression(p):
    '''simple_expression : simple_expression OP_PLUS term
                         | simple_expression OP_MINUS term
                         | simple_expression OP_OR bool_exp_marker term
                         | simple_expression OP_XOR term
                         | simple_expression OP_BIT_OR term
                         | simple_expression OP_BIT_XOR term
                         | term'''
    p[0] = IG.Node()
    if len(p) == 5:
        backpatch(p[1].falseList, p[3].quad)
        p[0].trueList = p[1].trueList + p[4].trueList
        p[0].falseList = p[4].falseList
        p[0].place = IG.newTempBool()
        p[0].type = p[0].place.type
        p[0].code = p[1].code + p[4].code
        p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.LOGICOR, src1=p[1].place, src2=p[4].place,
                                 dest=p[0].place, lineNo=nextQuad))
        nextQuad += 1

    elif len(p) == 4:
        if p[1].type == p[3].type:
            p[0].place = newTempInt()
            p[0].type = p[0].place.type
            p[0].code = p[1].code + p[3].code
            p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[2]], src1=p[1].place,
                                     src2=p[3].place, dest=p[0].place, lineNo=nextQuad))
            nextQuad += 1
            # TODO Generate Code for other types
        else:
            # TODO Type checking error

    elif len(p) == 2:
        p[0] = p[1]

def p_term(p):
    '''term : term OP_MULT factor
            | term OP_DIV factor
            | term OP_MOD factor
            | term OP_AND bool_exp_marker factor
            | term OP_BIT_AND factor
            | term OP_SHIFTLEFT factor
            | term OP_SHIFTRIGHT factor
            | factor'''

    p[0] = IG.Node()
    if len(p) == 5:
        backpatch(p[1].trueList, p[3].quad)
        p[0].trueList = p[4].trueList
        p[0].falseList = p[1].falseList + p[4].falseList
        p[0].place = IG.newTempBool()
        p[0].type = p[0].place.type
        p[0].code = p[1].code + p[4].code
        p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.LOGICAND, src1=p[1].place, src2=p[4].place,
                                 dest=p[0].place, lineNo=nextQuad))
        nextQuad += 1

    elif len(p) == 4:
        if p[1].type == p[3].type:
            p[0].place = newTempInt()
            p[0].type = p[0].place.type
            p[0].code = p[1].code + p[3].code
            p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[2]], src1=p[1].place,
                                     src2=p[3].place, dest=p[0].place, lineNo=nextQuad))
            nextQuad += 1
            # TODO Generate code for other types
        else:
            # TODO Type checking error
    elif len(p) == 2:
        p[0] = p[1]

def p_factor(p):
    '''factor : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
              | sign factor
              | OP_NOT factor
              | OP_BIT_NOT factor
              | function_call
              | variable_reference
              | unsigned_constant'''
    p[0] = IG.Node()
    if len(p) == 3:
        # TODO Generate Code
        if p[1] == 'not':
            p[0].trueList = p[2].falseList
            p[0].falseList = p[2].trueList
            p[0].place = IG.newTempBool()
            p[0].type = p[0].place.type
            p[0].code = p[2].code
            p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.LOGICNOT, src1=p[2].place,
                                     dest=p[0].place, lineNo=nextQuad))
            nextQuad += 1
        else:
            p[0].place = newTempInt()
            p[0].type = p[0].place.type
            p[0].code = p[2].code
            p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[1]], src1=p[1].place,
                                     dest=p[0].place, lineNo=nextQuad))
            nextQuad += 1
            # TODO generate code for other types

    elif len(p) == 2:
        p[0].code = p[1].code
        if p[1].value == 'true':
            p[0].trueList = [nextQuad]
        elif p[1].value == 'false':
            p[0].falseList = [nextQuad]
        else:
            p[0].trueList = [nextQuad]
            p[0].falseList = [nextQuad+1]
    elif len(p) == 4:
        p[0] = p[2]

def p_bool_exp_marker(p):
    '''bool_exp_marker : '''
    p[0] = IG.Node()
    p[0].quad = nextQuad

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
    p[0] = p[1]

def p_unsigned_constant(p):
    '''unsigned_constant : CONSTANT_INTEGER
                         | CONSTANT_HEX
                         | CONSTANT_BINARY
                         | CONSTANT_OCTAL
                         | CONSTANT_NIL
                         | CONSTANT_BOOLEAN_TRUE
                         | CONSTANT_BOOLEAN_FALSE
                         | string'''
    #p[0] = Rule('unsigned_constant', get_production(p))

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
                           | IDENTIFIER LEFT_PARENTHESIS RIGHT_PARENTHESIS'''
    p[0] = IG.Node()
    if p[1] == 'read' or p[1] == 'readln':
        if len(p[3].items) == 1:
            # TODO Type Readln FIXME
            if p[3].items[0].type.type == ST.Type.INT or 
               (p[3].items[0].type.type == ST.Type.type and p[3].items[0].type.baseType == ST.Type.INT):
                ioFmtString = '%d'
            elif p[3].items[0].type.type == ST.Type.STRING or 
               (p[3].items[0].type.type == ST.Type.type and p[3].items[0].type.baseType == ST.Type.STRING):
                ioFmtString = '%s'
            elif p[3].items[0].type.type == ST.Type.CHAR or 
               (p[3].items[0].type.type == ST.Type.type and p[3].items[0].type.baseType == ST.Type.CHAR):
                ioFmtString = '%c'
            else:
                # TODO ERROR
                pass
                # print_error('Type Not Supported for Read Operation')
            p[0].genCode(IG.TACInstr(IG.TACInstr.SCANF, ioArgList=p[3].items,
                                    ioFmtString=ioFmtString, lineNo=nextQuad))
            nextQuad += 1
    elif p[1] == 'write' or p[1] == 'writeln':
        if len(p[3].items) == 1
            # TODO Type Writeln FIXME
            if p[3].items[0].isInt() or
               (p[3].items[0].isType() and p[3].items[0].type.baseType == ST.Type.INT):
                ioFmtString = '%d'
            elif p[3].items[0].isString() or
               (p[3].items[0].isType() and p[3].items[0].type.baseType == ST.Type.STRING):
                ioFmtString = '%s'
            elif p[3].items[0].isChar() or
               (p[3].items[0].isType() and p[3].items[0].type.baseType == ST.Type.CHAR):
                ioFmtString = '%c'
            else:
                # TODO ERROR
                pass
                # print_error('Type Not Supported for Read Operation')
            p[0].genCode(IG.TACInstr(IG.TACInstr.SCANF, ioArgList=p[3].items,
                                    ioFmtString=ioFmtString, lineNo=nextQuad))
            nextQuad += 1

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
    if p:
        print_error("Syntax error at line", p.lineno)
    else:
        print_error("Syntax error at end of file")

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
    for item in left_list:
        if type(item) is Rule:
            print item.name,
        else:
            print item,
    print '<b>'
    for item in nonterm_to_reduce.production:
        if type(item) is Rule:
            print item.name,
        else:
            print item,
    print '</b>'
    for item in right_list:
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

def print_error(string, *args):
    if args:
        print >> sys.stderr, string, args[0]
    else:
        print >> sys.stderr, string

# Build the parser
parser = yacc.yacc()
