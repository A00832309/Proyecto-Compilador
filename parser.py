from analizadorsemantico import analizadorsemantico
import ply.yacc as yacc
from cuadruplos import CuadruplosMan
from lexer import tokens
import sys

semantica = analizadorsemantico()
cuadru = CuadruplosMan()


def p_program(p):
    '''program : PROGRAM ID SEMI vars_decls func_decls MAIN body END'''
    p[0] = ('PROGRAM', p[2], p[4], p[5], p[7])


def p_func_decls(p):
    '''func_decls : func_decl func_decls
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + (p[2] if p[2] else [])
    else:
        p[0] = []

# ------------------------------------------------------------------------------
# Esta escrita como <func>
def p_func_decl(p):
    '''func_decl : VOID ID LPAREN params RPAREN LCO local_vars body RCO SEMI'''
    func_name = p[2]


    params = p[4] or []
    semantica.enter_scope(func_name)
    semantica.declarar_fucion(func_name, 'void', [(name, typ) for _, name, typ in params])

    local_decls = p[6] if p[6] else []
    for decl in local_decls:
        if decl and decl[0] == 'VARS_DECL':
            ids = decl[1]
            tipo = decl[2]
            for var_id in ids:
                semantica.declarar_variable(var_id, tipo)

    semantica.entorno_salida()
    print("PARSING FUNC OK:", func_name)
    p[0] = ('FUNC_DECL', func_name, params, local_decls, p[7])


def p_params(p):
    '''params : param_list
              | empty'''
    p[0] = p[1]

def p_param_list(p):
    '''param_list : ID COLON type
                 | ID COLON type COMMA param_list'''
    if len(p) == 4:
        p[0] = [('param', p[1], p[3])]
    else:
        p[0] = [('param', p[1], p[3])] + p[5]


# ------------------------------------------------------------------------------------------------
# Declarado como <body>

def p_body(p):
    '''body : LBRACE statements RBRACE'''
    p[0] = p[2]

# -----------------------------------------------------------------------------------------------------
def p_statements(p):
    '''statements : statement statements
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + (p[2] if p[2] else [])
    else:
        p[0] = []
# Declarado como <statment>

def p_statement(p):
    '''statement : assignment
                 | condition
                 | loop
                 | func_call
                 | print_stmt'''

    p[0] = p[1] if len(p) > 1 else None
# ---------------------------------------------------------------------------------
# se encuentra como <ASSING>
def p_assignment(p):
    '''assignment : ID EQ expression SEMI'''
    var = p[1]
    var_type = semantica.obtener_tipo_variable(var)

    if isinstance(p[3], tuple):
        if p[3][0] == 'CONST':
            expr_type = p[3][2][1]
        elif p[3][0] == 'ID':
            expr_type = p[3][2][1]
        elif isinstance(p[3][-1], tuple) and p[3][-1][0] == 'TYPE':
            expr_type = p[3][-1][1]
        else:
            raise Exception(f"No se pudo extraer tipo de la expresión: {p[3]}")
    else:
        expr_type = p[3]

    semantica.checar_operador(var_type, '=', expr_type)

    valor = cuadru.operandos.pop()
    cuadru.tipos.pop()

    cuadru.operandos.append(valor)
    cuadru.tipos.append(expr_type)

    cuadru.operandos.append(var)
    cuadru.tipos.append(var_type)

    cuadru.asigna()

    p[0] = ('ASSIGN', var, p[3])


# ------------------------------------------------------------------------------
# se encuentra como el <condition>
def p_condition(p):
    '''condition : IF LPAREN expression RPAREN body else_part SEMI'''
    exp = p[3]
    # print("DEBUG condition - Tipos:", cuadru.tipos)
    # print("DEBUG condition - Operandos:", cuadru.operandos)

    if not cuadru.tipos or not cuadru.operandos:
        raise Exception("Error: pila vacía al evaluar la condición IF")

    tipo = cuadru.tipos.pop()
    resultado = cuadru.operandos.pop()
    print("Condition type", tipo)
    if tipo != 'bool':
        raise Exception("Condición no booleana en IF")

    false_jump_index = len(cuadru.cuadruplos)
    cuadru.cuadruplos.append(('GOTOF', resultado, None, None))
    cuadru.saltos.append(false_jump_index)

    p[5]  # body

    if p[6]:  # hay else
        goto_end_index = len(cuadru.cuadruplos)
        cuadru.cuadruplos.append(('GOTO', None, None, None))

        end_if_index = len(cuadru.cuadruplos)
        gotof_index = cuadru.saltos.pop()
        cuadru.cuadruplos[gotof_index] = ('GOTOF', resultado, None, end_if_index)

        cuadru.cuadruplos[goto_end_index] = ('GOTO', None, None, len(cuadru.cuadruplos))
    else:
        end_if_index = len(cuadru.cuadruplos)
        gotof_index = cuadru.saltos.pop()
        cuadru.cuadruplos[gotof_index] = ('GOTOF', resultado, None, end_if_index)

    p[0] = ('IF', exp, p[5], p[6])


