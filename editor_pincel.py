import os

import flet as ft
import numpy as np
from PIL import Image

from postproceso import damero, exportar, img_a_b64, postprocesar

PREVIEW = 520
ZOOM_MIN = 0.5
ZOOM_MAX = 4.0
ZOOM_PASO = 0.25


def _escala_ajuste(img_w, img_h):
    if img_w <= 0 or img_h <= 0:
        return 1.0
    return min(PREVIEW / img_w, PREVIEW / img_h)


def _region_visible(img_w, img_h, zoom, pan_x, pan_y):
    fit = _escala_ajuste(img_w, img_h)
    escala = fit * max(ZOOM_MIN, min(ZOOM_MAX, zoom))
    vis_w = min(img_w, PREVIEW / escala)
    vis_h = min(img_h, PREVIEW / escala)
    max_x = max(0.0, img_w - vis_w)
    max_y = max(0.0, img_h - vis_h)
    x0 = max(0.0, min(max_x, pan_x * max_x))
    y0 = max(0.0, min(max_y, pan_y * max_y))
    return x0, y0, x0 + vis_w, y0 + vis_h, escala


def _vista_zoom(img, zoom, pan_x, pan_y):
    img = img.convert("RGBA")
    x0, y0, x1, y1, _escala = _region_visible(img.width, img.height, zoom, pan_x, pan_y)
    recorte = img.crop((int(x0), int(y0), max(int(x0) + 1, int(x1)), max(int(y0) + 1, int(y1))))
    recorte = recorte.resize((PREVIEW, PREVIEW), Image.Resampling.NEAREST if zoom >= 2 else Image.Resampling.BILINEAR)
    lienzo = damero((PREVIEW, PREVIEW))
    lienzo.alpha_composite(recorte, (0, 0))
    return lienzo


def _coords_en_imagen(lx, ly, img_w, img_h, zoom, pan_x, pan_y):
    if img_w <= 0 or img_h <= 0:
        return 0, 0
    x0, y0, x1, y1, _escala = _region_visible(img_w, img_h, zoom, pan_x, pan_y)
    vis_w = max(1e-6, x1 - x0)
    vis_h = max(1e-6, y1 - y0)
    x = int(x0 + (lx / PREVIEW) * vis_w)
    y = int(y0 + (ly / PREVIEW) * vis_h)
    return max(0, min(img_w - 1, x)), max(0, min(img_h - 1, y))


def _aplicar_pincel(actual_np, original_np, x, y, radio, restaurar):
    alto, ancho = actual_np.shape[:2]
    x0 = max(0, x - radio)
    y0 = max(0, y - radio)
    x1 = min(ancho, x + radio + 1)
    y1 = min(alto, y + radio + 1)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.ogrid[y0:y1, x0:x1]
    marca = (xx - x) ** 2 + (yy - y) ** 2 <= radio ** 2
    recorte = actual_np[y0:y1, x0:x1]
    if restaurar:
        recorte[marca, :3] = original_np[y0:y1, x0:x1][marca, :3]
        recorte[marca, 3] = 255
    else:
        recorte[marca, 3] = 0


