from lexer import lexer
from parser import parser, semantica, cuadru
from memoria import Mmemoria
memoria = Mmemoria()
import sys

test_cases = ["""
program SoloTest;
vars x : int;
vars val : int;

void comparar(val: int) [
    vars resultado : int;
    {
        resultado = val + 2;
        print(resultado);
    }
];

main {
    x = 5;
    comparar(x);
}
end
"""]


# def load_tests_from_file(filename):
#     with open(filename, 'r', encoding='utf-8') as f:
#         content = f.read()
#     return [case.strip() for case in content.split('--- TESTCASE ---') if case.strip()]
#
# test_cases = load_tests_from_file("testest.txt")



for i, code in enumerate(test_cases):
    print(f"\n--- Test case {i + 1} ---")

    print("Código fuente:")
    for idx, line in enumerate(code.strip().splitlines(), 1):
        print(f"{idx:02d}: {line}")

    result = parser.parse(code, lexer=lexer)
    # cuadru.print_quadruples()
    # print("nMapa de memoria:")
    # from pprint import pprint

    # pprint(semantica.memoria.memory)
    print(result)

    semantica.imprimir_directorio()
    semantica.__init__()
    cuadru.__init__()