def p_else_part(p):
    '''else_part : ELSE body
                 | empty'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None

    # if len(p) > 1:
    #     goto_end = len(cuadru.cuadruplos)
    #     cuadru.cuadruplos.append(('GOTO', None, None, None))
    #
    #     end_if = len(cuadru.cuadruplos)
    #     gotof_index = cuadru.saltos.pop()
    #     cuadru.cuadruplos[gotof_index] = ('GOTOF', cuadru.operandos[-1], None, end_if)
    #
    #     cuadru.saltos.append(goto_end)
    #     p[0] = p[2]
    # else:
    #     p[0] = None
# ------------------------------------------------------------------------------
# declarado como <cycle>
def p_loop(p):
    '''loop : WHILE LPAREN expression RPAREN DO body SEMI'''
    # p[0] = ('WHILE', p[3], p[6])

    loop_start = len(cuadru.cuadruplos)

    if not cuadru.tipos or not cuadru.operandos:
        raise Exception("Error: pila vacía al evaluar la condición WHILE")

    tipo = cuadru.tipos.pop()
    resultado = cuadru.operandos.pop()

    if tipo != 'bool':
        raise Exception("Condición no booleana en WHILE")

    # Salto falso si la condición es falsa
    false_jump_index = len(cuadru.cuadruplos)
    cuadru.cuadruplos.append(('GOTOF', resultado, None, None))
    cuadru.saltos.append(false_jump_index)

    # Ejecutar body del ciclo
    p[6]

    cuadru.cuadruplos.append(('GOTO', None, None, loop_start))

    end_loop = len(cuadru.cuadruplos)
    gotof_index = cuadru.saltos.pop()
    cuadru.cuadruplos[gotof_index] = ('GOTOF', resultado, None, end_loop)

    p[0] = ('WHILE', p[3], p[6])


# ------------------------------------------------------------------------------
# Declarada en el documento como <fcall>
def p_func_call(p):
    '''func_call : ID LPAREN args RPAREN SEMI'''
    argumento = p[3] or []
    tipos_argumentos = [a[2][1] for a in argumento]
    semantica.validar_fun_call(p[1], tipos_argumentos)
    p[0] = ('FUNC_CALL', p[1], argumento)

# Parte dde <facall>
def p_args(p):
    '''args : expression_list
            | empty'''
    p[0] = p[1] if len(p) > 1 else None

# parte de <args>
def p_expression_list(p):
    '''expression_list : expression
                       | expression COMMA expression_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


# -------------------------------------------------------------------------------------------
# Es el <print>
def p_print_stmt(p):
    '''print_stmt : PRINT LPAREN print_args RPAREN SEMI'''
    # p[0] = ('PRINT', p[3])
    if p[3]:
        for val in p[3]:
            if isinstance(val, tuple) and val[0] != 'CONST':
                # Es expresión numérica, sacar operandos
                if cuadru.operandos:
                    cuadru.operandos.pop()
                    cuadru.tipos.pop()
    p[0] = ('PRINT', p[3])


def p_print_args(p):
    '''print_args : print_list
                  | empty'''
    p[0] = p[1]

def p_print_list(p):
    '''print_list : printable
                 | printable COMMA print_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_printable(p):
    '''printable : expression
                | CTE_STRING'''
    p[0] = p[1]
# -----------------------------------------------------------------------------------
# todas las variables
def p_vars_decls(p):
    '''vars_decls : vars_decl vars_decls
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + (p[2] if p[2] else [])
    else:
        p[0] = []

def p_vars_decl(p):
    '''vars_decl : VAR ID list_ids COLON type SEMI'''
    ids = [p[2]] + p[3]
    for var_id in ids:
        semantica.declarar_variable(var_id, p[5])
    p[0] = ('VARS_DECL', ids, p[5])

def p_list_ids(p):
    '''list_ids : COMMA ID list_ids
                | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_local_vars(p):
    '''local_vars : vars_decl local_vars
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + (p[2] if p[2] else [])
    else:
        p[0] = []

# ------------------------------------------------------------------------------
def p_type(p):
    '''type : INT
            | FLOAT'''
    p[0] = p[1]
