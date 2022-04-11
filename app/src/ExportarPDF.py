from Utils import Utils
from fpdf import FPDF
from datetime import datetime
import time

class PDF(FPDF):
    
    def header(self):
        # Select Arial bold 15
        self.ln(5)
        self.set_font('Arial', 'B', 15)
        self.cell(10)
        # Framed title
        self.cell(0, 12, txt = "TFM José Manuel Simón Ramos", align = 'J')
        self.image("./static/logo.png", x = 135, y = 10, w = 60, h = 20)
        # Line break
        self.ln(20)


class ExportarPDF():
    def __init__(self):
        self.utils = Utils()
        self.configuracion = self.utils.cargarConfiguracion()
        self.margen = self.configuracion["PDF"]["margen"]
        self.doc = self.utils.deserializarObjeto(self.configuracion["META"]["path_output_doc_bin"])
        self.fuente = self.configuracion["PDF"]["fuente"]
    
    def exportarPDF(self):
        inicio = time.time()
        pdf = PDF() # Creamos el PDF
        pdf.add_page()

        # Fijamos la fuente y los margenes
        pdf.add_font("Fira", "", self.fuente, uni = True)
        pdf.set_font("Fira", "", 12)

        pdf.set_left_margin(self.margen)
        pdf.set_right_margin(self.margen)

        # Introducimos un bloque de texto
        pdf.cell(0, 25, txt = "Documento Generado:", ln = 5, align = "C")

        pdf.set_font("Fira", "", 10)
        # Introducimos tantos bloques de texto como sean necesarios con el texto anonimizado
        pdf.multi_cell(0, 6, self.doc.text, align = "J")

        sufijo = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        # Exportamos el PDF
        pdf.output(f"{self.configuracion['PDF']['output_path']}/Documento {sufijo}.pdf")

        fin = time.time()
        self.utils.escribirTiempoEjecucion("a", f"\n* Exportar Documento Anonimizado a PDF\t{self.utils.calcularTiempoEjecucion(inicio, fin)}")