def abrir_editor_pincel(page, original_path, mascara_img, output_path, get_opciones, on_guardado):
    if any(getattr(v, "route", None) == "/pincel" for v in page.views):
        return
    if not original_path or not os.path.isfile(original_path) or mascara_img is None:
        return

    original = Image.open(original_path).convert("RGBA")
    if original.size != mascara_img.size:
        original = original.resize(mascara_img.size, Image.Resampling.LANCZOS)

    actual = mascara_img.convert("RGBA").copy()
    estado = {
        "original_np": np.array(original),
        "actual_np": np.array(actual),
        "anterior": None,
        "size": actual.size,
        "ultimo": None,
        "zoom": 1.0,
        "pan_x": 0.5,
        "pan_y": 0.5,
        "pan_inicio": None,
        "mover_vista": False,
    }

    def imagen_actual():
        return Image.fromarray(estado["actual_np"])

    def etiqueta_zoom():
        return f"{int(round(estado['zoom'] * 100))} %"

    def redibujar():
        vista = _vista_zoom(imagen_actual(), estado["zoom"], estado["pan_x"], estado["pan_y"])
        img_preview.src_base64 = img_a_b64(vista)
        zoom_label.value = etiqueta_zoom()
        zoom_slider.value = estado["zoom"]
        page.update()

    def pintar_en(lx, ly, continuar=False):
        x, y = _coords_en_imagen(
            lx, ly, *estado["size"], estado["zoom"], estado["pan_x"], estado["pan_y"]
        )
        radio = int(tamano_slider.value or 18)
        puntos = [(x, y)]
        if continuar and estado["ultimo"] is not None:
            x0, y0 = estado["ultimo"]
            dist = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
            pasos = max(1, int(dist / max(radio / 2.5, 1)))
            puntos = [
                (int(x0 + (x - x0) * i / pasos), int(y0 + (y - y0) * i / pasos))
                for i in range(1, pasos + 1)
            ]
        restaurar = modo.value == "restaurar"
        for px, py in puntos:
            _aplicar_pincel(estado["actual_np"], estado["original_np"], px, py, radio, restaurar)
        estado["ultimo"] = (x, y)
        redibujar()

    def guardar_deshacer():
        estado["anterior"] = estado["actual_np"].copy()
        estado["ultimo"] = None

    def on_pan_start(e: ft.DragStartEvent):
        if estado["mover_vista"] or modo_vista.value == "mover":
            estado["pan_inicio"] = (e.local_x, e.local_y, estado["pan_x"], estado["pan_y"])
            return
        guardar_deshacer()
        pintar_en(e.local_x, e.local_y, continuar=False)

    def on_pan_update(e: ft.DragUpdateEvent):
        if estado["pan_inicio"] is not None:
            lx0, ly0, px0, py0 = estado["pan_inicio"]
            img_w, img_h = estado["size"]
            _x0, _y0, x1, y1, escala = _region_visible(
                img_w, img_h, estado["zoom"], px0, py0
            )
            vis_w = max(1e-6, x1 - _x0)
            vis_h = max(1e-6, y1 - _y0)
            max_x = max(0.0, img_w - vis_w)
            max_y = max(0.0, img_h - vis_h)
            dx = (e.local_x - lx0) / PREVIEW * vis_w
            dy = (e.local_y - ly0) / PREVIEW * vis_h
            if max_x > 0:
                estado["pan_x"] = max(0.0, min(1.0, (px0 * max_x - dx) / max_x))
            if max_y > 0:
                estado["pan_y"] = max(0.0, min(1.0, (py0 * max_y - dy) / max_y))
            redibujar()
            return
        pintar_en(e.local_x, e.local_y, continuar=True)

    def on_pan_end(e=None):
        estado["pan_inicio"] = None

    def on_tap_down(e: ft.TapEvent):
        if estado["mover_vista"] or modo_vista.value == "mover":
            return
        guardar_deshacer()
        pintar_en(e.local_x, e.local_y, continuar=False)

    def aplicar_zoom(nuevo, ancla=None):
        img_w, img_h = estado["size"]
        punto = None
        if ancla is not None and img_w > 0:
            punto = _coords_en_imagen(
                ancla[0], ancla[1], img_w, img_h, estado["zoom"], estado["pan_x"], estado["pan_y"]
            )
        estado["zoom"] = max(ZOOM_MIN, min(ZOOM_MAX, round(float(nuevo) / ZOOM_PASO) * ZOOM_PASO))
        if punto is not None:
            x, y = punto
            x0, y0, x1, y1, _e = _region_visible(img_w, img_h, estado["zoom"], 0.5, 0.5)
            vis_w = max(1e-6, x1 - x0)
            vis_h = max(1e-6, y1 - y0)
            max_x = max(0.0, img_w - vis_w)
            max_y = max(0.0, img_h - vis_h)
            deseado_x = x - (ancla[0] / PREVIEW) * vis_w
            deseado_y = y - (ancla[1] / PREVIEW) * vis_h
            estado["pan_x"] = max(0.0, min(1.0, deseado_x / max_x)) if max_x > 0 else 0.5
            estado["pan_y"] = max(0.0, min(1.0, deseado_y / max_y)) if max_y > 0 else 0.5
        redibujar()

    def on_scroll(e: ft.ScrollEvent):
        delta = e.scroll_delta_y or 0
        if delta == 0:
            return
        paso = -ZOOM_PASO if delta > 0 else ZOOM_PASO
        aplicar_zoom(estado["zoom"] + paso, ancla=(e.local_x, e.local_y))

    def zoom_mas(e=None):
        aplicar_zoom(estado["zoom"] + ZOOM_PASO)

    def zoom_menos(e=None):
        aplicar_zoom(estado["zoom"] - ZOOM_PASO)

    def zoom_reset(e=None):
        estado["pan_x"] = 0.5
        estado["pan_y"] = 0.5
        aplicar_zoom(1.0)

    def on_zoom_slider(e=None):
        aplicar_zoom(zoom_slider.value or 1.0)

    def deshacer(e=None):
        if estado["anterior"] is None:
            aviso.value = "No hay un trazo que deshacer."
            page.update()
            return
        estado["actual_np"] = estado["anterior"]
        estado["anterior"] = None
        redibujar()
        aviso.value = "Último trazo deshecho."
        page.update()

    def guardar(e=None):
        opciones = get_opciones() if get_opciones else {}
        actual_img = imagen_actual()
        final = postprocesar(actual_img, opciones)
        ruta = exportar(final, output_path, opciones)
        if on_guardado:
            on_guardado(actual_img, final, ruta)
        close_window()

    def close_window(e=None):
        page.window.width = ventana_previa["width"]
        page.window.height = ventana_previa["height"]
        page.window.maximized = ventana_previa["maximized"]
        if len(page.views) > 1:
            page.views.pop()
        page.update()

    img_preview = ft.Image(
        src_base64=img_a_b64(_vista_zoom(imagen_actual(), 1.0, 0.5, 0.5)),
        width=PREVIEW,
        height=PREVIEW,
        fit=ft.ImageFit.FILL,
        gapless_playback=True,
    )
    aviso = ft.Text(
        "Pinta sobre el recorte: acierto recupera pelo u objeto; error borra restos de fondo. Usa el zoom para bordes finos.",
        size=14,
    )
    modo = ft.RadioGroup(
        value="restaurar",
        content=ft.Column(
            [
                ft.Radio(value="restaurar", label="Acierto: recuperar (pelo, bordes)"),
                ft.Radio(value="borrar", label="Error: borrar restos de fondo"),
            ]
        ),
    )
    modo_vista = ft.RadioGroup(
        value="pintar",
        content=ft.Column(
            [
                ft.Radio(value="pintar", label="Pincel"),
                ft.Radio(value="mover", label="Mover vista (con zoom)"),
            ]
        ),
    )
    tamano_slider = ft.Slider(min=4, max=80, value=18, divisions=76, label="{value} px")
    zoom_slider = ft.Slider(
        min=ZOOM_MIN,
        max=ZOOM_MAX,
        value=1.0,
        divisions=int((ZOOM_MAX - ZOOM_MIN) / ZOOM_PASO),
        label="{value}x",
        on_change_end=on_zoom_slider,
    )
    zoom_label = ft.Text(etiqueta_zoom(), weight=ft.FontWeight.BOLD)

    panel_imagen = ft.Column(
        [
            ft.Container(
                content=ft.GestureDetector(
                    content=img_preview,
                    drag_interval=20,
                    mouse_cursor=ft.MouseCursor.PRECISE,
                    on_pan_start=on_pan_start,
                    on_pan_update=on_pan_update,
                    on_pan_end=on_pan_end,
                    on_tap_down=on_tap_down,
                    on_scroll=on_scroll,
                ),
                width=PREVIEW,
                height=PREVIEW,
                alignment=ft.alignment.center,
                bgcolor="#222222",
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
            aviso,
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=2,
    )
    panel_controles = ft.Column(
        [
            ft.Text("Pincel de acierto / error", weight=ft.FontWeight.BOLD, size=18),
            modo,
            ft.Text("Vista"),
            modo_vista,
            ft.Text("Zoom"),
            ft.Row(
                [
                    ft.ElevatedButton("−", on_click=zoom_menos, tooltip="Alejar"),
                    zoom_label,
                    ft.ElevatedButton("+", on_click=zoom_mas, tooltip="Acercar"),
                    ft.TextButton("100 %", on_click=zoom_reset),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            zoom_slider,
            ft.Text("Tamaño del pincel"),
            tamano_slider,
            ft.Row(
                [
                    ft.ElevatedButton("Deshacer trazo", on_click=deshacer),
                    ft.ElevatedButton("Guardar y volver", on_click=guardar),
                ],
                wrap=True,
            ),
            ft.Text(
                "Acerca con + o la rueda del ratón. Con zoom activo, elige «Mover vista» para desplazarte y luego vuelve a «Pincel».",
                size=12,
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
    page.views.append(
        ft.View(
            route="/pincel",
            appbar=ft.AppBar(
                title=ft.Text("Retocar recorte"),
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
    )
    page.update()
