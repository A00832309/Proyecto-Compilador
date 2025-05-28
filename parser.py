from analizadorsemantico import analizadorsemantico  # Importa la clase directamente
import ply.yacc as yacc
from lexer import tokens
import sys

semantica = analizadorsemantico()

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

    semantica.declarar_fucion(func_name, 'void', [(name, typ) for _, name, typ in params])
    semantica.enter_scope(func_name)

    if isinstance(p[6], tuple):  # <-- Solución aquí
        for var_id in p[6][1]:
            semantica.declare_var(var_id, p[6][2])

    semantica.entorno_actual = 'global'
    p[0] = ('FUNC_DECL', func_name, params, p[6], p[7])




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
    var_type = semantica.obtener_tipo_variable(p[1])
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

    resultado = semantica.checar_operador(var_type, '=', expr_type)
    p[0] = ('ASSIGN', p[1], p[3])


# ------------------------------------------------------------------------------
# se encuentra como el <condition>
def p_condition(p):
    '''condition : IF LPAREN expression RPAREN body else_part SEMI'''
    p[0] = ('IF', p[3], p[5], p[6])

def p_else_part(p):
    '''else_part : ELSE body
                 | empty'''
    p[0] = p[2] if len(p) > 1 else None

# ------------------------------------------------------------------------------
# declarado como <cycle>
def p_loop(p):
    '''loop : WHILE LPAREN expression RPAREN DO body SEMI'''
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
    '''local_vars : vars_decl
                  | empty'''
    p[0] = p[1]
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
    if len(p) == 2:
        p[0] = p[1]
    else:
        semantica.pila_operadores.append(p[2])
        semantica.generar_cuadruplo()
        p[0] = ('RELOP', p[2], p[1], p[3])


# Definido en el documento con <EXP>
def p_simple_expression(p):
    '''simple_expression : term
                         | term PLUS simple_expression
                         | term MINUS simple_expression'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        op = p[2]

        if isinstance(p[1], tuple):
            if p[1][0] == 'ID':
                left_type = p[1][2][1]
            elif p[1][0] == 'CONST':
                left_type = p[1][2][1]
            elif isinstance(p[1][-1], tuple) and p[1][-1][0] == 'TYPE':
                left_type = p[1][-1][1]
            else:
                raise Exception(f"No se pudo extraer tipo izquierdo: {p[1]}")
        else:
            left_type = p[1]

        if isinstance(p[3], tuple):
            if p[3][0] == 'ID':
                right_type = p[3][2][1]
            elif p[3][0] == 'CONST':
                right_type = p[3][2][1]
            elif isinstance(p[3][-1], tuple) and p[3][-1][0] == 'TYPE':
                right_type = p[3][-1][1]
            else:
                raise Exception(f"No se pudo extraer tipo derecho: {p[3]}")
        else:
            right_type = p[3]

        resultado = semantica.checar_operador(left_type, op, right_type)

        p[0] = ('SUMIN', op, p[1], p[3], ('TYPE', resultado))

# -------------------------------------------------------------------------------
# definida como <termino>
def p_term(p):
    '''term : factor
            | factor mulop term'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        semantica.pila_operadores.append(p[2])
        semantica.generar_cuadruplo()
        p[0] = ('MULOP', p[2], p[1], p[3])

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
        p[0] = ('ID', p[1], ('TYPE', tipo))
    else:
        p[0] = p[1]

# --------------------------------------------------------------------------


def p_cte(p):
    '''cte : CTE_INT
           | CTE_FLOAT'''
    p[0] = ('CONST', p[1], ('TYPE', 'int' if isinstance(p[1], int) else 'float'))

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
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\
# cuadruplos

def p_expresion_binaria(p):
    '''expresion : expresion PLUS termino
                 | expresion MINUS termino'''
    p[0] = None
    semantica.pila_operadores.append(p[2])
    semantica.generar_cuadruplo()

def p_termino_binario(p):
    '''termino : termino MULT factor
               | termino DIV factor'''
    p[0] = None
    semantica.pila_operadores.append(p[2])
    semantica.generar_cuadruplo()

def p_factor_num(p):
    'factor : NUMBER'
    semantica.pila_operandos.append(p[1])
    semantica.pila_tipos.append('int')
    p[0] = p[1]

def p_factor_id(p):
    'factor : ID'
    tipo = semantica.obtener_tipo_variable(p[1])
    if isinstance(tipo, Exception):
        raise tipo
    semantica.pila_operandos.append(p[1])
    semantica.pila_tipos.append(tipo)
    p[0] = p[1]

def p_asignacion(p):
    'asignacion : ID EQ expresion'
    tipo_id = semantica.obtener_tipo_variable(p[1])
    tipo_exp = semantica.pila_tipos.pop()
    resultado = semantica.pila_operandos.pop()

    if tipo_id != tipo_exp:
        raise Exception(f"Error de tipo en asignación: {tipo_id} = {tipo_exp}")

    semantica.cuadruplos.append(('=', resultado, None, p[1]))


for i, cuad in enumerate(semantica.cuadruplos):
    print(f"{i}: {cuad}")
parser = yacc.yacc()



