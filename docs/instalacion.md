# Instalación y arranque

La forma recomendada de iniciar **The Pure Scene** es:

```bash
python3 run_app.py
```

`run_app.py` hace tres cosas:

1. Crea un entorno virtual en `venv/` si no existe (usa el módulo estándar `venv`; si falla, intenta `virtualenv`).
2. Instala las dependencias de `requirements.txt` dentro de ese entorno.
3. Lanza `main.py` con el Python del entorno virtual.

## Requisitos

- Python 3.10 o superior (probado con Python 3.13)
- Conexión a internet la primera vez, para descargar paquetes y el modelo de rembg

Dependencias principales:

| Paquete | Uso |
| --- | --- |
| `flet[desktop]==0.28.3` | Interfaz de escritorio |
| `rembg[cpu]` | Quitar el fondo (incluye `onnxruntime`) |
| `Pillow` | Abrir, editar y exportar imágenes |
| `pystray` | Icono en la bandeja del sistema |

Instalación manual, si no usas `run_app.py`:

```bash
python3 -m venv venv
source venv/bin/activate   # en Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Primera ejecución

Al arrancar por primera vez:

- Se crea `venv/` en la carpeta del proyecto.
- rembg puede descargar el modelo de segmentación; tarda más que los siguientes inicios.
- Aparece la ventana **The Pure Scene** y un icono en la bandeja.

Si ves errores `Gdk-CRITICAL` / `Failed to initialize GLArea`, suele ser un desajuste del driver NVIDIA. Reinicia el equipo y vuelve a lanzar la app. The Pure Scene usa ventana de escritorio; no abre el navegador salvo `TPS_VIEW=web`.

Los siguientes arranques reutilizan el entorno y son más rápidos.

## Carpetas que crea el programa

| Carpeta | Para qué sirve |
| --- | --- |
| `venv/` | Entorno virtual (no hace falta versionarla) |
| `temp/` | Preferencias, historial y máscara temporal del pincel |
| `descargas/` | Imágenes bajadas desde el [buscador](buscador.md) |

## Siguiente categoría

- [Quitar fondo](quitar-fondo.md)
