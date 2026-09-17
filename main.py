import asyncio
import os

import flet as ft
from PIL import Image

from constants import BASE_DIR, DEFAULT_IMAGE_PATH
from _runtime_paths import data_dir
from editor_pincel import abrir_editor_pincel
from editor_recorte import abrir_editor_recorte
from eliminar_fondo import (
    abrir_carpeta_destino,
    eliminar_fondo,
    eliminar_fondo_carpeta,
    nombre_sin_fondo,
)
from menu import Menu
from page_config import configure_page
from portapapeles import copiar_imagen
from postproceso import (
    EFECTOS,
    EXTENSIONES,
    FONDOS,
    FORMATOS,
    TAMANOS,
    encajar,
    exportar,
    img_a_b64,
    mezclar_previews,
    parsear_rutas,
    postprocesar,
)
from preferencias import (
    añadir_historial,
    cargar as cargar_prefs,
    recordar_carpetas,
    recordar_exportacion,
)
from tray_icon import create_tray_icon
from ui_layout import _tarjeta, create_ui

TEMP_DIR = os.path.join(data_dir(BASE_DIR), "temp")
MASCARA_PATH = os.path.join(TEMP_DIR, "mascara.png")
PREVIEW_SIZE = (240, 240)
DEFAULT_IMAGE_ABS = os.path.join(BASE_DIR, DEFAULT_IMAGE_PATH)


def _mostrar_imagen(control, img=None, ruta=None):
    if img is not None:
        control.src = None
        control.src_base64 = img_a_b64(encajar(img, PREVIEW_SIZE, con_damero=True))
    elif ruta and os.path.isfile(ruta):
        control.src = None
        control.src_base64 = img_a_b64(encajar(Image.open(ruta), PREVIEW_SIZE, con_damero=True))
    else:
        control.src_base64 = None
        control.src = DEFAULT_IMAGE_PATH


