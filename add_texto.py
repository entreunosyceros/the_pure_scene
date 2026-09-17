import base64
import io
import os

import flet as ft
from PIL import Image, ImageDraw, ImageFont

from constants import BASE_DIR

PREVIEW = 480
IMAGEN_POR_DEFECTO = os.path.join(BASE_DIR, "assets", "default-image.png")
RUTAS_FUENTES = {
    "Arial": os.path.join(BASE_DIR, "assets", "fonts", "Arial.ttf"),
    "Times New Roman": os.path.join(BASE_DIR, "assets", "fonts", "Times New Roman.ttf"),
    "Courier New": os.path.join(BASE_DIR, "assets", "fonts", "Courier New.ttf"),
    "Comic Sans": os.path.join(BASE_DIR, "assets", "fonts", "ComicSans.ttf"),
}


def _archivo_a_b64(ruta):
    img = Image.open(ruta).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _color_valido(valor):
    valor = (valor or "").strip()
    if valor.startswith("#") and len(valor) in (4, 7):
        return valor
    return "#000000"


def _fuente(nombre, tamano):
    ruta = RUTAS_FUENTES.get(nombre)
    if ruta and os.path.isfile(ruta):
        return ImageFont.truetype(ruta, tamano)
    return ImageFont.load_default()


def _coords_en_imagen(lx, ly, img_w, img_h):
    if img_w <= 0 or img_h <= 0:
        return 0, 0
    escala = min(PREVIEW / img_w, PREVIEW / img_h)
    visible_w, visible_h = img_w * escala, img_h * escala
    origen_x = (PREVIEW - visible_w) / 2
    origen_y = (PREVIEW - visible_h) / 2
    x = int((lx - origen_x) / escala)
    y = int((ly - origen_y) / escala)
    return max(0, min(img_w - 1, x)), max(0, min(img_h - 1, y))


