import flet as ft
from PIL import Image, ImageDraw

from postproceso import encajar, img_a_b64

PREVIEW = 520


def _coords(lx, ly, img_w, img_h):
    if img_w <= 0 or img_h <= 0:
        return 0, 0
    escala = min(PREVIEW / img_w, PREVIEW / img_h)
    visible_w, visible_h = img_w * escala, img_h * escala
    origen_x = (PREVIEW - visible_w) / 2
    origen_y = (PREVIEW - visible_h) / 2
    x = int((lx - origen_x) / escala)
    y = int((ly - origen_y) / escala)
    return max(0, min(img_w - 1, x)), max(0, min(img_h - 1, y))


def abrir_editor_recorte(page, imagen, on_guardado):
    if any(getattr(v, "route", None) == "/recorte" for v in page.views):
        return
    if imagen is None:
        return

    estado = {
        "img": imagen.convert("RGBA").copy(),
        "x0": None,
        "y0": None,
        "x1": None,
        "y1": None,
    }

    def con_marco():
        vista = estado["img"].copy()
        if None not in (estado["x0"], estado["y0"], estado["x1"], estado["y1"]):
            caja = (
                min(estado["x0"], estado["x1"]),
                min(estado["y0"], estado["y1"]),
                max(estado["x0"], estado["x1"]),
                max(estado["y0"], estado["y1"]),
            )
            if caja[2] - caja[0] > 2 and caja[3] - caja[1] > 2:
                draw = ImageDraw.Draw(vista)
                draw.rectangle(caja, outline=(180, 80, 255, 255), width=max(2, vista.width // 200))
        return vista

    def redibujar():
        img_preview.src_base64 = img_a_b64(encajar(con_marco(), (PREVIEW, PREVIEW), con_damero=True))
        page.update()

    def on_pan_start(e: ft.DragStartEvent):
        estado["x0"], estado["y0"] = _coords(e.local_x, e.local_y, *estado["img"].size)
        estado["x1"], estado["y1"] = estado["x0"], estado["y0"]
        redibujar()

    def on_pan_update(e: ft.DragUpdateEvent):
        estado["x1"], estado["y1"] = _coords(e.local_x, e.local_y, *estado["img"].size)
        redibujar()

    def aplicar(e=None):
        if None in (estado["x0"], estado["y0"], estado["x1"], estado["y1"]):
            aviso.value = "Arrastra sobre la imagen para marcar el recorte."
            page.update()
            return
        caja = (
            min(estado["x0"], estado["x1"]),
            min(estado["y0"], estado["y1"]),
            max(estado["x0"], estado["x1"]),
            max(estado["y0"], estado["y1"]),
        )
        if caja[2] - caja[0] < 4 or caja[3] - caja[1] < 4:
            aviso.value = "El recorte es demasiado pequeño."
            page.update()
            return
        recorte = estado["img"].crop(caja)
        if on_guardado:
            on_guardado(recorte)
        close_window()

    def close_window(e=None):
        page.window.width = ventana_previa["width"]
        page.window.height = ventana_previa["height"]
        page.window.maximized = ventana_previa["maximized"]
        if len(page.views) > 1:
            page.views.pop()
        page.update()

    img_preview = ft.Image(
        src_base64=img_a_b64(encajar(estado["img"], (PREVIEW, PREVIEW), con_damero=True)),
        width=PREVIEW,
        height=PREVIEW,
        fit=ft.ImageFit.CONTAIN,
        gapless_playback=True,
    )
    aviso = ft.Text("Arrastra para marcar el recorte y pulsa Aplicar.", size=14)

    ventana_previa = {
        "width": page.window.width,
        "height": page.window.height,
        "maximized": page.window.maximized,
    }
    page.window.maximized = True
    page.views.append(
        ft.View(
            route="/recorte",
            appbar=ft.AppBar(
                title=ft.Text("Recortar a mano"),
                bgcolor="purple",
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=close_window),
                actions=[ft.TextButton("Cerrar", on_click=close_window, style=ft.ButtonStyle(color="white"))],
            ),
            controls=[
                ft.Column(
                    [
                        ft.Container(
                            content=ft.GestureDetector(
                                content=img_preview,
                                drag_interval=30,
                                on_pan_start=on_pan_start,
                                on_pan_update=on_pan_update,
                            ),
                            width=PREVIEW,
                            height=PREVIEW,
                            alignment=ft.alignment.center,
                            bgcolor="#222222",
                        ),
                        aviso,
                        ft.ElevatedButton("Aplicar recorte", on_click=aplicar),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                )
            ],
            padding=20,
            fullscreen_dialog=True,
        )
    )
    page.update()
