import ply.yacc as yacc
import sys
import symbol_table as ST
import ircodegen as IG

# Get the token map from the lexer. This is required.
from lexer import tokens

def backpatch(instrList, target):
    for instr in instrList:
        if instr == IG.InstrList[instr].LineNo:
            print 'Backpatching', instr
            IG.InstrList[instr].Target = target
        else:
            print 'Why is this happening!', instr

def p_start(p):
    'start : program_statement global_decs_defs block DOT'
    p[0] = IG.Node()
    p[0].code = p[2].code + p[3].code
    p[0].genCode(IG.TACInstr(IG.TACInstr.RETURN, lineNo=IG.nextQuad))
    IG.nextQuad += 1

def p_program_statement(p):
    '''program_statement : KEYWORD_PROGRAM IDENTIFIER SEMICOLON
                         | empty'''
    if len(p) == 4:
        ST.currSymTab.addVar(p[2], ST.Type('program', ST.Type.PROGRAM))
    else:
        pass

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
        backpatch([p[2].quad], IG.nextQuad)
        p[0].code = p[1].code + p[2].code + p[3].code
    else:
        pass

def p_marker_fpdef(p):
    '''marker_fpdef : '''
    p[0] = IG.Node()
    p[0].quad = IG.nextQuad
    p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=IG.nextQuad))
    IG.nextQuad += 1
    ST.currSymTab = ST.SymTab(ST.currSymTab)

def p_const_declarations(p):
    '''const_declarations : KEYWORD_CONST const_statements'''
    p[0] = p[2]

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
    p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, dest=STEntry, src1=p[3].place, lineNo=IG.nextQuad))
    IG.nextQuad += 1

def p_const_statement_error(p):
    'const_statement : IDENTIFIER EQUAL expression'
    #Line number reported from expression nonterminal
    print_error("Syntax error at line", p.linespan(3)[1])
    print_error("\tMissing ';'")

def p_string(p):
    '''string : CONSTANT_STRING_LEADSPACE substring
              | CONSTANT_STRING_LEADSPACE
              | substring'''

    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = p[1]

    # We need strings with quotes
    p[0] = '"' + p[0] + '"'

def p_substring(p):
    '''substring : CONSTANT_STRING substring
                 | CONSTANT_SPECIAL_CHAR substring
                 | CONSTANT_STRING
                 | CONSTANT_SPECIAL_CHAR'''
    if len(p) == 3:
        if type(p[1]) == str:
            p[0] = p[1] + p[2]
        else:
            p[0] = chr(p[1]) + p[2]
    elif len(p) == 2:
        if type(p[1]) == str:
            p[0] = p[1]
        else:
            p[0] = chr(p[1])

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
            ST.currSymTab.addVar(item, ST.Type(item, ST.Type.TYPE, baseType=p[3].type))
    else:
        ST.currSymTab.addVar(p[1], ST.Type(p[1], ST.Type.TYPE, baseType=p[3].type))

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
        p[0].arrayEndList = p[1].arrayEndList + p[3].arrayEndList
    else:
        p[0].arrayBeginList = p[1].arrayBeginList
        p[0].arrayEndList = p[1].arrayEndList

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
        sys.exit(1)

def p_char_range(p):
    '''char_range : char DOTDOT char'''

    p[0] = IG.Node()
    if (p[1] <= p[3]):
        p[0].arrayBeginList = [p[1]]
        p[0].arrayEndList = [p[3]]
    else:
        print_error("Semantic error at line", p.lineno(3))
        print_error("\tEnd index is less than start index")
        sys.exit(1)

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
    if type(p[1]) == int:
        p[0] = chr(p[1])
    else:
        if len(p[1]) == 1:
            p[0] = p[1]
        else:
            print_error("Semantic error at line", p.lineno(1))
            print_error("\tExpected character got string")
            sys.exit(1)

