
class analizadorsemantico:
    def __init__(self):
        self.pila_operandos = []
        self.pila_tipos = []
        self.pila_operadores = []
        self.cuadruplos = []
        self.temporal_contador = 1

        self.directorio_Funk = {
            'global': {
                'vars': {},
                'type': 'void',
                'params': []
            }
        }
        self.entorno_actual = 'global'
        self.cubito_semantico = self.build_cubito_semantico()


    def build_cubito_semantico(self):
        return {
            '+':{
                ('int','int'):'int',
                ('int','float'):'float',
                ('float','float'):'float',
                ('float','int'):'float',
            },
            '-':{
                ('int','int'):'int',
                ('int','float'):'float',
                ('float','float'):'float',
                ('float','int'):'float',
            },
            '*':{
                ('int','int'):'int',
                ('int','float'):'float',
                ('float','int'):'float',
                ('float','float'):'float',
            },
            '/':{
                ('int','int'):'int',
                ('int','float'):'float',
                ('float','int'):'float',
                ('float','float'):'float',
            },
            '<':{
                ('int','int'):'bool',
                ('int','float'):'bool',
                ('float','int'):'bool',
                ('float','float'):'bool',
            },
            '>':{
                ('int','int'):'bool',
                ('int','float'):'bool',
                ('float','int'):'bool',
                ('float','float'):'bool',
            },
            '=':{
                ('int','int'):'int',
                ('float','float'):'float',
                ('bool','bool'):'bool',
            },
            '!=':{
                ('int','int'):'bool',
                ('bool','bool'):'bool',
                ('int','float'):'bool',
                ('float','float'):'bool',
                ('float','int'):'bool',
            },
            '==':{
                ('int','int'):'bool',
                ('bool','bool'):'bool',
                ('float','float'):'bool',
                ('int','float'):'bool',
                ('float', 'int'):'bool',
            }
        }
    def enter_scope(self,nombre_func):
        self.entorno_actual = nombre_func
        if nombre_func in self.directorio_Funk:
            self.directorio_Funk[nombre_func] = {
                'vars':{},
                'type':'void',
                'params':[]
            }
    def entorno_salida(self):
        self.entorno_actual = 'global'

    def declarar_variable(self,nombre_var, tipo_var):
        entorno_de_variable = self.directorio_Funk[self.entorno_actual]['vars']
        if nombre_var in entorno_de_variable:
            raise Exception(f"{nombre_var} ya existe")
        entorno_de_variable[nombre_var] = tipo_var

    def obtener_tipo_variable(self,nombre_var):
        if nombre_var in self.directorio_Funk[self.entorno_actual]['vars']:
            return self.directorio_Funk[self.entorno_actual]['vars'][nombre_var]
        elif nombre_var in self.directorio_Funk['global']['vars']:
            return self.directorio_Funk['global']['vars'][nombre_var]
        else:
            return Exception(f"{nombre_var} no esta declarada")

    def checar_operador(self, iz_type, operador, de_type):
        result = self.cubito_semantico.get(operador, {}).get((iz_type, de_type))
        if result is None:
            raise Exception(f"Error semántico: No se puede aplicar '{operador}' entre '{iz_type}' y '{de_type}'")
        return result

    def declarar_fucion(self,func_name,type_return,parametros):
        if func_name in self.directorio_Funk:
            raise Exception(f"{func_name} ya existe")
        self.directorio_Funk[func_name] = {
            'vars':{},
            'type':type_return,
            'params':parametros
        }

    def validar_fun_call(self, nombre_func, argumentos_type):
        if nombre_func not in self.directorio_Funk:
            raise Exception(f"{nombre_func} no existe")

        func_info = self.directorio_Funk[nombre_func]
        parametros_exp = func_info['params']

        if len(argumentos_type) != len(parametros_exp):
            raise Exception(f"Error: Funcion'{nombre_func}' tamaño excedido, esperado: '{len(parametros_exp)}'")

        for i, ((nombre_para, para_type),argument_type) in enumerate(zip(parametros_exp,argumentos_type)):
            if para_type != argument_type:
                raise Exception(f"Error en argumento {i+1} ('{nombre_para}'): se esperaban '{para_type}' recibidos: '{argument_type}')")

    def imprimir_directorio(self):
        print("\n Directorio de Funciones \n")
        for func_name, func_info in self.directorio_Funk.items():
            print(f"Función: {func_name}")
            print(f"  Tipo de retorno: {func_info['type']}")
            print("  Parámetros:")
            for nombre, tipo in func_info['params']:
                print(f"    - {nombre} : {tipo}")
            print("  Variables:")
            for var_name, var_type in func_info['vars'].items():
                print(f"    - {var_name} : {var_type}")
            print("----------------------------------")

    def nuevo_temporal(self):
        temp_name = f"t{self.temporal_contador}"
        self.temporal_contador += 1
        return temp_name

    def generar_cuadruplo(self):
        if len(self.pila_operadores) == 0 or len(self.pila_operandos) < 2 or len(self.pila_tipos) < 2:
            return

        operador = self.pila_operadores.pop()
        derecho = self.pila_operandos.pop()
        tipo_derecho = self.pila_tipos.pop()
        izquierdo = self.pila_operandos.pop()
        tipo_izquierdo = self.pila_tipos.pop()

        try:
            tipo_resultado = self.checar_operador(tipo_izquierdo, operador, tipo_derecho)
        except Exception as e:
            raise Exception(f"Error de tipos en operación: {e}")

        temporal = self.nuevo_temporal()
        self.cuadruplos.append((operador, izquierdo, derecho, temporal))

        # Guardar el resultado temporal para usar en operaciones posteriores
        self.pila_operandos.append(temporal)
        self.pila_tipos.append(tipo_resultado)

    def generar_cuadruplo_asignacion(self, destino):
        if len(self.pila_operandos) < 1 or len(self.pila_tipos) < 1:
            raise Exception("Error: No hay valor para asignar")

        valor = self.pila_operandos.pop()
        tipo_valor = self.pila_tipos.pop()
        tipo_destino = self.obtener_tipo_variable(destino)

        if tipo_destino != tipo_valor:
            raise Exception(f"Error de tipos en asignación: {tipo_destino} != {tipo_valor}")

        self.cuadruplos.append(('=', valor, None, destino))

    def generar_cuadruplo_condicion(self, operador):
        if len(self.pila_operandos) < 2 or len(self.pila_tipos) < 2:
            raise Exception("Error: Condición incompleta")

        derecho = self.pila_operandos.pop()
        tipo_derecho = self.pila_tipos.pop()
        izquierdo = self.pila_operandos.pop()
        tipo_izquierdo = self.pila_tipos.pop()

        try:
            tipo_resultado = self.checar_operador(tipo_izquierdo, operador, tipo_derecho)
        except Exception as e:
            raise Exception(f"Error de tipos en condición: {e}")

        # Para condiciones, el resultado es un salto condicional
        temporal = self.nuevo_temporal()
        self.cuadruplos.append((operador, izquierdo, derecho, temporal))

        return temporal  # Devuelve el temporal que puede usarse para el salto



# -----------------------------------------------------------------------------------/
#
#     def exportar_directorio_json(self, archivo='directorio_funciones.json'):
#         with open(archivo, 'w') as f:
#             json.dump(self.directorio_Funk, f, indent=4)
        