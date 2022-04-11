import spacy
from spacy.tokens import Doc, Span
from Utils import Utils
from spacy import displacy
from src.Grafos import Grafos
import random
import re
import string
import time

LOG_MESSAGE = "ANONIMIZADOR"

class Anonimizador():

    def __init__(self):
        self.utils = Utils()
        self.configuracion = self.utils.cargarConfiguracion()
        self.doc = self.utils.deserializarObjeto(f"{self.configuracion['META']['tmp']}/doc.bin")
        self.doc_nuevo = None
        
        inicio = time.time()
        # Cargamos el modulo de los grafos con el documento a anonimizar
        self.MODULO_GRAFOS = Grafos( self.doc ) 
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Cargar Módulo Grafos\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")
        
        # Cargamos el diccionario global de reemplazos
        self.diccionario_global = self.utils.cargarDiccionarioReemplazos()
        
        print("DOCS: " , self.doc.ents)

        self.reemplazos_grafo = {} # Reemplazos obtenidos por el modulo de grafos
        self.intentos_reemplazo = self.configuracion["ANONIMIZACION"]["intentos"]
        self.lista_reemplazos = []

        self.opciones = { 
            "ents": self.configuracion["ANONIMIZACION"]["ENTIDADES"],
            "colors": self.configuracion["HERRAMIENTA"]["COLORES"],
        }

    def AnonimizarDocumento (self):
        inicio = time.time()
        # Generamos los reemplazos para las entidades relacionadas con los grafos
        self.MODULO_GRAFOS.GenerarReemplazos() 
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Obtención de Reemplazos (Grafos)\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")
        # Obtenemos los reemplazos generados por el modulo de grafos
        self.reemplazos_grafo = self.MODULO_GRAFOS.reemplazos_entidades
        
        inicio = time.time()
        # Calculamos los reemplazos para el resto de entidades
        self.obtenerReemplazos()
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Obtención de Reemplazos (Otras entidades)\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")
        print("======================================")
        
        print( len(self.lista_reemplazos) == len(self.doc.ents) )
        # Validamos que los reemplazos sean correctos
        self.validarReemplazos(self.lista_reemplazos)
        
        inicio = time.time()
        # Generamos el nuevo documento con los reemplazos generados
        self.generarNuevoDoc()
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Generar Nuevo Documento\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")
        
        self.utils.serializarObjeto(ruta = self.configuracion["META"]["path_output_doc_bin"], objeto = self.doc_nuevo)
        return self.generarVisualizacionDocumentos()

    def generarNuevoDoc(self):
        # Cogemos el texto del documento original
        nuevo_texto = [x.text for x in self.doc]
        for reemplazo in self.lista_reemplazos:
            # Calculo el numero de palabras que tienen el reemplazo
            # reemplazo = (inicio, fin, tipo_mencion, nueva_mencion)
            longitud = reemplazo[1] - reemplazo[0]
            # Obtengo la mencion original y pongo la nueva mencion en el mismo formato que esta (mayusculas, minusculas, etc)
            mencion_original = nuevo_texto[reemplazo[0] : (reemplazo[0] + longitud)]
            nueva_mencion = self.utils.normalizarEntidad( " ".join(mencion_original), reemplazo[3])
            # Sustituyo en el nuevo texto las palabras de la mencion antigua por la nueva
            nuevo_texto[reemplazo[0]: (reemplazo[0] + longitud)] = nueva_mencion.split(" ")
        
        nlp_vacio = spacy.blank("es")
        # Creamos el objeto Doc vacio con el texto de reemplazo
        self.doc_nuevo = Doc(nlp_vacio.vocab, words = nuevo_texto)
        nuevas_entidades = []
        
        # Añadimos las nuevas entidades al Doc final
        for reemplazo in self.lista_reemplazos:
            nuevas_entidades.append( Span(self.doc_nuevo, reemplazo[0], reemplazo[1], reemplazo[2]) )

        self.doc_nuevo.set_ents(nuevas_entidades)

    def generarVisualizacionDocumentos(self):
        html = displacy.render(self.doc_nuevo, style="ent", options = self.opciones)
        return html

    def obtenerReemplazos(self):
        for entidad in self.doc.ents: # Iteramos sobre las entidades detectadas
            # Transformamos las entidades a la primera letra mayuscula para poder buscarlas mas facilmente y tenerlas en un formato comun
            entidad_normalizada = entidad.text.title()
            try: # Se busca si la entidad ya ha sido anonimizada
                nueva_entidad = self.reemplazos_grafo[entidad_normalizada]
                self.lista_reemplazos.append( (entidad.start, entidad.end, entidad.label_, nueva_entidad) )
            
            except KeyError: # La entidad no tiene reemplazo --> se busca en el otro diccionario a ver si esta ha sido transformada en el modulo de diccionarios
                try:
                    nueva_entidad = self.reemplazos_grafo[self.MODULO_GRAFOS.diccionario_normalizacion[entidad_normalizada]]
                    self.lista_reemplazos.append( (entidad.start, entidad.end, entidad.label_, nueva_entidad) )
                except KeyError: # No tengo info de esa entidad   
                    fallos = 0
                    while fallos < self.intentos_reemplazo:
                        try:
                            nueva_entidad = self.generarNuevaEntidad(entidad)
                            if nueva_entidad == entidad_normalizada:
                                raise ValueError
                            break
                        except Exception:
                            fallos += 1
                    if fallos == self.intentos_reemplazo: # Si tengo reemplazo lo añado a la lista y si no no lo anonimizo
                        self.reemplazos_grafo[entidad_normalizada] = entidad_normalizada
                        self.lista_reemplazos.append( (entidad.start, entidad.end, entidad.label_, entidad_normalizada) )
                    else:
                        self.reemplazos_grafo[entidad_normalizada] = nueva_entidad
                        self.lista_reemplazos.append( (entidad.start, entidad.end, entidad.label_, nueva_entidad) )

    def generarNuevaEntidad(self, entidad):
        if entidad.label_ == "DNI":
            lista_letras = list("TRWAGMYFPDXBNJZSQVHLCKE")

            def calcular_nif(numero, letra_inicial):
                letra_control = 'jabcdefghi'

                evens = sum([int(k) for i, k in enumerate(numero) if i % 2])
                odds = [2 * int(k) for i, k in enumerate(numero) if not i % 2]
                odds = sum([int(d) for i in odds for d in str(i)])
                c = (10 - int(str(evens + odds)[-1])) % 10

                if letra_inicial.lower() in 'abcdefghijuv':
                    return text[0].upper() + numero + str(c)
                elif letra_inicial.lower() in 'npqrsw':
                    return text[0].upper() + numero + letra_control[c]
                return numero

            id_number = str(random.randint(10000000, 99999999))

            text = re.sub(r'[^\w]', '', entidad.text.strip())
            numero = len([k for k in text if k.isdigit()])

            nuevo_dni = text

            if numero == 8:  # DNI, CIF or old NIE
                if text[0].isalpha() and text[-1].isalpha():  # NIE
                    nuevo_dni = text[0].upper() + id_number + lista_letras[int(id_number) % 23]
                elif text[0].isalpha():  # NIF/CIF with control digit
                    nuevo_dni = calcular_nif(id_number[:-1], text[0])
                elif text[-1].isalpha():  # DNI
                    nuevo_dni = id_number + lista_letras[int(id_number) % 23]
            elif numero == 7:  # NIF or new NIE
                if text[0].lower() in 'xyz' and text[-1].isalpha():  # NIE
                    aux_number = int(str('xyz'.find(text[0].lower())) + id_number[:numero])
                    nuevo_dni = text[0].lower().upper() + id_number[:numero] + lista_letras[aux_number % 23]
                elif text[0].isalpha():  # NIF/CIF with control letter
                    nuevo_dni = calcular_nif(id_number[:numero], text[0])
                elif text[-1].isalpha():  # Old DNI? 9,999,999A
                    nuevo_dni = id_number + lista_letras[int(id_number) % 23]
            else:  # Defaults to DNI
                nuevo_dni = id_number + lista_letras[int(id_number) % 23]

            nuevo_dni = list(nuevo_dni)
            for idx, c in enumerate(entidad.text):
                if c in ' -.':
                    nuevo_dni.insert(idx, c)
            return ''.join(nuevo_dni).strip()
        
        elif entidad.label_ == "TELEFONO":
            
            def calcularPrefijo(telefono):
                prefijo = "".join( telefono[:3] )
                try:
                    provincia_prefijo = self.diccionario_global["PREFIJO"][prefijo]
                except KeyError:
                    prefijo = "".join( telefono[:2] )
                    try:
                        provincia_prefijo = self.diccionario_global["PREFIJO"][prefijo]
                    except KeyError:
                        return None
                
                return prefijo, provincia_prefijo
            
            telefono_antiguo = list(entidad.text)
            
            if telefono_antiguo[0] == 6:
                nuevo_prefijo = "6"
            else:
                prefijo_antiguo, provincia_prefijo = calcularPrefijo(telefono_antiguo)
                try:
                    nueva_provincia = self.reemplazos_grafo[provincia_prefijo]
                    nuevo_prefijo = self.diccionario_global["PREFIJO_PROV"][nueva_provincia]
                except KeyError:
                    nuevo_prefijo = random.choice( list( self.diccionario_global["PREFIJO"].keys() ) )
                    
            telefono = [x for x in telefono_antiguo if x.isdigit()]

            numero_base = nuevo_prefijo + ''.join(['0' for k in range(9 - len(nuevo_prefijo))])
            numero_maximo = nuevo_prefijo + ''.join(['9' for k in range(9 - len(nuevo_prefijo))])

            nuevo_telefono = list(str(random.randint(int(numero_base), int(numero_maximo))))

            for index, value in enumerate(telefono_antiguo):
                if value.isdigit() == False:
                    nuevo_telefono.insert(index, value)
            
            return ("".join(nuevo_telefono)).strip()

        elif entidad.label_ in ["NOMBRE", "APELLIDO"]:
            n_tokens = len(entidad.text.split(' '))
            return random.choice( self.diccionario_global[str(entidad.label_)][n_tokens] ).strip()
        
        elif entidad.label_ in ["EMAIL", "URL"]:
            n_tokens = len(entidad.text.split(' '))
            
            nueva_entidad = list(random.choice(self.diccionario_global[entidad.label_]))
            intervalo = int(len(nueva_entidad) / n_tokens)

            for i in range(1, n_tokens): 
                nueva_entidad.insert((intervalo * i), " ")

            return "".join(nueva_entidad).strip()

        elif entidad.label_ in ["CSV", "MATRICULA", "REF_CATASTRAL", "SEGURIDAD_SOCIAL"]:
            nueva_entidad = []
            for caracter in entidad.text:
                if caracter.isalnum():
                    if caracter.isdigit():
                        nueva_entidad.append( str( random.randint(0,9) ) )
                    else:
                        nueva_entidad.append( random.choice(string.ascii_uppercase) )
                else:
                    nueva_entidad.append(caracter)
            
            return ("".join(nueva_entidad)).strip()
        
        elif entidad.label_ == "CUENTA_BANCARIA":
            
            separadores = [(i,x) for i, x in enumerate(entidad.text) if x.isalnum() == False]

            lista_iban_antiguo = [x for x in entidad.text if x.isalnum()]
            nuevo_numero = list(str(random.randint(1000000000, 9999999999)))
            nuevo_iban = lista_iban_antiguo[:-10] + nuevo_numero

            # Insert in the new mention the separators of the original
            for index, sep in separadores:
                nuevo_iban.insert(index, sep)

            return "".join(nuevo_iban).strip()
        elif entidad.label_ == "DIRECCION":
            n_tokens = len(entidad.text.split(' '))
            try:  
                provincia = random.choice( list( self.diccionario_global["DIRECCION"][n_tokens] ) )
                
                if provincia in self.reemplazos_grafo.keys():
                    return random.choice(self.diccionario_global["DIRECCION"][n_tokens][self.reemplazos_grafo[provincia]])
                else:
                    return random.choice(self.diccionario_global["DIRECCION"][n_tokens][provincia])
            except KeyError:
                return entidad.text

    def validarReemplazos(self, lista):
        errores = 0
        for reemplazo in lista:
            n_tokens = reemplazo[1] - reemplazo[0]
            n_tokens_real = len(reemplazo[3].split(" "))
            if n_tokens != n_tokens_real:
                print(reemplazo)
                errores +=1
        if errores == 0:
            print("DOC PERFECTO!!")
