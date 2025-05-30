from lexer import lexer
from parser import parser, semantica, cuadru
import sys

test_cases = [
# program Fugonachi;
#     vars n, a, b, temp : int;
#     void generarFugonachi(n: int) [
#         {
#             a = 0;
#             b = 1;
#             print(a);
#             if (n > 1) {
#                 print(b);
#                 n = n - 2;
#                 while (n > 0) {
#                     temp = a + b;
#                     print(temp);
#                     a = b;
#                     b = temp;
#                     n = n - 1;
#                 };
#             };
#         };
#     ];
#
#     main {
#         n = 7;
#         generarFugonachi(n);
#     }
# end


# program MyProgram;
#     vars x, y : int;
#     vars a :int;
#     void foo(a: int) [
#         {
#             a = 1;
#             print("Dentro de foo");
#         }
#     ];
#     main {
#         x = 3;
#         if (x < 5) {
#             print(x);
#         } else {
#             print("Mayor o igual");
#         };
#     }
#     end


    # Programa mínimo válido
    '''
    program Fugonachi;
    vars n : int;
    
    void generarFugonachi(n: int)
    [
        vars a, b, temp : int;
        {
            a = 0;
            b = 1;
            print(a);
            if (n > 1) {
                print(b);
                n = n - 2;
                while (n > 0) do {
                    temp = a + b;
                    print(temp);
                    a = b;
                    b = temp;
                    n = n - 1;
                };
            };
        }
    ];
    
    main {
        n = 7;
        generarFugonachi(n);
    }
    end

    ''',
    # Prfuebna 2
    # Ciclo while
    '''
    program LoopTest;
    vars x : int;
    main {
        x = 0;
        while (x > 10) do {
            print(x);
            x = x + 1;
        };
    }
    end
    ''',
    # prueba 3
    # llamada de print sencilla para probar errores
    '''program Test;
    main {
        print("Hola");
    }
    end
    ''',
    # Llamada a función con argumentos
    '''
    void show(a: int, b: float) [
    print(a);
    ];
    '''


]



for i, code in enumerate(test_cases):
    print(f"\n--- Test case {i + 1} ---")

    # IMPRIMIR CÓDIGO CON LÍNEAS
    print("Código fuente:")
    for idx, line in enumerate(code.strip().splitlines(), 1):
        print(f"{idx:02d}: {line}")

    result = parser.parse(code, lexer=lexer)
    cuadru.print_quadruples()
    print(result)

    semantica.imprimir_directorio()
    semantica.__init__()
    cuadru.__init__()