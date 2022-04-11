import spacy
from spacy.tokens import Doc, Span
from Utils import Utils
from src.RegexNER import REGEXComponent
from spacy import displacy
import glob
import os
import time

LOG_MESSAGE = "NER"

class NER():
    def __init__(self):
        self.utils = Utils()
        self.configuracion = self.utils.cargarConfiguracion()
        self.ruta_tmp = self.configuracion["META"]["tmp"]

        # Obtenemos la lista de los documentos en .txt generados y los ordenamos por fecha de creación (obteniendo así el texto en el mismo orden que las paginas del original)
        self.lista_documentos = glob.glob(f"{self.ruta_tmp}/*.txt")
        self.lista_documentos.sort(key = os.path.getmtime)
        
        self.lista_documentos_NER = [] # Lista para guardar los objetos Doc de cada pagina

        self.opciones = { 
            "ents": self.configuracion["ANONIMIZACION"]["ENTIDADES"],
            "colors": self.configuracion["HERRAMIENTA"]["COLORES"],
        }
        
    def obtenerPrediccionesNER(self):
        # Realiza el computo
        inicio = time.time()
        self.aplicarNER() # Aplicamos el NER a los documentos
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* NER\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")
        self.exportarDocumentoYPredicciones() # Exportamos el Doc a binario

    def aplicarNER(self):
        n_tokens, n_entidades = 0, 0
        # Cargamos el modelo y le añadimos la componente de las expresiones regulares
        nlp = spacy.load(self.configuracion["META"]["path_modelo"])
        nlp.add_pipe("regex", before = 'ner')

        # Por cada una de las paginas del documento original...
        for documento in self.lista_documentos: 
            print(f"{LOG_MESSAGE}-Aplicando NER en el Documento: {documento}")
            texto = self.utils.cargarTexto(documento) # Cargamos el texto del documento de texto
            doc = nlp(texto) # Generamos el objeto Doc con las anotaciones del modelo
            self.lista_documentos_NER.append(doc) # Añadimos el Doc procesado a la lista de los documentos NER
            n_tokens += len(doc)
            n_entidades += len(doc.ents)
        
        self.utils.escribirTiempoEjecucion("a", f"\n* Número de Palabras: \t {n_tokens}")
        self.utils.escribirTiempoEjecucion("a", f"\n* Número de Entidades: \t {n_entidades}")
        print(self.lista_documentos_NER[-1].ents)
        print("Pipeline: ", nlp.pipe_names)

    def generarVisualizacionDocumentos(self): # Generamos el codigo HTML de los documentos con displacy
        html = displacy.render(self.lista_documentos_NER, style="ent", options = self.opciones)
        return html

    def exportarDocumentoYPredicciones(self):
        # Juntamos todos los objetos Doc con las predicciones para cada pagina del PDF en un único Doc y lo serializamos para su posterior uso
        doc = Doc.from_docs(self.lista_documentos_NER)
        self.utils.serializarObjeto(f"{self.ruta_tmp}/doc.bin", doc)

        # Eliminamos los documentos .txt para ahorrar espacio y evitar errores
        lista_archivos = glob.glob(f"{self.configuracion['META']['tmp']}*.txt")
        for archivo in lista_archivos:
            os.remove(archivo)

