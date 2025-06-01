from memoria import Mmemoria
from analizadorsemantico import analizadorsemantico
semantica = analizadorsemantico()


class CuadruplosMan:
    def __init__(self):
        self.operadores = []
        self.operandos = []
        self.tipos = []
        self.cuadruplos = []
        self.saltos = []
        self.temp_counter = 0
        self.memoria = Mmemoria()

    def nuevo_temp(self, tipo):
        return semantica.memoria.get_temp_address(tipo)

    def genera_cuadruplo(self, operador):
        if len(self.operandos) < 2 or len(self.tipos) < 2:
            raise Exception("Error: pila insuficiente para generar cuádruplo")

        der = self.operandos.pop()
        izq = self.operandos.pop()
        tipo_der = self.tipos.pop()
        tipo_izq = self.tipos.pop()

        if operador in ['+', '-', '*', '/']:
            result_type = tipo_izq if tipo_izq == tipo_der else 'float'
        elif operador in ['<', '>', '!=', '==']:
            result_type = 'bool'
        else:
            result_type = tipo_izq

        resultado = self.nuevo_temp()
        self.operandos.append(resultado)
        self.tipos.append(result_type)
        self.cuadruplos.append((operador, izq, der, resultado))

    def asigna(self):
        valor = self.operandos.pop()
        var = self.operandos.pop()
        self.tipos.pop()
        self.tipos.pop()
        self.cuadruplos.append(('=', valor, None, var))

    def print_quadruples(self):
        print("\nCuádruplos Generados:")
        for i, quad in enumerate(self.cuadruplos):
            print(f"{i}: {quad}")
