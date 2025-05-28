from lexer import lexer
from parser import parser, semantica
import sys


test_cases = [
    # Programa mínimo válido
    '''
    program MyProgram;
    vars x, y : int;
    vars a :int;
    void foo(a: int) [  
        {
            a = 1;
            print("Dentro de foo");
        }
    ];
    main {
        x = 3;
        if (x < 5) {
            print(x);
        } else {
            print("Mayor o igual");
        };
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
        while (x < 10) do {
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
    result = parser.parse(code, lexer=lexer)
    print(result)

    semantica.imprimir_directorio()
    semantica.__init__()