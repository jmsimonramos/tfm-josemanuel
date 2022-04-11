import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import connected_components
import itertools
import Levenshtein as lev
from networkx.algorithms.isomorphism import GraphMatcher
import matplotlib.pyplot as plt
from Utils import Utils
import random

class UtilsGrafos():
    def __init__(self):
        self.utils = Utils()
        self.configuracion = self.utils.cargarConfiguracion()

        self.ruta_csv = self.configuracion["META"]["path_data_csv"]
        self.ruta_bin = self.configuracion["META"]["path_data_bin"]
        
        self.JERARQUIA = self.configuracion["ANONIMIZACION"]["JERARQUIA"]
        self.PROVINCIAS = self.utils.cargarFicheroDatos(self.configuracion["META"]["path_provincias"])
            
    def cargarGrafo(self):
        try:
            return self.utils.deserializarObjeto(self.ruta_bin)
        except FileNotFoundError: # No tengo el grafo serializado (cargo txt)
            grafo = nx.Graph()
            lineas_fichero = self.utils.cargarFicheroDatos(self.ruta_csv)

            for registro in lineas_fichero[1:]: # Omitimos la primera linea al ser la cabecera
                datos = [ x for x in registro.split(";") ] # Eliminamos los registros vacios
                if datos[1] in self.PROVINCIAS: # Provincia = Ciudad (se añade sufijo a ciudad)
                    datos[1] += "_CIUDAD"
                
                # Añadimos los nodos y sus propiedades
                grafo.add_nodes_from([ (entidad, {"tipo": self.JERARQUIA[indice], "n_tokens": len(entidad.split(" ")), "profundidad": self.JERARQUIA.index(self.JERARQUIA[indice])} ) for indice, entidad in enumerate(datos)] ) 
                
                for i in range(len(datos)):
                    try:
                        grafo.add_edge( datos[i], datos[i + 1])
                    except IndexError:
                        continue
            self.utils.serializarObjeto(self.ruta_bin, objeto = grafo)
            return grafo
    
    def estaConectada(self, grafo, entidad1, entidad2):
        return entidad1 in grafo.neighbors( entidad2 )
    
    def ordenarGrafo(self, grafo):
        # Ordenamos los nodos de los grafos de mayor profundidad a menor profundidad
        grafo_ordenado = nx.Graph()
        grafo_ordenado.add_nodes_from( sorted( grafo.nodes( data = True ), key = lambda x: x[1]["profundidad"], reverse = True) )
        grafo_ordenado.add_edges_from(grafo.edges)

        return grafo_ordenado
    
