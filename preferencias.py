import json
import os
from datetime import datetime

from constants import BASE_DIR
from _runtime_paths import data_dir

RUTA = os.path.join(data_dir(BASE_DIR), "temp", "preferencias.json")
MAX_HISTORIAL = 12


def _vacio():
    return {
        "origen": "",
        "destino": "",
        "formato": "png",
        "tamano": "original",
        "historial": [],
    }


def cargar():
    try:
        with open(RUTA, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        base = _vacio()
        base.update(datos if isinstance(datos, dict) else {})
        if not isinstance(base.get("historial"), list):
            base["historial"] = []
        return base
    except (OSError, ValueError):
        return _vacio()


def guardar(prefs):
    os.makedirs(os.path.dirname(RUTA), exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as archivo:
        json.dump(prefs, archivo, ensure_ascii=False, indent=2)


def recordar_carpetas(origen=None, destino=None):
    prefs = cargar()
    if origen:
        prefs["origen"] = origen
    if destino:
        prefs["destino"] = destino
    guardar(prefs)
    return prefs


def recordar_exportacion(formato=None, tamano=None):
    prefs = cargar()
    if formato:
        prefs["formato"] = formato
    if tamano:
        prefs["tamano"] = tamano
    guardar(prefs)


def añadir_historial(origen, destino, carpeta_destino):
    prefs = cargar()
    entrada = {
        "nombre": os.path.basename(destino or origen or ""),
        "origen": origen or "",
        "destino": destino or "",
        "carpeta_destino": carpeta_destino or os.path.dirname(destino or ""),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    resto = [h for h in prefs["historial"] if h.get("destino") != entrada["destino"]]
    prefs["historial"] = [entrada] + resto
    prefs["historial"] = prefs["historial"][:MAX_HISTORIAL]
    guardar(prefs)
    return prefs["historial"]