def p_string_declaration(p):
    '''string_declaration : KEYWORD_STRING LEFT_SQUARE_BRACKETS CONSTANT_INTEGER RIGHT_SQUARE_BRACKETS'''
    p[0] = IG.Node()
    p[0].type = ST.Type('string', ST.Type.TYPE, strLen=p[3])

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
    p[0] = IG.Node()
    if len(p) == 5:
        if type(p[1]) == IG.Node:
            for item in p[1].items:
                STEntry = ST.currSymTab.addVar(item, p[3].type)
                if STEntry.isArray():
                    p[0].genCode(IG.TACInstr(IG.TACInstr.DECLARE, dest='array', src1=p[3].type.arrayBeginList[0],
                                             src2=p[3].type.arrayEndList[0], lineNo=IG.nextQuad))
                    IG.nextQuad += 1
        else:
            STEntry = ST.currSymTab.addVar(p[1], p[3].type)
            if STEntry.isArray():
                p[0].genCode(IG.TACInstr(IG.TACInstr.DECLARE, dest='array', src1=p[3].type.arrayBeginList[0],
                                         src2=p[3].type.arrayEndList[0], lineNo=IG.nextQuad))
                IG.nextQuad += 1

    else:
        STEntry = ST.currSymTab.addVar(p[1], p[3].type)
        p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, dest=STEntry, src1=p[5].place, lineNo=IG.nextQuad))
        IG.nextQuad += 1

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
    ST.currSymTab.previousTable.addTable(ST.currSymTab)
    ST.currSymTab = ST.currSymTab.previousTable
    p[0] = IG.Node()
    p[0].code = p[1].code + p[3].code + p[4].code
    p[0].genCode(IG.TACInstr(IG.TACInstr.RETURN, lineNo=IG.nextQuad))
    IG.nextQuad += 1

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
    p[0].genCode(IG.TACInstr(IG.TACInstr.LABEL, label=p[2], paramList=p[3].items, lineNo=IG.nextQuad))
    IG.nextQuad += 1

def p_func_def(p):
    '''func_def : func_head SEMICOLON declarations block SEMICOLON'''
    ST.currSymTab.previousTable.addTable(ST.currSymTab)
    ST.currSymTab = ST.currSymTab.previousTable
    p[0] = IG.Node()
    p[0].code = p[1].code + p[3].code + p[4].code
    p[0].genCode(IG.TACInstr(IG.TACInstr.RETURN, src1=p[1].place, lineNo=IG.nextQuad))
    IG.nextQuad += 1

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
    TypeSTEntry = ST.lookup(p[5].type.name)
    if TypeSTEntry is not None:
        if TypeSTEntry.isType():
            p[0] = IG.Node()
            p[0].place = STEntry
            p[0].genCode(IG.TACInstr(IG.TACInstr.LABEL, label=p[2], paramList=p[3].items, lineNo=IG.nextQuad))
            IG.nextQuad += 1
        else:
            # Variable given as type
            print_error("Type error at line", p.linespan(5)[1])
            print_error("\tVariable identifer given as return type")
            sys.exit(1)
    else:
        # Undefined type
        print_error("Type error at line", p.linespan(5)[1])
        print_error("\tReturn type is not a built in or predefined type")
        sys.exit(1)

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
    if len(p) == 3:
        p[0].code = p[1].code + p[2].code

def p_parameter_list(p):
    '''parameter_list : LEFT_PARENTHESIS parameter_declarations RIGHT_PARENTHESIS
                      | LEFT_PARENTHESIS RIGHT_PARENTHESIS'''
    if len(p) == 4:
        p[0] = p[2]
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
    p[0] = p[2]

def p_statements(p):
    '''statements : statements SEMICOLON marker_statement statement
                  | statement'''
    p[0] = IG.Node()
    if len(p) == 5:
        p[0].code = p[1].code + p[3].code
        p[0].nextList = p[4].nextList
        backpatch(p[1].nextList, p[3].quad)

    elif len(p) == 2:
        p[0] = p[1]

def p_statements_error(p):
    '''statements : statements error statement'''
    print_error("\tExpected ';', Found " + p[2].type)

def p_marker_statement(p):
    '''marker_statement : '''
    p[0] = IG.Node()
    p[0].quad = IG.nextQuad

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
        print 'test', p[8].quad
        backpatch(p[2].falseList, p[8].quad)
        backpatch(p[2].trueList, p[4].quad)
        p[0].nextList = p[5].nextList + p[6].nextList + p[9].nextList

    elif len(p) == 3:
        p[0].code = p[1].code + p[2].code
        p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, target=p[1].quad, lineNo=IG.nextQuad))
        IG.nextQuad += 1
        backpatch(p[1].endList, IG.nextQuad)

