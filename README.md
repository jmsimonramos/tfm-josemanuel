
## 脥ndice

1. [馃摑 Introducci贸n](#Introducci贸n)
2. [馃挭 Motivaci贸n del Proyecto](#Motivaci贸n_El_Proyecto)
3. [馃摎 Conjunto de Datos](#Conjunto_De_Datos)
4. [馃洜 Implementaci贸n](#Implementaci贸n)
5. [馃挰 Extracci贸n del texto de los documentos](#Extracci贸n_Del_Texto_De_Los_Documentos)
6. [馃暤锔忊?嶁檧锔? Detecci贸n de las menciones personales](#Detecci贸n_De_Las_Menciones_Personales)
7. [馃樁鈥嶐煂笍 Anonimizaci贸n de las menciones](#Anonimizaci贸n_De_Las_Menciones)
8. [馃敆 Generaci贸n de reemplazos mediante Grafos](#Generaci贸n_De_Reemplazos_Mediante_Grafos)
9. [馃摃 Generaci贸n de reemplazos mediante Diccionarios](#Generaci贸n_De_Reemplazos_Mediante_Diccionarios)
10. [馃煱 Normalizaci贸n de las menciones](#Normalizaci贸n_De_Las_Menciones)
11. [馃搫 Generaci贸n del nuevo documento PDF](#Generaci贸n_Del_Nuevo_Documento_Pdf)
12. [馃О Rendimiento de la Herramienta](#Rendimiento_De_La_Herramienta)
13. [鈿栵笍 Evaluaci贸n del Rendimiento](#Evaluaci贸n_Del_Rendimiento)
14. [鈿欙笍 Estructura del Repositorio](#Estructura_Del_Repositorio)
15. [馃摲 Capturas de Pantalla](#Capturas)
16. [馃敋 Conclusiones y Trabajo Futuro](#Conclusiones_Y_Trabajo_Futuro)
17. [馃敋 Conclusiones](#Conclusiones)
18. [馃敭 Trabajo Futuro](#Trabajo_Futuro)


Repositorio del proyecto fin de m谩ster: **Implementaci贸n de una herramienta basada en PLN para la detecci贸n y anonimizaci贸n de datos personales en documentos**. Link a la web con la memoria oficial: [UVaDoc](https://uvadoc.uva.es/handle/10324/49995)

# 馃摑 Introducci贸n <a name="Introducci贸n"></a>

En los 煤ltimos a帽os, el avance en el campo del Aprendizaje Autom谩tico, unido a las mejoras hardware, y al aumento de datos, ha motivado la utilizaci贸n de t茅cnicas de aprendizaje para automatizar procesos o extraer conocimiento a partir de los datos (Ver Figura 1).

![Evoluci贸n revisiones AI](assets/totalPublicaciones.png)
**Figura 1: Evoluci贸n de las revisiones de art铆culos de Inteligencia Artificial. Fuente: [AI Index Report](https://aiindex.stanford.edu/wp-content/uploads/2021/03/2021-AI-Index-Report\_Master.pdf)**

Desde el punto de vista del Procesamiento del Lenguaje Natural (PLN), la utilizaci贸n de estos datos se encuentra m谩s limitada debido a la informaci贸n de car谩cter personal en los datos.

Esta caracter铆stica, unida a la fuerte legislaci贸n que existe actualmente sobre la Protecci贸n de Datos (RGPD), hace que las administraciones hayan de tener un mayor control y cuidado a la hora de utilizar y/o compartir documentos con informaci贸n personal.

Sin embargo, existen t茅cnicas para evitar estos problemas:
* Eliminar las apariciones de las menciones personales.
* **Anonimizaci贸n de las menciones.**

## 馃挭 Motivaci贸n del proyecto <a name="Motivaci贸n_El_Proyecto"></a>

Debido a ese control y privacidad sobre los datos, una p茅rdida en los mismos podr铆a suponer grandes sanciones, adem谩s del problema que supone el filtrado de datos personales.

En este proyecto se va a presentar una propuesta **gen茅rica**, que permita tanto detectar distintos tipos de menciones personales en los datos, as铆 como anonimizarlas.

Adem谩s, la propuesta presentada abordar谩 todas las etapas a la hora de anonimizar un documento:

* Obtenci贸n del texto del documento origen --> Aplicando t茅cnicas de OCR.
* Detecci贸n de las menciones personales --> Utilizando modelos de Deep Learning para PLN.
* Anonimizaci贸n de las menciones --> Implementando mecanismos de reemplazos eficientes.
* Generaci贸n del nuevo documento anonimizado --> Creando y modificando archivos PDF.

# 馃摎 Conjunto de Datos <a name="Conjunto_De_Datos"></a>

El conjunto de datos se encuentra formado por 309 documentos administrativos de distintas clases: multas, permisos, pagos, etc (Ver Figuras 2 y 3).

![Datos](assets/datos.png)
**Figura 2: Distribuci贸n de las entidades en los documentos.**
![Estructura de los documentos](assets/estructurasPDF.png)
**Figura 3: Estructura de los documentos.**

# 馃洜 Implementaci贸n <a name="Implementaci贸n"></a>

El *pipeline* desarrollado se encuentra formado por los siguientes componentes (Ver Figura 4):
* Extracci贸n de Texto.
* Detecci贸n de menciones personales.
* Anonimizaci贸n.
* Normalizaci贸n de las menciones.
* Generador de PDF.

![Pipeline Desarrollado](assets/pipelineDesarrollada.png)
**Figura 4: Estructura del pipeline desarrollado.**

## 馃挰 Extracci贸n del texto de los documentos <a name="Extracci贸n_Del_Texto_De_Los_Documentos"></a>

Este componente se encarga de obtener el texto del documento PDF de entrada (Ver Figura 5).

![Extracci贸n del texto](assets/componenteOCR.png)
**Figura 5: Flujo de ejecuci贸n del componente de extracci贸n de texto.**

## 馃暤锔忊?嶁檧锔? Detecci贸n de las menciones personales <a name="Detecci贸n_De_Las_Menciones_Personales"></a>
Componente encargado de extraer las menciones personales del texto. Las menciones son detectadas utilizando modelos de Deep Learning generados utilizando la librer铆a de PLN [Spacy](https://spacy.io/).

Adem谩s, se ha implementado un componente de soporte basado en expresiones regulares para detectar menciones con una estructura predecible (Ver Figuras 6 y 7).

![Regex General](assets/metricasRegex.png)
**Figura 6: M茅tricas generales de la herramienta con y sin la aplicaci贸n expresiones regulares.**

![Regex Desglosada](assets/metricasRegexDesglosadas.png)
**Figura 6: M茅tricas de la herramienta desglosadas por entidad con y sin la aplicaci贸n expresiones regulares.**

## 馃樁鈥嶐煂笍 Anonimizaci贸n de las menciones <a name="Anonimizaci贸n_De_Las_Menciones"></a>

El componente de anonimizaci贸n se ha desarrollado siguiendo un enfoque h铆brido basado en grafos y diccionarios:
* **Enfoque Basado en Grafos:** Permite generar reemplazos para los tipos de menciones que guardan relaci贸n entre s铆 (provincia, ciudad y c贸digo postal).
* **Enfoque Basado en Diccionarios:** Permite generar reemplazos para el resto de las entidades.

Alguna de las propiedades que cumplen los nuevos reemplazos son:
* **Robustez** --> Se generan reemplazos para cualquier tipo de menci贸n.
* **Integridad** --> Mantienen la estructura y tipo del original.
* **Concordancia** --> Los nuevos reemplazos mantienen relaciones entre s铆.

### 馃敆 Generaci贸n de Reemplazos Mediante Grafos <a name="Generaci贸n_De_Reemplazos_Mediante_Grafos"></a>

Permite generar reemplazos entre distintos tipos de entidades manteniendo su jerarqu铆a (Ver Figura 8). La jerarqu铆a implementada es **Provincia > Ciudad > C贸digo Postal**.

![Grafos](assets/normalizarGrafo.png)
![Grafos](assets/reemplazosValidosGrafo.png)
**Figura 8: Generaci贸n de reemplazos mediante grafos.**

### 馃摃 Generaci贸n de Reemplazos Mediante Diccionarios <a name="Generaci贸n_De_Reemplazos_Mediante_Diccionarios"></a>

Permite generar reemplazos para el resto de las entidades manteniendo su estructura (Ver Figura 9).

![Diccionario](assets/estructuraDiccionario.png)
**Figura 9: Estructura del diccionario de reemplazos.**

## 馃煱 Normalizaci贸n de las  Menciones <a name="Normalizaci贸n_De_Las_Menciones"></a>

Algunos tipos de documentos tienen partes cuyo texto se escribe todo en may煤sculas o en min煤sculas. Para evitar que sea evidente que el documento ha sido modificado, se normalizan los reemplazos para que estos tengan el formato de la menci贸n original: todo may煤sculas, todo min煤sculas, etc.

## 馃搫 Generaci贸n del nuevo documento PDF <a name="Generaci贸n_Del_Nuevo_Documento_Pdf"></a>

Este componente se encarga de tomar el texto del documento original, y de generar un nuevo documento PDF con dicho texto y reemplazando las menciones por sus reemplazos normalizados (Ver Figura 10).

![Generar PDF](assets/ejemploOutputPDF.png)
**Figura 10: Documento final generado por la herramienta.**

# 馃О Rendimiento de la herramienta <a name="Rendimiento_De_La_Herramienta"></a>
## 鈿栵笍 Evaluaci贸n del rendimiento <a name="Evaluaci贸n_Del_Rendimiento"></a>
Tras la realizaci贸n de varias pruebas con distintos documentos de diferente tama帽o, n煤mero de p谩ginas, menciones, palabras, etc, los resultados (en t茅rminos de rendimiento) obtenidos son los siguientes:

![Rendimiento Etapas](assets/tiempoTotalDesglose.png)
![Rendimiento Etapas Zoom](assets/tiempoTotalDesgloseZoom.png)
**Figura 11: Rendimiento de la herramienta por componentes.**

![Rendimiento generaci贸n reemplazos](assets/tiempoReemplazos.png)
**Figura 12: Rendimiento de la herramienta a la hora de realizar la generaci贸n de los reemplazos.**

# 鈿欙笍 Estructura del Repositorio <a name="Estructura_Del_Repositorio"></a>

El repositorio se encuentra estructurado de la siguiente forma:

```
.
鈹溾攢鈹? app/ # Herramienta software
鈹?   鈹溾攢鈹? datos/ # Datos para generar el grafo y el diccionario
鈹?   鈹溾攢鈹? doc/ # Directorio donde se almacenan los documentos en raw para la herramienta
鈹?   鈹溾攢鈹? keys/ # Claves para generar el certificado digital de la herramienta
鈹?   鈹溾攢鈹? models/ # Modelo de PLN de la herramienta
鈹?   鈹溾攢鈹? output/ # Directorio donde se almacenan los documentos finales procesados en la herramienta
鈹?   鈹溾攢鈹? src/ # C贸digo fuente de las distintas componentes de la herramienta
鈹?   鈹溾攢鈹? static/ # Elementos est谩ticos de la herramienta (logo, css, imgs, etc)
鈹?   鈹溾攢鈹? templates/ # P谩ginas html de la herramienta
鈹?   鈹溾攢鈹? tmp/ # Directorio donde se almacenan los documentos temporales de la herramienta
鈹?   鈹溾攢鈹? app.py # Script principal para el despliegue de la herramienta
鈹?   鈹溾攢鈹? config.json # Configuraci贸n de la herramienta
鈹?   鈹斺攢鈹? Utils.py # Funciones comunes de los distintos m贸dulos
鈹溾攢鈹? assets/ # Im谩genes del README
鈹溾攢鈹? Documentacion Tecnica/ # Memoria y presentaci贸n del proyecto en PDF
鈹溾攢鈹? Notebooks/聽# Ficheros .ipynb adicionales
鈹溾攢鈹? config.cfg # Configuraci贸n para entrenar el modelo de Spacy
鈹溾攢鈹? README.md
鈹斺攢鈹? requirements.txt # Dependencias python para ejecutar la herramienta
```

# 馃摲 Capturas de Pantalla <a name="Capturas"></a>

![Herramienta: Cargar Documento](assets/apendiceExaminarDocumento.png)
**Figura 13: Herramienta: Examinar documento a anonimizar.**

![Herramienta: Detectar Menciones](assets/apendiceCargarDocumento.png)
**Figura 14: Herramienta: Detectadas menciones personales en el documento.**

![Herramienta: Anonimizar Menciones](assets/apendiceAnonimizarDocumento.png)
**Figura 15: Herramienta: Menciones anonimizadas.**

![Herramienta: Exportar Documento](assets/aprendiceExportarDocumento.png)
**Figura 16: Herramienta: Exportar documento anonimizado.**

![Herramienta: Documento Exportado](assets/apendiceOutputDocumento.png)
**Figura 17: Herramienta: Documento Exportado.**

# 馃敋 Conclusiones y Trabajo Futuro <a name="Conclusiones_Y_Trabajo_Futuro"></a>
## 馃敋 Conclusiones <a name="Conclusiones"></a>
Las conclusiones que se han obtenido tras la realizaci贸n del proyecto son:

* Los resultados obtenidos durante la creaci贸n y optimizaci贸n del modelo son muy buenos a pesar de la variedad de las menciones a detectar (en torno a un 94% de detecci贸n).
* La utilizaci贸n de expresiones regulares ha mejorado de forma sustancial los resultados para menciones con una estructura predecible (57,59% de media).
* Los tiempos de ejecuci贸n de los componentes desarrollados en el proyecto son bajos (0,19 segundos de media para documentos entre 25 y 630 menciones, aproximadamente 240 menciones de media), y se mantienen constantes (o aumentan muy ligeramente) a medida que aumentan las palabras o las menciones: **Escalabilidad**.
* A pesar de las limitaciones de la herramienta, esta puede considerarse gen茅rica ya que es posible adaptarla a cualquier contexto modificando el modelo o la base de conocimiento para generar los reemplazos.

## 馃敭 Trabajo Futuro <a name="Trabajo_Futuro"></a>

Las posibles l铆neas de trabajo futuro que se abren tras la finalizaci贸n del proyecto son:
* Optimizaci贸n o implementaci贸n de un mecanismo eficiente de b煤squeda en grafos.
* Implementaci贸n de diccionarios din谩micos para realizar los reemplazos.
* Aplicaci贸n de la herramienta a otro tipo de documentos del mismo tipo, o a los mismos documentos pero en otra administraci贸n distinta.
* Mejora de la gesti贸n y manejo de los PDF.
* Implementaci贸n de nuevos componentes en el *pipeline* (introducci贸n de metadatos para volver a las menciones originales, cifrado de los metadatos, etc).