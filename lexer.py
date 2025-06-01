import ply.lex as lex

# Palabras reservadas
reserved = {
    'do': 'DO',
    'while': 'WHILE',
    'print': 'PRINT',
    'void': 'VOID',
    'end': 'END',
    'program': 'PROGRAM',
    'if': 'IF',
    'else': 'ELSE',
    'int': 'INT',
    'float': 'FLOAT',
    'main': 'MAIN',
    'vars': 'VAR'
}

# Tokens
tokens = [
    'ID',
    'CTE_INT', 'CTE_FLOAT', 'CTE_STRING',
    'PLUS', 'MINUS', 'MULT', 'DIV',
    'LT', 'GT', 'EQ', 'NEQ',
    'LPAREN', 'RPAREN', 'SEMI', 'COLON', 'LBRACE', 'RBRACE', 'COMMA', 'LCO', 'RCO',
    # 'IGUA'
] + list(reserved.values())

# Expresiones regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_LT = r'<'
t_GT = r'>'
t_EQ = r'='
t_NEQ = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMI = r';'
t_COLON = r':'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_LCO = r'\['
t_RCO = r'\]'
# t_IGUA = r'=='

# Ignorar espacios y tabs
t_ignore = ' \t'

# Identificadores o palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Constantes numéricas (enteras y flotantes)
def t_CTE_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CTE_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Constantes de cadena
def t_CTE_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]  # Remover las comillas
    return t

# Nueva línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Comentarios (para ignorar)
def t_COMMENT(t):
    r'\#.*'
    pass

# Errores
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()