def p_unmatched_statement(p):
    '''unmatched_statement : KEYWORD_IF expression KEYWORD_THEN marker_if statement
                           | KEYWORD_IF expression KEYWORD_THEN marker_if matched_statement \
                             marker_if_end KEYWORD_ELSE marker_else unmatched_statement
                           | loop_header unmatched_statement'''
    p[0] = IG.Node()
    if len(p) == 6:
        p[0].code = p[2].code + p[4].code + p[5].code
        backpatch(p[2].trueList, p[4].quad)
        p[0].nextList = p[2].falseList + p[5].nextList

    elif len(p) == 10:
        p[0].code = p[2].code + p[4].code + p[5].code + p[6].code + p[9].code
        backpatch(p[2].falseList, p[8].quad)
        backpatch(p[2].trueList, p[4].quad)
        p[0].nextList = p[5].nextList + p[6].nextList + p[9].nextList

    elif len(p) == 3:
        p[0].code = p[1].code + p[2].code
        p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, target=p[1].quad, lineNo=IG.nextQuad))
        IG.nextQuad += 1
        backpatch(p[1].endList, IG.nextQuad)

def p_marker_if(p):
    '''marker_if : '''
    p[0] = IG.Node()
    # p[0].genCode(IG.TACInstr(IG.TACInstr.IFGOTO, src1=p[-2].place, src2=False, op=IG.TACInstr.EQ, lineNo=IG.nextQuad))
    p[0].quad = IG.nextQuad
    # IG.nextQuad += 1

def p_marker_if_end(p):
    '''marker_if_end : '''
    p[0] = IG.Node()
    p[0].nextList = [IG.nextQuad]
    p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=IG.nextQuad))
    IG.nextQuad += 1

def p_marker_else(p):
    '''marker_else : '''
    p[0] = IG.Node()
    p[0].quad = IG.nextQuad

def p_loop_header(p):
    '''loop_header : for_loop_header
                   | while_loop_header'''
    p[0] = p[1]

def p_for_loop_header(p):
    '''for_loop_header : for_loop_to
                       | for_loop_downto'''
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
    print_error("\tExpected ':=', Found " + p[3].type)

def p_while_loop_header(p):
    '''while_loop_header : KEYWORD_WHILE marker_while_begin expression marker_while KEYWORD_DO'''
    p[0] = IG.Node()
    p[0].code = p[3].code + p[4].code
    p[0].endList = [p[4].quad]
    p[0].quad = p[2].quad

def p_marker_while_begin(p):
    '''marker_while_begin : '''
    p[0] = IG.Node()
    p[0].quad = IG.nextQuad

def p_marker_while(p):
    '''marker_while : '''
    p[0] = IG.Node()
    p[0].genCode(IG.TACInstr(IG.TACInstr.IFGOTO, src1=p[-1].place, src2=False, op=IG.TACInstr.EQ, lineNo=IG.nextQuad))
    p[0].quad = IG.nextQuad
    IG.nextQuad += 1

def p_simple_statement(p):
    '''simple_statement : assignment_statement
                        | func_proc_statement'''
    p[0] = p[1]

def p_assignment_statement(p):
    '''assignment_statement : variable_reference COLON_EQUAL expression'''
    p[0] = IG.Node()
    p[0].nextList = p[3].nextList
    p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, src1=p[3].place, dest=p[1].place, lineNo=IG.nextQuad))
    IG.nextQuad += 1

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
        # p[0].place = IG.newTempBool()
        # p[0].type = p[0].place.type
        # p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[2]], src1=p[1].place,
        #                          src2=p[3].place, dest=p[0].place, lineNo=IG.nextQuad))
        p[0].trueList = [IG.nextQuad]
        p[0].falseList = [IG.nextQuad+1]
        print 'Given src2', p[3].place
        print "Truelist", p[0].trueList
        print "Falselist", p[0].falseList
        p[0].genCode(IG.TACInstr(IG.TACInstr.IFGOTO, op=IG.TACInstr.OpMap[p[2]], src1=p[1].place,
                                 src2=p[3].place, lineNo=IG.nextQuad))
        IG.nextQuad += 1
        p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=IG.nextQuad))
        IG.nextQuad += 1

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
        p[0].code = p[1].code + p[4].code
        # p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.LOGICOR, src1=p[1].place, src2=p[4].place,
        #                          dest=p[0].place, lineNo=IG.nextQuad))
        # IG.nextQuad += 1

    elif len(p) == 4:
        if p[1].type == p[3].type:
            p[0].place = IG.newTempInt()
            p[0].type = p[0].place.type
            p[0].code = p[1].code + p[3].code
            p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[2]], src1=p[1].place,
                                     src2=p[3].place, dest=p[0].place, lineNo=IG.nextQuad))
            IG.nextQuad += 1
            # TODO Generate Code for other types
        else:
            # TODO Type checking error
            pass

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
        # p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.LOGICAND, src1=p[1].place, src2=p[4].place,
        #                          dest=p[0].place, lineNo=IG.nextQuad))
        # IG.nextQuad += 1

    elif len(p) == 4:
        if p[1].type == p[3].type:
            p[0].place = IG.newTempInt()
            p[0].type = p[0].place.type
            p[0].code = p[1].code + p[3].code
            p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[2]], src1=p[1].place,
                                     src2=p[3].place, dest=p[0].place, lineNo=IG.nextQuad))
            IG.nextQuad += 1
            # TODO Generate code for other types
        else:
            # TODO Type checking error
            pass
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
            p[0].code = p[2].code
        #    p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.LOGICNOT, src1=p[2].place,
        #                             dest=p[0].place, lineNo=IG.nextQuad))
        #    IG.nextQuad += 1
        else:
            p[0].place = IG.newTempInt()
            p[0].type = p[0].place.type
            p[0].code = p[2].code
            p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.OpMap[p[1]], src1=p[1].place,
                                     dest=p[0].place, lineNo=IG.nextQuad))
            IG.nextQuad += 1
            # TODO generate code for other types

    elif len(p) == 2:
        p[0] = p[1]
        # TODO handle case for if boolean then  ...
        if p[1].place == 'true':
            p[0].trueList = [IG.nextQuad]
            #p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=IG.nextQuad))
            #IG.nextQuad += 1

        elif p[1].place == 'false':
            p[0].falseList = [IG.nextQuad]
            #p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=IG.nextQuad))
            #IG.nextQuad += 1

        elif type(p[1].place) == ST.SymTabEntry and p[1].place.isBool():
            p[0].trueList = [IG.nextQuad]
            p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=IG.nextQuad))
            IG.nextQuad += 1
            p[0].falseList = [IG.nextQuad]
            p[0].genCode(IG.TACInstr(IG.TACInstr.GOTO, lineNo=IG.nextQuad))
            IG.nextQuad += 1

    elif len(p) == 4:
        p[0].place = p[2].place
        p[0].type = p[2].type
        p[0].trueList = p[2].trueList
        p[0].falseList = p[2].falseList

