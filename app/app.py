from flask import Flask, render_template, request, flash
from markupsafe import Markup
from src.ConversorPDF import ConversorPDF
from src.NER import NER
from spacy import displacy
from src.Anonimizador import Anonimizador
from src.ExportarPDF import ExportarPDF
from datetime import datetime
from Utils import Utils

app = Flask(__name__)
# Definimos una clave privada para la aplicación para poder establecer conexiones HTTPS
with open("keys/secret_key", "r") as file: app.secret_key = file.read()
orden = 0 # Variable para controlar el flujo de la aplicación

@app.route("/", methods=["GET", "POST"])
def main():
    global orden
    utils = Utils()
    configuracion = utils.cargarConfiguracion()
    if request.method == "POST":
        # Se ha pulsado el boton de cargar documento
        if request.form.get("btn-cargar") == "Cargar":
            print("BOTON CARGAR!!")
            visualizacion_prediccion = ""
            # Tomamos el archivo que ha sido seleccionado
            archivo = request.form.get("input-doc")

            fecha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            utils.escribirTiempoEjecucion("a", f"\n\nMétricas de tiempo para el archivo: {archivo} (en segundos) Fecha --> {fecha}\n")
            orden = 1
            try: # Procesamos el PDF para extraer el texto
                conversorPDF = ConversorPDF()
                conversorPDF.extraerTextoPDF(archivoPDF = archivo)
            except Exception as e:
                flash("ERROR!! No se ha seleccionado un archivo para anonimizar.", "error")
                return render_template("index.html")

            try: # Procesamos el texto para extraer las menciones personales
                ner = NER()
                ner.obtenerPrediccionesNER() # Calculamos las predicciones del modelo
                # Generamos la vista HTML de los documentos con sus predicicones
                visualizacion_prediccion = ner.generarVisualizacionDocumentos()
                utils.serializarObjeto(ruta = configuracion["META"]["input_div_path"], objeto = visualizacion_prediccion)
            except Exception as e:
                flash("Ha ocurrido un error durante el proceso de detección de entidades (NER)", "error")
                print(e)

            flash(f"¡El documento: {archivo} se ha cargado con éxito!", "ok")
            
            # Actualizamos la vista con las entidades detectadas
            return render_template("index.html", visualizacion_prediccion = Markup(visualizacion_prediccion) ) 

        elif request.form.get("btn-anonimizar") == "Anonimizar":
            anonimizador, visualizacion_nuevo_doc = None, None
            
            if orden < 1: # Si el doc no esta cargado o anonimizado
                flash("ERROR!! No se ha seleccionado un archivo para anonimizar.", "error")
                return render_template("index.html")
            orden = 2
            try: # Cargamos el modulo de anonimizacion junto con el de los grafos
                anonimizador = Anonimizador()
            except Exception:
                flash("Ha ocurrido un error durante la creación del grafo de reemplazos", "error")
            try: # Anonimizamos el documento
                visualizacion_nuevo_doc = anonimizador.AnonimizarDocumento()
            except Exception as e:
                flash("Ha ocurrido un error durante la anonimización", "error")
                print(f"El Error es: {e}")
            
            # Obtenemos el documento con las etiquetas predichas por el modelo
            visualizacion_prediccion = utils.deserializarObjeto(configuracion["META"]["input_div_path"])

            flash("La anonimización del documento se ha realizado correctamente", "ok")
            
            # Mostramos la vista con ambos documentos (real y anonimizado)
            return render_template("index.html", visualizacion_prediccion = Markup(visualizacion_prediccion), visualizacion_nuevo_doc = Markup(visualizacion_nuevo_doc) ) 
        
        elif request.form.get("btn-exportar") == "Exportar":
            print("BOTON EXPORTAR!!")

            if orden != 2: # Si el doc no está anonimizado
                flash("ERROR!! Hay que anonimizar un documento antes de exportarlo", "error")
                return render_template("index.html")
            try: # Exportamos el documento anonimizado a PDF
                generadorNuevoPDF = ExportarPDF()
                generadorNuevoPDF.exportarPDF()
                flash("El PDF anonimizado se ha exportado correctamente", "ok")

                opciones = { # Fijamos las opciones de la visualizacion
                    "ents": configuracion["ANONIMIZACION"]["ENTIDADES"],
                    "colors": configuracion["HERRAMIENTA"]["COLORES"],
                }
                # Cargamos la vista de la predicciones del doc original
                visualizacion_prediccion = utils.deserializarObjeto(configuracion["META"]["input_div_path"])
                
                # Cargamos el doc anonimizado
                visualizacion_anonimizacion = utils.deserializarObjeto(configuracion["META"]["path_output_doc_bin"])
                # Generamos la vista del doc anonimizado
                visualizacion_anonimizacion = displacy.render(visualizacion_anonimizacion, style="ent", options = opciones)
                
                # Mostramos la pagina con las vistas de ambos documentos
                return render_template("index.html", visualizacion_prediccion = Markup(visualizacion_prediccion), visualizacion_nuevo_doc = Markup(visualizacion_anonimizacion) ) 

            except Exception as e:
                flash("ERROR! No se ha podido exportar el PDF", "error")
                print("ERROR PDF: ", e)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(ssl_context = ("keys/cert.pem", "keys/key.pem"), debug=True)