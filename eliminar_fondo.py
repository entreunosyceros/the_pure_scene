import asyncio
import io
import os
import platform
import subprocess

from PIL import Image
from rembg import remove

from postproceso import EXTENSIONES, exportar, extension_formato, postprocesar, ya_tiene_sinfondo


def nombre_sin_fondo(filename, formato="png"):
    base, _ext = os.path.splitext(filename)
    return f"{base}_sinfondo.{extension_formato(formato)}"


def abrir_carpeta_destino(carpeta):
    try:
        if platform.system() == "Windows":
            subprocess.run(["explorer", carpeta])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", carpeta])
        else:
            subprocess.run(["open", carpeta])
    except Exception as e:
        print(f"Error al abrir la carpeta: {e}")


def quitar_fondo_rgba(input_path):
    with open(input_path, "rb") as origen:
        datos = remove(origen.read())
    return Image.open(io.BytesIO(datos)).convert("RGBA")


def eliminar_fondo(input_path, output_path, opciones=None, mascara_path=None):
    opciones = opciones or {}
    mascara = quitar_fondo_rgba(input_path)
    if mascara_path:
        os.makedirs(os.path.dirname(mascara_path) or ".", exist_ok=True)
        mascara.save(mascara_path, "PNG")
    final = postprocesar(mascara, opciones)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    output_path = exportar(final, output_path, opciones)
    return mascara, final, output_path


def _debe_omitir(filename, output_path, omitir_existentes):
    if ya_tiene_sinfondo(filename):
        return True
    if omitir_existentes and os.path.exists(output_path):
        return True
    return False


async def eliminar_fondo_carpeta(
    input_dir,
    output_dir,
    progress_bar,
    page,
    cancel_event=None,
    omitir_existentes=True,
    opciones=None,
    archivos=None,
):
    opciones = opciones or {}
    if archivos:
        rutas = [p for p in archivos if p.lower().endswith(EXTENSIONES)]
    else:
        rutas = [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if f.lower().endswith(EXTENSIONES)
        ]

    total_files = len(rutas)
    procesados_ok = 0
    omitidos = 0
    cancelado = False

    for indice, input_path in enumerate(rutas, start=1):
        if cancel_event is not None and cancel_event.is_set():
            cancelado = True
            break

        filename = os.path.basename(input_path)
        formato = opciones.get("formato", "png")
        output_path = os.path.join(output_dir, nombre_sin_fondo(filename, formato))

        if _debe_omitir(filename, output_path, omitir_existentes):
            omitidos += 1
            progress_bar.value = indice / total_files if total_files else 1
            page.update()
            continue

        await asyncio.to_thread(eliminar_fondo, input_path, output_path, opciones)
        procesados_ok += 1
        progress_bar.value = indice / total_files if total_files else 1
        page.update()

    return {
        "total": total_files,
        "procesados": procesados_ok,
        "omitidos": omitidos,
        "cancelado": cancelado,
    }