def p_bool_exp_marker(p):
    '''bool_exp_marker : '''
    p[0] = IG.Node()
    p[0].quad = IG.nextQuad

def p_function_call(p):
    '''function_call : IDENTIFIER LEFT_PARENTHESIS expression_list RIGHT_PARENTHESIS
                     | IDENTIFIER LEFT_PARENTHESIS RIGHT_PARENTHESIS'''
    p[0] = IG.Node()
    if len(p) == 4:
        p[0].place = IG.newTempInt()
        p[0].type = p[0].place.type
        p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.CALLOP,
                                 dest=p[0].place, targetLabel=p[1], lineNo=IG.nextQuad))
        IG.nextQuad += 1
    elif len(p) == 5:
        p[0].place = IG.newTempInt()
        p[0].type = p[0].place.type
        p[0].genCode(IG.TACInstr(IG.TACInstr.ASSIGN, op=IG.TACInstr.CALLOP,
                                 dest=p[0].place, lineNo=IG.nextQuad, paramList=p[3].items, targetLabel=p[1]))
        IG.nextQuad += 1

def p_expression_list(p):
    '''expression_list : expression_list COMMA expression
                       | expression'''
    p[0] = IG.Node()
    if len(p) == 4:
        p[0].items = p[1].items + [p[3].place]
    else:
        p[0].items = [p[1].place]

def p_variable_reference(p):
    '''variable_reference : IDENTIFIER
                          | IDENTIFIER LEFT_SQUARE_BRACKETS array_index RIGHT_SQUARE_BRACKETS
                          | IDENTIFIER array_index_cstyle'''

    p[0] = IG.Node()
    STEntry = ST.lookup(p[1])
    if STEntry:
        if len(p) == 2:
            p[0].place = STEntry
            p[0].type = STEntry.type
        elif len(p) == 3:
            p[0].place = IG.ArrayElement(STEntry, p[2].place)

def p_array_index(p):
    '''array_index : array_index COMMA expression
                   | expression COMMA expression'''

def p_array_index_cstyle(p):
    '''array_index_cstyle : array_index_cstyle LEFT_SQUARE_BRACKETS expression RIGHT_SQUARE_BRACKETS
                   | LEFT_SQUARE_BRACKETS expression RIGHT_SQUARE_BRACKETS'''
    p[0] = IG.Node()
    if len(p) == 4:
        p[0] = p[2]
    else:
        # TODO Handle Multi Dimensional
        pass

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
    p[0] = IG.Node()
    p[0].place = p[1]
    if type(p[1]) == int:
        p[0].type = ST.Type('integer', ST.Type.INT)
    elif type(p[1]) == str:
        if p[1] == 'true' or p[1] == 'false':
            p[0].type = ST.Type('boolean', ST.Type.BOOL)
        else:   # TODO Nil is string FIXME
            p[0].type = ST.Type('string', ST.Type.STRING)

