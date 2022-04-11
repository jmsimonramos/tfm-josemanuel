import json
import pickle
import string
from pathlib import Path
class Utils():
    def calcularTiempoEjecucion(self, inicio, fin):
        return round(fin - inicio, 3)
    
    def escribirTiempoEjecucion(self, modo, contenido):
        try:
            with open(self.cargarConfiguracion()["META"]["path_logs"], modo, encoding = "utf-8") as file:
                file.write(contenido)
        except FileNotFoundError:
            with open(self.cargarConfiguracion()["META"]["path_logs"], "w", encoding = "utf-8") as file:
                file.write(contenido)

    def cargarFicheroDatos(self, ruta):
        with open (ruta, "r", encoding="utf-8") as file:
            lineas = [ x.strip() for x in file.readlines() ]
        return lineas
        
    def cargarConfiguracion(self, filepath='./config.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config

    def cargarTexto(self, fichero):
        with open(fichero, 'r', encoding='utf-8') as file:
            texto = ' '.join([x.rstrip() for x in file])
        return texto  
    
    def serializarObjeto(self, ruta, objeto):
        with open(ruta, "wb") as file:
            pickle.dump(objeto, file, pickle.HIGHEST_PROTOCOL)

    def deserializarObjeto(self, ruta):
        with open(ruta, "rb") as file:
            data = pickle.load(file)
        return data
    def ordenarDiccionario(self, diccionario):
        return dict( sorted(diccionario.items(), key = lambda item: item[1]) )

    def cargarDiccionarioReemplazos(self):
        configuracion = self.cargarConfiguracion()

        try:  # We tried to load the serialized file
            with open(configuracion["META"]["path_diccionario_bin"], 'rb') as dictionary_file:
                global_dict = pickle.load(dictionary_file)
        except Exception:  
            dir_path = Path(configuracion["META"]["path_diccionario_files"])
            files = list(dir_path.glob('./DIC_*.txt'))
            
            global_dict = {}
            data_dict = {}

            for f in files:
                key_name = f.stem.replace("DIC_", "")
                with open(f, 'r', encoding='utf8') as file:
                    if key_name == "PREFIJO":
                        data_dict[key_name] = [x.strip().split(';') for x in file]
                    elif key_name == "DIRECCION":
                        data_dict[key_name] = [x.strip().split(';') for x in file]
                    else:
                        data_dict[key_name] = [x.strip() for x in file]

            for key_name, items in data_dict.items():
                aux_dict = {}
                
                if key_name == "PREFIJO":
                    prefijos_dict = {}
                    for prefix in items:
                        prefijos_dict[string.capwords(prefix[0])] = prefix[1]
                        aux_dict[prefix[1]] = string.capwords(prefix[0])
                    global_dict[key_name] = aux_dict
                    global_dict["PREFIJO_PROV"] = prefijos_dict
                elif key_name == "EMAIL":
                    global_dict[key_name] = data_dict[key_name]
                elif key_name == "DIRECCION":
                    for street, town in data_dict[key_name]:
                        street_tokens = len(street.split(' '))
                        aux_dict.setdefault(street_tokens, {}).setdefault(town, []).append(street)
                    global_dict[key_name] = aux_dict

                elif key_name == "URL":
                    global_dict[key_name] = data_dict[key_name]
                else:
                    for item in items:
                        aux_dict.setdefault(len(item.split(' ')), []).append(item)

                    global_dict[key_name] = aux_dict
            
                self.serializarObjeto(ruta = configuracion["META"]["path_diccionario_bin"], objeto = global_dict)
            
        return global_dict

    def normalizarEntidad(self, original, reemplazo):    
        if original.isupper():
            return reemplazo.upper()
        elif original.islower():
            return reemplazo.lower()
        else:
            return string.capwords(reemplazo)