def abrir_ventana_texto_imagen(page):
    if any(getattr(v, "route", None) == "/add-texto" for v in page.views):
        return
    estado = {
        "original": None,
        "compuesta": None,
        "tamano": (0, 0),
        "capas": [],
        "seleccionada": None,
    }

    def mostrar_aviso(mensaje):
        aviso.value = mensaje
        page.update()

    def imagen_compuesta():
        img = Image.open(estado["original"]).convert("RGBA")
        draw = ImageDraw.Draw(img)
        for capa in estado["capas"]:
            draw.text(
                (capa["x"], capa["y"]),
                capa["texto"],
                font=_fuente(capa["fuente"], capa["tamaño"]),
                fill=capa["color"],
            )
        return img

    def redibujar_imagen():
        if not estado["original"]:
            return
        img = imagen_compuesta()
        estado["tamano"] = img.size
        estado["compuesta"] = img
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_preview.src_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
        page.update()

    def handle_file_picker_result(e):
        if not e.files:
            return
        estado["original"] = e.files[0].path
        estado["capas"].clear()
        estado["seleccionada"] = None
        redibujar_imagen()
        mostrar_aviso("Imagen cargada. Escribe un texto y pulsa sobre la imagen para colocarlo.")

    def datos_formulario():
        texto = (texto_field.value or "").strip()
        if not texto:
            mostrar_aviso("Escribe el texto antes de añadirlo.")
            return None
        tamano = int(tamaño_field.value) if (tamaño_field.value or "").isdigit() else 40
        return {
            "texto": texto,
            "fuente": fuente_dropdown.value or "Arial",
            "tamaño": max(8, tamano),
            "color": _color_valido(color_field.value),
        }

    def agregar_texto(x, y):
        datos = datos_formulario()
        if not datos:
            return
        datos["x"] = x
        datos["y"] = y
        estado["capas"].append(datos)
        estado["seleccionada"] = len(estado["capas"]) - 1
        redibujar_imagen()
        mostrar_aviso("Texto añadido. Usa las flechas para moverlo o pulsa de nuevo para otro texto.")

    def imagen_on_tap(e: ft.TapEvent):
        if not estado["original"]:
            mostrar_aviso("Carga una imagen primero.")
            return
        img_w, img_h = estado["tamano"]
        x, y = _coords_en_imagen(e.local_x, e.local_y, img_w, img_h)
        agregar_texto(x, y)

    def añadir_en_centro(e=None):
        if not estado["original"]:
            mostrar_aviso("Carga una imagen primero.")
            return
        img_w, img_h = estado["tamano"]
        agregar_texto(img_w // 8, img_h // 8)

    def mover_capa(dx, dy):
        idx = estado["seleccionada"]
        if idx is None:
            mostrar_aviso("No hay un texto seleccionado.")
            return
        estado["capas"][idx]["x"] += dx
        estado["capas"][idx]["y"] += dy
        redibujar_imagen()

    def actualizar_capa(e=None):
        idx = estado["seleccionada"]
        if idx is None:
            mostrar_aviso("No hay un texto seleccionado. Añádelo pulsando la imagen.")
            return
        datos = datos_formulario()
        if not datos:
            return
        estado["capas"][idx].update(datos)
        redibujar_imagen()
        mostrar_aviso("Texto actualizado.")

    def eliminar_texto(e=None):
        idx = estado["seleccionada"]
        if idx is None:
            mostrar_aviso("No hay un texto seleccionado.")
            return
        estado["capas"].pop(idx)
        estado["seleccionada"] = len(estado["capas"]) - 1 if estado["capas"] else None
        redibujar_imagen()
        mostrar_aviso("Texto eliminado.")

    def guardar_imagen(e=None):
        if not estado["compuesta"]:
            mostrar_aviso("Carga una imagen y añade texto antes de guardar.")
            return
        save_picker.save_file(file_name="imagen_con_texto.png", allowed_extensions=["png"])

    def save_image_to_path(e):
        if not e.path or not estado["compuesta"]:
            return
        destino = e.path if e.path.lower().endswith((".png", ".jpg", ".jpeg")) else f"{e.path}.png"
        estado["compuesta"].save(destino)
        mostrar_aviso(f"Imagen guardada en {destino}")

    def close_window(e=None):
        if len(page.views) > 1 and page.views[-1] is vista:
            page.views.pop()
        page.window.maximized = ventana_previa["maximized"]
        if not ventana_previa["maximized"]:
            page.window.width = ventana_previa["width"]
            page.window.height = ventana_previa["height"]
        page.update()

    file_picker = ft.FilePicker(on_result=handle_file_picker_result)
    save_picker = ft.FilePicker(on_result=save_image_to_path)
    for picker in (file_picker, save_picker):
        if picker not in page.overlay:
            page.overlay.append(picker)

    img_preview = ft.Image(
        src_base64=_archivo_a_b64(IMAGEN_POR_DEFECTO),
        width=PREVIEW,
        height=PREVIEW,
        fit=ft.ImageFit.CONTAIN,
        gapless_playback=True,
    )
    aviso = ft.Text("Carga una imagen, escribe el texto y pulsa sobre ella para colocarlo.", size=14)
    texto_field = ft.TextField(label="Texto", value="", expand=True)
    fuente_dropdown = ft.Dropdown(
        label="Familia de la fuente",
        value="Arial",
        options=[ft.dropdown.Option(nombre) for nombre in RUTAS_FUENTES],
        expand=True,
    )
    tamaño_field = ft.TextField(label="Tamaño de la fuente", value="40", keyboard_type=ft.KeyboardType.NUMBER)
    color_field = ft.TextField(label="Color de la fuente (hex)", value="#000000")

    panel_imagen = ft.Column(
        [
            ft.Container(
                content=ft.GestureDetector(
                    content=img_preview,
                    on_tap_down=imagen_on_tap,
                ),
                width=PREVIEW,
                height=PREVIEW,
                alignment=ft.alignment.center,
            ),
            aviso,
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=2,
    )

    panel_controles = ft.Column(
        [
            ft.ElevatedButton(
                "Cargar imagen",
                on_click=lambda e: file_picker.pick_files(
                    allowed_extensions=["png", "jpg", "jpeg", "webp"]
                ),
            ),
            texto_field,
            fuente_dropdown,
            tamaño_field,
            color_field,
            ft.Text("Posición del texto", weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    ft.ElevatedButton("Añadir texto", on_click=añadir_en_centro),
                    ft.ElevatedButton("Arriba", on_click=lambda e: mover_capa(0, -15)),
                    ft.ElevatedButton("Izq.", on_click=lambda e: mover_capa(-15, 0)),
                    ft.ElevatedButton("Der.", on_click=lambda e: mover_capa(15, 0)),
                    ft.ElevatedButton("Abajo", on_click=lambda e: mover_capa(0, 15)),
                ],
                wrap=True,
            ),
            ft.Row(
                [
                    ft.ElevatedButton("Actualizar texto", on_click=actualizar_capa),
                    ft.ElevatedButton("Eliminar texto", on_click=eliminar_texto),
                    ft.ElevatedButton("Guardar imagen", on_click=guardar_imagen),
                ],
                wrap=True,
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=1,
    )

    ventana_previa = {
        "width": page.window.width,
        "height": page.window.height,
        "maximized": page.window.maximized,
    }
    page.window.maximized = True

    vista = ft.View(
        route="/add-texto",
        appbar=ft.AppBar(
            title=ft.Text("Añadir texto a la imagen"),
            bgcolor="purple",
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=close_window, tooltip="Volver"),
            actions=[
                ft.TextButton("Cerrar", on_click=close_window, style=ft.ButtonStyle(color="white")),
            ],
        ),
        controls=[
            ft.Row(
                [panel_imagen, panel_controles],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=30,
            )
        ],
        padding=20,
        fullscreen_dialog=True,
    )
    page.views.append(vista)
    page.update()