def p_relational_operator(p):
    '''relational_operator : OP_NEQ
                           | OP_GT
                           | OP_LT
                           | OP_GEQ
                           | OP_LEQ
                           | EQUAL'''
    p[0] = p[1]

def p_func_proc_statement(p):
    '''func_proc_statement : IDENTIFIER LEFT_PARENTHESIS expression_list RIGHT_PARENTHESIS
                           | IDENTIFIER LEFT_PARENTHESIS RIGHT_PARENTHESIS'''
    p[0] = IG.Node()
    if len(p) == 5:
        if p[1] == 'read' or p[1] == 'readln':
            if len(p[3].items) == 1:
                # TODO Type Readln FIXME
                if p[3].items[0].getDeepestType() == ST.Type.INT:
                    ioFmtString = '"%d"'
                elif p[3].items[0].getDeepestType() == ST.Type.STRING:
                    ioFmtString = '"%s"'
                elif p[3].items[0].getDeepestType() == ST.Type.CHAR:
                    ioFmtString = '"%c"'
                else:
                    # TODO ERROR
                    pass
                    # print_error('Type Not Supported for Read Operation')
                ioArgList = [IG.Operand(item) for item in p[3].items]
                p[0].genCode(IG.TACInstr(IG.TACInstr.SCANF, ioArgList=ioArgList,
                                        ioFmtString=ioFmtString, lineNo=IG.nextQuad))
                IG.nextQuad += 1
        elif p[1] == 'write' or p[1] == 'writeln':
            if len(p[3].items) == 1:
                # TODO Type Writeln FIXME
                if type(p[3].items[0]) == ST.SymTabEntry or type(p[3].items[0]) == IG.ArrayElement:
                    #print p[3].items[0].type.name, p[3].items[0].type.getDeepestType()
                    if p[3].items[0].type.getDeepestType() == 'integer':
                        ioFmtString = '%d'
                    elif p[3].items[0].type.getDeepestType() == 'string':
                        ioFmtString = '%s'
                    elif p[3].items[0].type.getDeepestType() == 'char':
                        ioFmtString = '%c'
                    else:
                        # TODO ERROR
                        pass
                        # print_error('Type Not Supported for Read Operation')
                else:
                    if type(p[3].items[0]) == int:
                        ioFmtString = '%d'
                    elif type(p[3].items[0]) == str and len(p[3].items[0]) == 1:
                        ioFmtString = '%c'
                    elif type(p[3].items[0]) == str:
                        ioFmtString = '%s'
                        # TODO Error
                        pass
                if p[1] == 'writeln':
                    ioFmtString += '\\n'
                ioFmtString = '"' + ioFmtString + '"'
                ioArgList = [IG.Operand(item) for item in p[3].items]
                p[0].genCode(IG.TACInstr(IG.TACInstr.PRINTF, ioArgList=ioArgList,
                                        ioFmtString=ioFmtString, lineNo=IG.nextQuad))
                IG.nextQuad += 1
        else:
            STEntry = ST.lookup(p[1])
            if STEntry and (STEntry.isFunction() or STEntry.isProcedure()):
                p[0].genCode(IG.TACInstr(IG.TACInstr.CALL, paramList=p[3].items, lineNo=IG.nextQuad, targetLabel=p[1]))
                IG.nextQuad += 1

    else:
        STEntry = ST.lookup(p[1])
        if STEntry and (STEntry.isFunction() or STEntry.isProcedure()):
            p[0].genCode(IG.TACInstr(IG.TACInstr.CALL, paramList=[], lineNo=IG.nextQuad, targetLabel=p[1]))
            IG.nextQuad += 1
        else:
            # TODO Type Checking Error
            pass

def p_structured_statement(p):
    '''structured_statement : block
                            | repeat_statement'''
    p[0] = p[1]

def p_repeat_statement(p):
    '''repeat_statement : KEYWORD_REPEAT statements KEYWORD_UNTIL expression'''


def p_empty(p):
    'empty :'

# Error rule for syntax errors
def p_error(p):
    if p:
        print_error("Syntax error at line", p.lineno)
    else:
        print_error("Syntax error at end of file")

def print_error(string, *args):
    if args:
        print >> sys.stderr, string, args[0]
    else:
        print >> sys.stderr, string

# Build the parser
parser = yacc.yacc()