async def main(page: ft.Page):
    configure_page(page)
    create_tray_icon(page, BASE_DIR)
    menu = Menu(page)
    os.makedirs(TEMP_DIR, exist_ok=True)
    prefs = cargar_prefs()

    estado = {
        "input": "",
        "carpeta": "",
        "archivos": [],
        "output_dir": prefs["destino"] if prefs.get("destino") and os.path.isdir(prefs["destino"]) else "",
        "fondo_imagen": "",
        "original_img": None,
        "mascara_img": None,
        "final_img": None,
        "output_path": "",
        "cancel": None,
        "procesando": False,
        "aplicando_post": False,
        "origen_dir": prefs["origen"] if prefs.get("origen") and os.path.isdir(prefs["origen"]) else "",
    }

    img_input = ft.Text(value="No hay imagen seleccionada", expand=1)
    original_image_preview = ft.Image(
        src=DEFAULT_IMAGE_PATH, width=240, height=240, fit=ft.ImageFit.CONTAIN, gapless_playback=True
    )
    removed_bg_image_preview = ft.Image(
        src=DEFAULT_IMAGE_PATH, width=240, height=240, fit=ft.ImageFit.CONTAIN, gapless_playback=True
    )
    progress = ft.ProgressBar(visible=False, color="purple", bgcolor="#444444", bar_height=10)
    progress_text = ft.Text("Progreso:", weight=ft.FontWeight.BOLD, visible=False)
    snack_bar = ft.SnackBar(ft.Text(""))

    fondo_dropdown = ft.Dropdown(
        label="Tipo de fondo",
        value="transparente",
        options=[ft.dropdown.Option(clave, texto) for clave, texto in FONDOS.items()],
        expand=2,
    )
    color1 = ft.TextField(label="Color 1 (hex)", value="#FFFFFF", expand=1, visible=False)
    color2 = ft.TextField(label="Color 2 (hex)", value="#5A2A82", expand=1, visible=False)
    fondo_img_label = ft.Text("", size=12, visible=False, expand=1)
    formato_dropdown = ft.Dropdown(
        label="Formato",
        value=prefs.get("formato") if prefs.get("formato") in FORMATOS else "png",
        options=[ft.dropdown.Option(clave, texto) for clave, texto in FORMATOS.items()],
        expand=1,
    )
    tamano_dropdown = ft.Dropdown(
        label="Tamaño",
        value=prefs.get("tamano") if prefs.get("tamano") in TAMANOS else "original",
        options=[ft.dropdown.Option(clave, texto) for clave, texto in TAMANOS.items()],
        expand=1,
    )
    efecto_dropdown = ft.Dropdown(
        label="Sticker",
        value="ninguno",
        options=[ft.dropdown.Option(clave, texto) for clave, texto in EFECTOS.items()],
        expand=1,
    )
    contorno_color = ft.TextField(label="Color del contorno", value="#FFFFFF", expand=1, visible=False)
    brillo_slider = ft.Slider(min=50, max=150, value=100, divisions=20, label="{value}%")
    contraste_slider = ft.Slider(min=50, max=150, value=100, divisions=20, label="{value}%")
    saturacion_slider = ft.Slider(min=50, max=150, value=100, divisions=20, label="{value}%")
    nitidez_slider = ft.Slider(min=100, max=200, value=115, divisions=20, label="{value}%")
    recortar_sw = ft.Switch(label="Recortar al sujeto", value=True)
    omitir_sw = ft.Switch(label="Omitir archivos _sinfondo o ya exportados", value=True)
    compare_slider = ft.Slider(
        min=0, max=100, value=100, divisions=20, label="Resultado {value}%", disabled=True
    )

    def aviso(mensaje):
        snack_bar.content.value = mensaje
        snack_bar.open = True
        page.update()

    def get_opciones():
        return {
            "fondo": fondo_dropdown.value or "transparente",
            "color1": color1.value,
            "color2": color2.value,
            "fondo_imagen": estado["fondo_imagen"],
            "recortar": recortar_sw.value,
            "padding": 12,
            "formato": formato_dropdown.value or "png",
            "tamano": tamano_dropdown.value or "original",
            "brillo": (brillo_slider.value or 100) / 100.0,
            "contraste": (contraste_slider.value or 100) / 100.0,
            "saturacion": (saturacion_slider.value or 100) / 100.0,
            "nitidez": (nitidez_slider.value or 100) / 100.0,
            "efecto": efecto_dropdown.value or "ninguno",
            "contorno_color": contorno_color.value,
        }

    def opciones_de_proceso():
        if panel_postcorte.visible and estado["mascara_img"] is not None:
            return get_opciones()
        opciones = get_opciones()
        opciones.update(
            {
                "fondo": "transparente",
                "tamano": "original",
                "efecto": "ninguno",
                "formato": "png",
            }
        )
        return opciones

    def actualizar_campos_fondo(e=None):
        tipo = fondo_dropdown.value
        color1.visible = tipo in ("personalizado", "degradado")
        color2.visible = tipo == "degradado"
        btn_fondo_img.visible = tipo == "imagen"
        fondo_img_label.visible = tipo == "imagen"
        page.update()
        reaplicar_postproceso()

    def actualizar_efecto(e=None):
        contorno_color.visible = efecto_dropdown.value == "contorno"
        page.update()
        reaplicar_postproceso()

    def guardar_exportacion(e=None):
        recordar_exportacion(formato_dropdown.value, tamano_dropdown.value)
        reaplicar_postproceso()

    def reaplicar_postproceso(e=None):
        if estado["aplicando_post"] or estado["procesando"] or estado["mascara_img"] is None:
            return
        if fondo_dropdown.value == "imagen" and not estado["fondo_imagen"]:
            aviso("Elige la imagen de fondo o cambia el tipo de fondo.")
            return
        estado["aplicando_post"] = True
        try:
            recordar_exportacion(formato_dropdown.value, tamano_dropdown.value)
            final = postprocesar(estado["mascara_img"], get_opciones())
            guardar_resultado(final)
        finally:
            estado["aplicando_post"] = False

    fondo_dropdown.on_change = actualizar_campos_fondo
    efecto_dropdown.on_change = actualizar_efecto
    formato_dropdown.on_change = guardar_exportacion
    tamano_dropdown.on_change = guardar_exportacion
    recortar_sw.on_change = reaplicar_postproceso
    color1.on_blur = reaplicar_postproceso
    color1.on_submit = reaplicar_postproceso
    color2.on_blur = reaplicar_postproceso
    color2.on_submit = reaplicar_postproceso
    contorno_color.on_blur = reaplicar_postproceso
    contorno_color.on_submit = reaplicar_postproceso
    brillo_slider.on_change_end = reaplicar_postproceso
    contraste_slider.on_change_end = reaplicar_postproceso
    saturacion_slider.on_change_end = reaplicar_postproceso
    nitidez_slider.on_change_end = reaplicar_postproceso

    def hay_origen():
        return bool(estado["input"] or estado["carpeta"] or estado["archivos"])

    def carpeta_inicial():
        return estado["origen_dir"] or None

    def aplicar_rutas(rutas):
        if not rutas:
            return
        imagenes = [p for p in rutas if os.path.isfile(p) and p.lower().endswith(EXTENSIONES)]
        carpetas = [p for p in rutas if os.path.isdir(p)]
        estado["mascara_img"] = None
        estado["final_img"] = None
        estado["output_path"] = ""
        retocar_btn.disabled = True
        recorte_btn.disabled = True
        girar_btn.disabled = True
        voltear_h_btn.disabled = True
        voltear_v_btn.disabled = True
        copiar_btn.disabled = True
        compare_slider.disabled = True
        compare_slider.value = 100
        panel_postcorte.visible = False
        _mostrar_imagen(removed_bg_image_preview, ruta=DEFAULT_IMAGE_ABS)

        if carpetas:
            estado["carpeta"] = carpetas[0]
            estado["input"] = ""
            estado["archivos"] = []
            estado["origen_dir"] = carpetas[0]
            img_input.value = estado["carpeta"]
            _mostrar_imagen(original_image_preview, ruta=DEFAULT_IMAGE_ABS)
            recordar_carpetas(origen=carpetas[0])
            aviso(f"Carpeta lista: {estado['carpeta']}")
        elif len(imagenes) == 1:
            estado["input"] = imagenes[0]
            estado["carpeta"] = ""
            estado["archivos"] = []
            estado["origen_dir"] = os.path.dirname(imagenes[0])
            img_input.value = imagenes[0]
            estado["original_img"] = Image.open(imagenes[0]).convert("RGBA")
            _mostrar_imagen(original_image_preview, img=estado["original_img"])
            recordar_carpetas(origen=estado["origen_dir"])
            aviso("Imagen seleccionada. Elige destino y pulsa Procesar (Enter).")
        elif imagenes:
            estado["archivos"] = imagenes
            estado["input"] = ""
            estado["carpeta"] = ""
            estado["origen_dir"] = os.path.dirname(imagenes[0])
            img_input.value = f"{len(imagenes)} imágenes seleccionadas"
            estado["original_img"] = Image.open(imagenes[0]).convert("RGBA")
            _mostrar_imagen(original_image_preview, img=estado["original_img"])
            recordar_carpetas(origen=estado["origen_dir"])
            aviso(f"{len(imagenes)} imágenes listas. Elige destino y pulsa Procesar.")
        else:
            aviso("No se encontraron imágenes compatibles (png, jpg, jpeg, webp, ico).")
            return
        if estado["output_dir"]:
            procesar_imagenes_btn.disabled = False
        page.update()

    def on_file_chosen(e: ft.FilePickerResultEvent):
        if e.files:
            aplicar_rutas([f.path for f in e.files if f.path])

    def on_folder_chosen(e: ft.FilePickerResultEvent):
        if e.path:
            estado["output_dir"] = e.path
            recordar_carpetas(destino=e.path)
            procesar_imagenes_btn.disabled = not hay_origen()
            abrir_carpeta_btn.disabled = False
            aviso(f"Carpeta de destino: {estado['output_dir']}")

    def on_folder_with_images_chosen(e: ft.FilePickerResultEvent):
        if e.path:
            aplicar_rutas([e.path])

    def on_fondo_img_chosen(e: ft.FilePickerResultEvent):
        if e.files:
            estado["fondo_imagen"] = e.files[0].path
            fondo_img_label.value = os.path.basename(estado["fondo_imagen"])
            page.update()
            reaplicar_postproceso()

    def actualizar_compare(e=None):
        if estado["original_img"] is None or estado["final_img"] is None:
            return
        mezcla = mezclar_previews(
            estado["original_img"],
            estado["final_img"],
            (compare_slider.value or 0) / 100.0,
            PREVIEW_SIZE,
        )
        removed_bg_image_preview.src = None
        removed_bg_image_preview.src_base64 = img_a_b64(mezcla)
        page.update()

    compare_slider.on_change = actualizar_compare

    def alternar_compare(e=None):
        if estado["final_img"] is None:
            aviso("Procesa una imagen para comparar.")
            return
        compare_slider.value = 0 if (compare_slider.value or 0) >= 50 else 100
        actualizar_compare()

    def abrir_tamano_real(e=None):
        if estado["final_img"] is None:
            aviso("Procesa una imagen para verla a tamaño real.")
            return
        img = estado["final_img"]
        w, h = img.size
        escala = min(1.0, 900 / max(w, 1), 620 / max(h, 1))
        mostrar = img.resize((max(1, int(w * escala)), max(1, int(h * escala))), Image.Resampling.LANCZOS) if escala < 1 else img
        vista = encajar(mostrar, mostrar.size, con_damero=True)
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Vista previa a tamaño real ({w}×{h} px)"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Image(
                            src_base64=img_a_b64(vista),
                            width=vista.width,
                            height=vista.height,
                            fit=ft.ImageFit.NONE,
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=min(920, vista.width + 20),
                height=min(640, vista.height + 20),
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo))],
        )
        page.open(dialogo)

    def habilitar_edicion_resultado(activo=True):
        compare_slider.disabled = not activo
        retocar_btn.disabled = not activo or not estado["input"]
        recorte_btn.disabled = not activo
        girar_btn.disabled = not activo
        voltear_h_btn.disabled = not activo
        voltear_v_btn.disabled = not activo
        copiar_btn.disabled = not activo
        panel_postcorte.visible = bool(activo and estado["mascara_img"] is not None)

    def guardar_resultado(img):
        estado["final_img"] = img
        if estado["output_path"] or estado["output_dir"]:
            base = estado["output_path"] or os.path.join(
                estado["output_dir"], nombre_sin_fondo(os.path.basename(estado["input"] or "imagen"), get_opciones()["formato"])
            )
            estado["output_path"] = exportar(img, base, get_opciones())
        _mostrar_imagen(removed_bg_image_preview, img=img)
        page.update()

    def on_pincel_guardado(mascara, final, output_path):
        estado["mascara_img"] = mascara
        estado["final_img"] = final
        estado["output_path"] = output_path
        compare_slider.value = 100
        habilitar_edicion_resultado(True)
        _mostrar_imagen(removed_bg_image_preview, img=final)
        aviso(f"Retoque guardado en {output_path}")

    def abrir_retocar(e=None):
        if estado["mascara_img"] is None or not estado["input"]:
            aviso("El pincel está disponible después de procesar una sola imagen.")
            return
        if not estado["output_path"]:
            aviso("No hay un archivo de salida para guardar el retoque.")
            return
        abrir_editor_pincel(
            page,
            estado["input"],
            estado["mascara_img"],
            estado["output_path"],
            get_opciones,
            on_pincel_guardado,
        )

    def copiar_resultado(e=None):
        if estado["final_img"] is None:
            aviso("Procesa una imagen para copiarla al portapapeles.")
            return
        if copiar_imagen(estado["final_img"]):
            aviso("Imagen copiada al portapapeles (sin diálogo de guardar).")
        else:
            aviso("No se pudo copiar. En Linux hace falta xclip o wl-copy.")

    def girar_resultado(e=None):
        if estado["final_img"] is None:
            aviso("Procesa una imagen primero.")
            return
        guardar_resultado(estado["final_img"].transpose(Image.Transpose.ROTATE_90))
        aviso("Imagen girada 90°.")

    def voltear_h(e=None):
        if estado["final_img"] is None:
            aviso("Procesa una imagen primero.")
            return
        guardar_resultado(estado["final_img"].transpose(Image.Transpose.FLIP_LEFT_RIGHT))
        aviso("Imagen volteada horizontalmente.")

    def voltear_v(e=None):
        if estado["final_img"] is None:
            aviso("Procesa una imagen primero.")
            return
        guardar_resultado(estado["final_img"].transpose(Image.Transpose.FLIP_TOP_BOTTOM))
        aviso("Imagen volteada verticalmente.")

    def on_recorte_manual(img):
        guardar_resultado(img)
        aviso("Recorte aplicado.")

    def abrir_recorte(e=None):
        if estado["final_img"] is None:
            aviso("Procesa una imagen para recortarla a mano.")
            return
        abrir_editor_recorte(page, estado["final_img"], on_recorte_manual)

    def abrir_historial(e=None):
        items = cargar_prefs().get("historial") or []
        if not items:
            aviso("Todavía no hay archivos procesados.")
            return

        def abrir_item(carpeta):
            if carpeta and os.path.isdir(carpeta):
                abrir_carpeta_destino(carpeta)
            else:
                aviso("La carpeta ya no existe.")

        def cargar_item(entrada):
            page.close(dialogo)
            destino = entrada.get("destino") or ""
            origen = entrada.get("origen") or ""
            carpeta = entrada.get("carpeta_destino") or ""
            if carpeta and os.path.isdir(carpeta):
                estado["output_dir"] = carpeta
                recordar_carpetas(destino=carpeta)
                abrir_carpeta_btn.disabled = False
            if origen and os.path.exists(origen):
                aplicar_rutas([origen])
            if destino and os.path.isfile(destino):
                estado["output_path"] = destino
                estado["final_img"] = Image.open(destino).convert("RGBA")
                _mostrar_imagen(removed_bg_image_preview, img=estado["final_img"])
                habilitar_edicion_resultado(True)
                aviso(f"Reabierto: {os.path.basename(destino)}")
            page.update()

        filas = [
            ft.ListTile(
                title=ft.Text(item.get("nombre") or "archivo"),
                subtitle=ft.Text(f"{item.get('fecha', '')}  ·  {item.get('carpeta_destino', '')}"),
                trailing=ft.TextButton(
                    "Carpeta",
                    on_click=lambda e, c=item.get("carpeta_destino"): abrir_item(c),
                ),
                on_click=lambda e, actual=item: cargar_item(actual),
            )
            for item in items
        ]
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Historial reciente"),
            content=ft.Container(
                content=ft.Column(filas, scroll=ft.ScrollMode.AUTO, spacing=0),
                width=520,
                height=min(420, 56 * len(filas) + 20),
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo))],
        )
        page.open(dialogo)

    def set_procesando(activo, lote=False):
        estado["procesando"] = activo
        procesar_imagenes_btn.disabled = activo or not estado["output_dir"] or not hay_origen()
        cancelar_btn.visible = activo and lote
        cancelar_btn.disabled = not activo
        progress.visible = activo
        progress_text.visible = activo
        page.update()

    async def procesar_imagenes(e=None):
        if estado["procesando"]:
            return
        if not estado["output_dir"]:
            aviso("Selecciona una carpeta de destino antes de procesar.")
            return
        if not hay_origen():
            aviso("Selecciona una imagen, varias imágenes o una carpeta.")
            return
        if panel_postcorte.visible and fondo_dropdown.value == "imagen" and not estado["fondo_imagen"]:
            aviso("Elige la imagen de fondo o cambia el tipo de fondo.")
            return

        lote = bool(estado["carpeta"] or estado["archivos"])
        set_procesando(True, lote=lote)
        try:
            if estado["input"]:
                await procesar_imagen_individual()
            else:
                await procesar_lote()
        except Exception as error:
            aviso(f"Error al procesar: {error}")
        finally:
            set_procesando(False, lote=lote)
            cancelar_btn.visible = False
            page.update()

    async def procesar_imagen_individual():
        opciones = opciones_de_proceso()
        output_path = os.path.join(
            estado["output_dir"], nombre_sin_fondo(os.path.basename(estado["input"]), opciones["formato"])
        )
        progress.value = None
        progress_text.value = "Eliminando el fondo..."
        aviso("Procesando imagen...")
        page.update()
        mascara, final, output_path = await asyncio.to_thread(
            eliminar_fondo, estado["input"], output_path, opciones, MASCARA_PATH
        )
        estado["mascara_img"] = mascara
        estado["final_img"] = final
        estado["output_path"] = output_path
        estado["original_img"] = Image.open(estado["input"]).convert("RGBA")
        compare_slider.value = 100
        habilitar_edicion_resultado(True)
        progress.value = 1
        _mostrar_imagen(original_image_preview, img=estado["original_img"])
        _mostrar_imagen(removed_bg_image_preview, img=final)
        añadir_historial(estado["input"], output_path, estado["output_dir"])
        aviso(f"Recorte guardado en {output_path}. Ahora puedes cambiar fondo, formato y ajustes.")

    async def procesar_lote():
        estado["cancel"] = asyncio.Event()
        progress.value = 0
        progress_text.value = "Procesando lote..."
        page.update()
        resultado = await eliminar_fondo_carpeta(
            estado["carpeta"],
            estado["output_dir"],
            progress,
            page,
            cancel_event=estado["cancel"],
            omitir_existentes=omitir_sw.value,
            opciones=opciones_de_proceso(),
            archivos=estado["archivos"] or None,
        )
        habilitar_edicion_resultado(False)
        origen = estado["carpeta"] or (estado["archivos"][0] if estado["archivos"] else "")
        añadir_historial(origen, estado["output_dir"], estado["output_dir"])
        if resultado["cancelado"]:
            aviso(
                f"Lote cancelado. Procesadas {resultado['procesados']} de {resultado['total']} "
                f"(omitidas {resultado['omitidos']})."
            )
        else:
            aviso(
                f"Lote terminado. Procesadas {resultado['procesados']} de {resultado['total']} "
                f"(omitidas {resultado['omitidos']})."
            )

    def cancelar_lote(e=None):
        if estado["cancel"] is not None:
            estado["cancel"].set()
            cancelar_btn.disabled = True
            progress_text.value = "Cancelando al terminar la imagen actual..."
            page.update()

    def usar_imagen_buscada(ruta):
        dest = estado["output_dir"] or os.path.join(data_dir(BASE_DIR), "descargas")
        os.makedirs(dest, exist_ok=True)
        estado["output_dir"] = dest
        recordar_carpetas(destino=dest, origen=os.path.dirname(ruta))
        abrir_carpeta_btn.disabled = False
        aplicar_rutas([ruta])
        page.run_task(procesar_imagenes)

    menu.on_usar_imagen = usar_imagen_buscada

    file_picker = ft.FilePicker(on_result=on_file_chosen)
    folder_picker = ft.FilePicker(on_result=on_folder_with_images_chosen)
    folder_picker_output = ft.FilePicker(on_result=on_folder_chosen)
    fondo_img_picker = ft.FilePicker(on_result=on_fondo_img_chosen)
    page.overlay.extend([file_picker, folder_picker, folder_picker_output, fondo_img_picker])

    def cargar_imagen(e=None):
        file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["png", "jpg", "jpeg", "webp", "ico"],
            initial_directory=carpeta_inicial(),
        )

    def seleccionar_carpeta_imagenes(e=None):
        folder_picker.get_directory_path(initial_directory=carpeta_inicial())

    def seleccionar_carpeta_destino(e=None):
        folder_picker_output.get_directory_path(initial_directory=estado["output_dir"] or carpeta_inicial())

    def elegir_fondo_imagen(e=None):
        fondo_img_picker.pick_files(allowed_extensions=["png", "jpg", "jpeg", "webp"])

    def abrir_carpeta_destino_click(e=None):
        if estado["output_dir"]:
            abrir_carpeta_destino(estado["output_dir"])
        else:
            aviso("Primero selecciona una carpeta de destino.")

    def pegar_rutas(e=None):
        try:
            clip = page.get_clipboard()
        except Exception:
            clip = ""
        rutas = parsear_rutas(clip)
        if rutas:
            aplicar_rutas(rutas)
        else:
            aviso("El portapapeles no contiene rutas de archivos o carpetas.")

    def on_keyboard(e: ft.KeyboardEvent):
        if len(page.views) > 1:
            return
        clave = str(e.key)
        if (e.ctrl or e.meta) and clave.lower() == "o":
            cargar_imagen()
        elif (e.ctrl or e.meta) and clave.lower() == "v":
            pegar_rutas()
        elif clave in ("Enter", "Return", "Numpad Enter") and not estado["procesando"]:
            page.run_task(procesar_imagenes)
        elif clave in ("Escape", "Esc"):
            cancelar_lote()

    def on_file_drop(e):
        datos = getattr(e, "data", "") or ""
        rutas = parsear_rutas(str(datos))
        if rutas:
            aplicar_rutas(rutas)

    page.on_keyboard_event = on_keyboard
    try:
        page._add_event_handler("file_drop", on_file_drop)
        page._add_event_handler("on_file_drop", on_file_drop)
    except Exception:
        pass

    prev_window = page.window.on_event

    def on_window_event(e):
        if str(getattr(e, "data", "")).lower() in ("file_drop", "drop", "filesdropped"):
            on_file_drop(e)
        if prev_window:
            prev_window(e)

    page.window.on_event = on_window_event

    zona_soltar = ft.Container(
        content=ft.Column(
            [
                ft.Text("Arrastra imágenes o una carpeta aquí", weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Pulsa para elegir archivos (Ctrl+O), una carpeta o pega rutas con Ctrl+V. Enter procesa, Esc cancela el lote.",
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Row(
                    [
                        ft.TextButton("Elegir archivos", on_click=cargar_imagen),
                        ft.TextButton("Elegir carpeta", on_click=seleccionar_carpeta_imagenes),
                        ft.TextButton("Pegar rutas", on_click=pegar_rutas),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=15,
        border=ft.border.all(2, "#9C27B0"),
        border_radius=10,
        bgcolor="#2A1233",
        on_click=cargar_imagen,
        ink=True,
    )

    procesar_imagenes_btn = ft.ElevatedButton(
        "Procesar imágenes",
        on_click=procesar_imagenes,
        tooltip="Enter",
        disabled=True,
    )
    cancelar_btn = ft.ElevatedButton(
        "Cancelar lote",
        on_click=cancelar_lote,
        tooltip="Esc",
        visible=False,
        color="white",
        bgcolor="#8B0000",
    )
    abrir_carpeta_btn = ft.ElevatedButton(
        "Abrir carpeta destino",
        on_click=abrir_carpeta_destino_click,
        disabled=not estado["output_dir"],
    )
    historial_btn = ft.ElevatedButton("Historial reciente", on_click=abrir_historial)
    alternar_btn = ft.ElevatedButton("Alternar antes/después", on_click=alternar_compare)
    tamano_real_btn = ft.ElevatedButton("Tamaño real", on_click=abrir_tamano_real)
    copiar_btn = ft.ElevatedButton("Copiar", on_click=copiar_resultado, tooltip="Copia el recorte al portapapeles", disabled=True)
    girar_btn = ft.ElevatedButton("Girar 90°", on_click=girar_resultado, disabled=True)
    voltear_h_btn = ft.ElevatedButton("Voltear H", on_click=voltear_h, disabled=True)
    voltear_v_btn = ft.ElevatedButton("Voltear V", on_click=voltear_v, disabled=True)
    recorte_btn = ft.ElevatedButton("Recortar a mano", on_click=abrir_recorte, disabled=True)
    retocar_btn = ft.ElevatedButton(
        "Retocar bordes",
        on_click=abrir_retocar,
        tooltip="Pincel de acierto/error sobre el recorte",
        disabled=True,
    )
    btn_fondo_img = ft.ElevatedButton("Imagen de fondo", on_click=elegir_fondo_imagen, visible=False)

    panel_postcorte = ft.Column(
        [
            _tarjeta(
                "Fondo de salida",
                ft.Column(
                    [
                        ft.Text(
                            "Se aplica sobre el recorte. Cambia las opciones para actualizar el resultado sin volver a quitar el fondo.",
                            size=12,
                        ),
                        ft.Row(
                            [
                                fondo_dropdown,
                                color1,
                                color2,
                                btn_fondo_img,
                                fondo_img_label,
                            ],
                            spacing=16,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=10,
                ),
            ),
            _tarjeta(
                "Formato y tamaño",
                ft.Row(
                    [
                        formato_dropdown,
                        tamano_dropdown,
                        efecto_dropdown,
                        contorno_color,
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            _tarjeta(
                "Ajustes tras el recorte",
                ft.Row(
                    [
                        ft.Column([ft.Text("Brillo"), brillo_slider], expand=True),
                        ft.Column([ft.Text("Contraste"), contraste_slider], expand=True),
                        ft.Column([ft.Text("Saturación"), saturacion_slider], expand=True),
                        ft.Column([ft.Text("Nitidez"), nitidez_slider], expand=True),
                    ],
                    spacing=12,
                ),
                color_borde="#555555",
            ),
        ],
        visible=False,
        spacing=14,
    )

    if estado["output_dir"] and hay_origen():
        procesar_imagenes_btn.disabled = False

    create_ui(
        page,
        zona_soltar=zona_soltar,
        img_input=img_input,
        original_image_preview=original_image_preview,
        removed_bg_image_preview=removed_bg_image_preview,
        cargar_imagen=cargar_imagen,
        seleccionar_carpeta_imagenes=seleccionar_carpeta_imagenes,
        seleccionar_carpeta_destino=seleccionar_carpeta_destino,
        procesar_imagenes_btn=procesar_imagenes_btn,
        abrir_carpeta_btn=abrir_carpeta_btn,
        historial_btn=historial_btn,
        progress=progress,
        progress_text=progress_text,
        snack_bar=snack_bar,
        fondo_dropdown=fondo_dropdown,
        color1=color1,
        color2=color2,
        btn_fondo_img=btn_fondo_img,
        fondo_img_label=fondo_img_label,
        formato_dropdown=formato_dropdown,
        tamano_dropdown=tamano_dropdown,
        efecto_dropdown=efecto_dropdown,
        contorno_color=contorno_color,
        brillo_slider=brillo_slider,
        contraste_slider=contraste_slider,
        saturacion_slider=saturacion_slider,
        nitidez_slider=nitidez_slider,
        recortar_sw=recortar_sw,
        omitir_sw=omitir_sw,
        panel_postcorte=panel_postcorte,
        compare_slider=compare_slider,
        alternar_btn=alternar_btn,
        tamano_real_btn=tamano_real_btn,
        copiar_btn=copiar_btn,
        girar_btn=girar_btn,
        voltear_h_btn=voltear_h_btn,
        voltear_v_btn=voltear_v_btn,
        recorte_btn=recorte_btn,
        retocar_btn=retocar_btn,
        cancelar_btn=cancelar_btn,
    )
    page.update()


ft.app(target=main, view=ft.AppView.FLET_APP, assets_dir="assets")