# --------------------------------------------------------------------------------------------
# definido en el documento <EXPRESION>
def p_expression(p):
    '''expression : simple_expression
                  | simple_expression relop simple_expression'''
    # if len(p) == 2:
    #     p[0] = p[1]
    # else:
    #     p[0] = ('RELOP', p[2], p[1], p[3])
    if len(p) == 2:
        p[0] = p[1]
    else:
        left = p[1]
        right = p[3]
        op = p[2]

        left_val = left[1] if isinstance(left, tuple) else left
        right_val = right[1] if isinstance(right, tuple) else right

        left_type = left[2][1] if isinstance(left, tuple) and left[2][0] == 'TYPE' else None
        right_type = right[2][1] if isinstance(right, tuple) and right[2][0] == 'TYPE' else None

        result_type = semantica.checar_operador(left_type, op, right_type)

        cuadru.operandos.pop()
        cuadru.operandos.pop()
        cuadru.tipos.pop()
        cuadru.tipos.pop()

        temp = cuadru.nuevo_temp()
        cuadru.cuadruplos.append((op, left_val, right_val, temp))

        cuadru.operandos.append(temp)
        cuadru.tipos.append(result_type)

        p[0] = ('RELOP', op, left, right, ('TYPE', result_type))

        # print("AFTER expression - Tipos:", cuadru.tipos)
        # print("AFTER expression - Operandos:", cuadru.operandos)


# Definido en el documento con <EXP>
def p_simple_expression(p):
    '''simple_expression : term
                         | term PLUS simple_expression
                         | term MINUS simple_expression'''
    #
    if len(p) == 2:
        p[0] = p[1]
    else:
        op = p[2]
        left = p[1]
        right = p[3]
        left_val = left[1] if isinstance(left, tuple) else left
        right_val = right[1] if isinstance(right, tuple) else right
        left_type = left[2][1] if isinstance(left, tuple) and left[2][0] == 'TYPE' else None
        right_type = right[2][1] if isinstance(right, tuple) and right[2][0] == 'TYPE' else None

        result_type = semantica.checar_operador(left_type, op, right_type)
        cuadru.operandos.pop()
        cuadru.operandos.pop()
        cuadru.tipos.pop()
        cuadru.tipos.pop()
        temp = cuadru.nuevo_temp()
        cuadru.cuadruplos.append((op, left_val, right_val, temp))
        cuadru.operandos.append(temp)
        cuadru.tipos.append(result_type)

        p[0] = ('SUMIN', op, left, right, ('TYPE', result_type))


# -------------------------------------------------------------------------------
# definida como <termino>
def p_term(p):
    '''term : factor
            | factor mulop term'''
    # if len(p) == 2:
    #     p[0] = p[1]
    # else:
    #     p[0] = ('MULOP', p[2], p[1], p[3])
    if len(p) == 2:
        p[0] = p[1]
    else:
        op = p[2]
        left = p[1]
        right = p[3]
        left_val = left[1] if isinstance(left, tuple) else left
        right_val = right[1] if isinstance(right, tuple) else right
        left_type = left[2][1] if isinstance(left, tuple) and left[2][0] == 'TYPE' else None
        right_type = right[2][1] if isinstance(right, tuple) and right[2][0] == 'TYPE' else None
        result_type = semantica.checar_operador(left_type, op, right_type)
        cuadru.operandos.pop()
        cuadru.operandos.pop()
        cuadru.tipos.pop()
        cuadru.tipos.pop()
        temp = cuadru.nuevo_temp()
        cuadru.cuadruplos.append((op, left_val, right_val, temp))
        cuadru.operandos.append(temp)
        cuadru.tipos.append(result_type)
        p[0] = ('MULOP', op, left, right, ('TYPE', result_type))
# -------------------------------------------------------------------------------
# definido como <factor>
def p_factor(p):
    '''factor : LPAREN expression RPAREN
              | facestrc '''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

# Parte de factor
def p_facestrc(p):
    '''facestrc : PLUS faciden
                | MINUS faciden
                | faciden '''
    if len(p) == 3:
        p[0] = ('UNARY', p[1], p[2])
    else:
        p[0] = p[1]


def p_faciden(p):
    ''' faciden : ID
                | cte'''
    if isinstance(p[1], str):
        tipo = semantica.obtener_tipo_variable(p[1])
        cuadru.operandos.append(p[1])
        cuadru.tipos.append(tipo)
        p[0] = ('ID', p[1], ('TYPE', tipo))
    else:
        p[0] = p[1]

# --------------------------------------------------------------------------


def p_cte(p):
    '''cte : CTE_INT
           | CTE_FLOAT'''
    # p[0] = ('CONST', p[1], ('TYPE', 'int' if isinstance(p[1], int) else 'float'))
    tipo = 'int' if isinstance(p[1], int) else 'float'
    cuadru.operandos.append(p[1])
    cuadru.tipos.append(tipo)
    p[0] = ('CONST', p[1], ('TYPE', tipo))


def p_relop(p):
    '''relop : LT
             | GT
             | NEQ'''
    p[0] = p[1]


def p_mulop(p):
    '''mulop : MULT
             | DIV'''
    p[0] = p[1]



def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' (line {p.lineno})")
    else:
        print("Syntax error at EOF")
    sys.exit(1)

parser = yacc.yacc()
