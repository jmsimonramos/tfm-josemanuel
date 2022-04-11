from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from Utils import Utils
import os
import time
LOG_MESSAGE = "CONVERSOR_PDF"

class ConversorPDF():
    def __init__(self):
        self.utils = Utils()
        self.configuracion = self.utils.cargarConfiguracion()
        # Cogemos la ruta base donde se encuentran los documentos originales y la ruta de los ficheros temporales
        self.doc_path = self.configuracion["META"]["input_docs"]
        self.tmp_path = self.configuracion["META"]["tmp"]
    
    def extraerTextoPDF(self, archivoPDF):    
        inicio = time.time()
        # Generamos una lista con todas las paginas del PDF
        paginas = convert_from_path(self.doc_path + archivoPDF, 500)
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Leer PDF\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")

        contador_paginas = 1
        
        inicio = time.time()
        # Para cada una de las paginas del PDF...
        for pagina in paginas:   
            print(f"{LOG_MESSAGE}-Procesando Pagina {contador_paginas} de {len(paginas)}")
            # Exportamos la imagen a JPEG
            pagina.save(self.tmp_path + f"doc_{contador_paginas}.jpg", 'JPEG')
            contador_paginas += 1
        
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Convertir PDF a imagen: \t{self.utils.calcularTiempoEjecucion(inicio, fin)}")

        self.utils.escribirTiempoEjecucion("a", f"\n* Páginas PDF: \t{contador_paginas - 1}")

        inicio = time.time()
        for i in range(1, contador_paginas): # Para cada una de las paginas...
            print(f"{LOG_MESSAGE}-Generando Texto {i} de {contador_paginas - 1}") 
            # Abrimos la imagen correspondiente a esa pagina
            archivo_imagen = self.tmp_path + f"doc_{i}.jpg"
            # Creamos un fichero de texto vacio para esa pagina
            fichero = open(self.tmp_path + f"doc_{i}.txt", "w")
            
            # Extraemos el texto utilizando el OCR
            texto = pytesseract.image_to_string( Image.open( archivo_imagen ))
            
            # Eliminamos el archivo de imagen para no acumular espacio innecesario
            os.remove(archivo_imagen)

            # Eliminamos los saltos de línea
            texto = texto.replace('-\n', '')    

            # Escribimos el texto extraido en el documento de texto
            fichero.write(texto)
            fichero.close()
        
        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Convertir imagen a texto\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")