class Grafos():
    def __init__(self, doc):
        self.GRAFO_UTILS = UtilsGrafos()
        self.doc = doc
        self.utils = Utils()
        self.configuracion = self.utils.cargarConfiguracion()

        self.ruta_csv = self.configuracion["META"]["path_data_csv"]
        self.ruta_bin = self.configuracion["META"]["path_data_bin"]
        self.JERARQUIA = self.configuracion["ANONIMIZACION"]["JERARQUIA"]
        self.PROVINCIAS = self.utils.cargarFicheroDatos(self.configuracion["META"]["path_provincias"])
        
        self.umbral = self.configuracion["ANONIMIZACION"]["umbral_coincidencia"]
        self.max_intentos_antes_dividir = self.configuracion["ANONIMIZACION"]["intentos_antes_dividir"]
        self.max_intentos_despues_dividir = self.configuracion["ANONIMIZACION"]["intentos_despues_dividir"]
        
        self.diccionario_normalizacion = {}

        self.GRAFO = self.GRAFO_UTILS.cargarGrafo()
        self.G_AUX = nx.Graph()
        self.reemplazos_entidades = {}

    def GenerarReemplazos(self):
        self.obtenerGrafoDocumento(self.doc) # Genera el grafo del documento
        self.encontrarReemplazosEntidades() # Calcula los reemplazos para el grafo del documento

    def _normalizarGrafo(self):
        # Me creo un grafo vacio con los nodos normalizados
        grafo_normalizado = nx.Graph()
        
        for nodo in self.G_AUX.nodes():
            # Para cada uno de los nodos busco cual es el mas similar a el dentro del grafo general utilizando ratios de similitud
            nodo_similar = self.encontrarSimilar(nodo)
                
            if nodo_similar: # Si hay un nodo similar lo añado normalizado
                grafo_normalizado.add_nodes_from([(nodo_similar[0], self.GRAFO.nodes[nodo_similar[0]])])
                self.diccionario_normalizacion[nodo] = nodo_similar[0]
            else: # Si no encuentro ninguna coincidencia lo dejo como esta
                grafo_normalizado.add_nodes_from([(nodo, self.G_AUX.nodes[nodo])])
        
        return grafo_normalizado
    
    def obtenerGrafoDocumento(self, docSpacy):
        self.G_AUX = nx.Graph()

        # Añado al grafo del documento aquellas entidades que se encuentren dentro de la jerarquia que se procesa en este modulo
        for entidad in docSpacy.ents:
            if entidad.label_ in self.GRAFO_UTILS.JERARQUIA:
                texto = entidad.text.title()
                self.G_AUX.add_node(texto, tipo = entidad.label_, n_tokens = len(entidad.text.split(" ")), profundidad = self.GRAFO_UTILS.JERARQUIA.index(entidad.label_))
        
        self.G_AUX = self._normalizarGrafo() # Normalizamos los nodos del grafo
        self._conectarNodosGrafoSpacy() # Establecemos las conexiones entre los nodos

    def _conectarNodosGrafoSpacy(self):
        # Generamos todos los pares de combinaciones de las entidades
        for entidad1, entidad2 in itertools.combinations(self.G_AUX.nodes(), 2):
            try: # Comprobamos si existe conexion entre ellas en el grafo general
                if self.GRAFO_UTILS.estaConectada(self.GRAFO, entidad1, entidad2):
                    self.G_AUX.add_edge(entidad2, entidad1)
            except Exception:
                pass

    def _calcularPosiblesSubgrafosValidos(self, grafoComprobar, flagDividir = False):
        # Inicializo el matcher encargado de encontrar coincidencias entre el grafo general y el grafo del documento
        Matcher = GraphMatcher( self.GRAFO, grafoComprobar )
        intentos = 0 # Numero de intentos fallidos
        # Itero sobre todos los subgrafos isomorfos que calcula el matcher
        for subgrafo in Matcher.subgraph_isomorphisms_iter():
            valido, dividir = True, False
            # Itero sobre los valores originales y las propuestas de reemplazo que me calcula el matcher y compruebo si son validos
            for reemplazo, original in subgrafo.items():
                if self.reemplazoValido(reemplazo, original): # Tienen la misma estructura
                    # No han sido utilizado antes
                    if reemplazo not in self.reemplazos_entidades.keys():
                        continue
                    else: # Si no es valido dejo de comprobar y proceso el siguiente grafo candidato
                        valido = False
                        break
                else: # Si no es valido dejo de comprobar y proceso el siguiente grafo candidato
                    valido = False
                    break
            if valido: # Si es valido paro de buscar y lo devuelvo como resultado
                return subgrafo
            
            if intentos % 5000 == 0:
                print(f"** Intentos: {intentos}")
            
            # Si llevo X intentos y no he dividido el grafo, activo el flag para eliminar conexiones
            if intentos == self.max_intentos_antes_dividir and not flagDividir:
                dividir = True
                break
            
            # Si llevo X intentos y ya he dividido el grafo, activo el flag para volver a eliminar conexiones
            if intentos == self.max_intentos_despues_dividir and flagDividir:
                dividir = True
                break
            
            intentos += 1
        
        if dividir: # En el caso de dividir el grafo
            print("DIVIDIR!!!")
            # Obtengo el nodo con mayor peso
            mayor_nodo = list( grafoComprobar.nodes() ) [-1]
            try: # Obtengo un nodo que este conectado al nodo con mayor peso
                nodo_eliminar = random.choice( list( grafoComprobar.neighbors(mayor_nodo) ) )
                # Elimino la conexion entre ambos nodos
                grafoComprobar.remove_edge(mayor_nodo, nodo_eliminar)
            except Exception:
                pass
            
            # Proceso las nuevas componentes que se han generado al realizar esta division
            for componente in list(sorted( connected_components(grafoComprobar), key = len , reverse = False)):
                
                grafo_dividido = grafoComprobar.subgraph( componente )
                grafo_dividido = self.GRAFO_UTILS.ordenarGrafo( grafo_dividido )
                
                print("COMPONENTE DIVIDIDA: ", grafo_dividido.nodes()) 
                
                subgrafo_valido = self._calcularPosiblesSubgrafosValidos(grafo_dividido, flagDividir = True)
                self.reemplazos_entidades.update(subgrafo_valido)
            
            return self.reemplazos_entidades
    
    def encontrarReemplazosEntidades(self):
        # Obtenemos la lista de componentes que conforman el grafo y las ordenamos de mas a menos largas
        lista_componentes = list(sorted( connected_components(self.G_AUX), key = len , reverse = True)) # Ordena las componentes de mayor a menor número de nodos
        
        for idx, componente in enumerate(lista_componentes):
            print(f"Procesando Componente {idx + 1} de {len(lista_componentes)}")
            print("COMPONENTE: ", componente)
            # Genero un subgrafo con los nodos y atributos del original
            grafoOrdenado = self.G_AUX.subgraph( componente )
            # Ordeno los nodos por profundidad
            grafoOrdenado = self.GRAFO_UTILS.ordenarGrafo( grafoOrdenado )
            print("ORDENADO: ", grafoOrdenado.nodes())
            
            # Obtengo un subgrafo del grafo general valido para esa componente
            subgrafo_valido = self._calcularPosiblesSubgrafosValidos(grafoOrdenado)
            # Actualizo el diccionario de reemplazos con los nuevos valores para esa componente
            self.reemplazos_entidades.update(subgrafo_valido)

        # Invierto el diccionario de reemplazos para dejarlo de la forma {mencion original: reemplazo asociado}
        self.reemplazos_entidades = {valor: clave for clave, valor in self.reemplazos_entidades.items()}
        
    # Calculo si un reemplazo es valido o nno        
    def reemplazoValido(self, entidad1, entidad2):
        if entidad1 != entidad2: # La nueva mencion ha de ser distinta a la original
            if self.GRAFO.nodes[entidad1]["profundidad"] == self.G_AUX.nodes[entidad2]["profundidad"]: # Han de ser de la misma categoria
                if self.GRAFO.nodes[entidad1]["n_tokens"] == self.G_AUX.nodes[entidad2]["n_tokens"]: # Han de tener el mismo numero de palabras
                    return True
        return False
    
    def encontrarSimilar(self, entidad):
        similitud_dict = {}

        for nodo_grafo in self.GRAFO.nodes():
            # Iteramos sobre todos los nodos del grafo general y calculamos su ratio de similiutd respecto al nodo que estamos comprobando
            score = round( lev.ratio(nodo_grafo.lower(), entidad.lower()), 3)
            similitud_dict[nodo_grafo] = score
            if score == 1: # Si hay coincidencia del 100% se para
                break
        # Obtenemos el nodo con la mayor coincidencia de todos
        mejor_coincidencia = self.utils.ordenarDiccionario(similitud_dict).popitem()
        # Devuelvo el valor como resultado en el caso de que supere el umbral de coincidencia establecido
        if mejor_coincidencia[1] < self.umbral:
            return None
        else:
            return mejor_coincidencia