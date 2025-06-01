from memoria import Mmemoria

class analizadorsemantico:
    def __init__(self):


        self.directorio_Funk = {
            'global': {
                'vars': {},
                'type': 'void',
                'params': []
            }
        }
        self.entorno_actual = 'global'
        self.cubito_semantico = self.build_cubito_semantico()
        self.memoria = Mmemoria()

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

    def enter_scope(self, nombre_func):
        self.entorno_actual = nombre_func
        if nombre_func not in self.directorio_Funk:
            self.directorio_Funk[nombre_func] = {
                'vars': {},
                'type': 'void',
                'params': []
            }


    def entorno_salida(self):
        self.entorno_actual = 'global'

    def declarar_variable(self,nombre_var, tipo_var):
        entorno_de_variable = self.directorio_Funk[self.entorno_actual]['vars']

        if nombre_var in entorno_de_variable:
            raise Exception(f"{nombre_var} ya existe")

        addr = self.memoria.get_address(
            'global' if self.entorno_actual == 'global' else 'local',
            nombre_var,
            tipo_var
        )

        entorno_de_variable[nombre_var] = {'type': tipo_var, 'addr': addr}

    def obtener_tipo_variable(self, nombre_var):
        for scope in [self.entorno_actual, 'global']:
            if nombre_var in self.directorio_Funk[scope]['vars']:
                var_info = self.directorio_Funk[scope]['vars'][nombre_var]
                return var_info['type'], var_info['addr']
        raise Exception(f"{nombre_var} no está declarada")

    def checar_operador(self, iz_type, operador, de_type):
        result = self.cubito_semantico.get(operador, {}).get((iz_type, de_type))
        if result is None:
            raise Exception(f"Error semántico: No se puede aplicar '{operador}' entre '{iz_type}' y '{de_type}'")
        return result

    def declarar_fucion(self,func_name,type_return,parametros):
        if func_name in self.directorio_Funk:
            raise Exception(f"{func_name} ya existe")
        self.directorio_Funk[func_name] = {
            'vars': {},
            'type': type_return,
            'params': parametros
        }

        for param_name, param_type in parametros:
            addr = self.memoria.get_address('local', param_name, param_type)
            self.directorio_Funk[func_name]['vars'][param_name] = {
                'type': param_type,
                'addr': addr
            }
        print(f"Registrado param: {param_name} tipo {param_type} addr {addr}")

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




# -----------------------------------------------------------------------------------/
#
#     def exportar_directorio_json(self, archivo='directorio_funciones.json'):
#         with open(archivo, 'w') as f:
#             json.dump(self.directorio_Funk, f, indent=4)
        