import hashlib
import json
import os
import re
import shutil
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

import flet as ft

from constants import BASE_DIR

FUENTES = {
    "Wikimedia Commons": {"tipo": "wikimedia", "etiqueta": "Wikimedia Commons"},
    "Flickr": {"tipo": "flickr", "etiqueta": "Flickr"},
    "Stocksnap": {"tipo": "stocksnap", "etiqueta": "Stocksnap"},
    "NASA": {"tipo": "nasa", "etiqueta": "NASA"},
    "Rawpixel": {"tipo": "web", "url": "https://www.rawpixel.com/search/", "etiqueta": "Rawpixel (navegador)"},
    "Unsplash": {"tipo": "web", "url": "https://unsplash.com/s/photos/", "etiqueta": "Unsplash (navegador)"},
    "Pexels": {"tipo": "web", "url": "https://www.pexels.com/search/", "etiqueta": "Pexels (navegador)"},
    "Pixabay": {"tipo": "web", "url": "https://pixabay.com/images/search/", "etiqueta": "Pixabay (navegador)"},
    "Freepik": {
        "tipo": "web",
        "url": "https://www.freepik.es/search?format=search&last_filter=query&query=",
        "etiqueta": "Freepik (navegador)",
    },
    "Morguefile": {"tipo": "web", "url": "https://morguefile.com/search?term=", "etiqueta": "Morguefile (navegador)"},
    "iStock": {
        "tipo": "web",
        "url": "https://www.istockphoto.com/es/search/2/image?phrase=",
        "etiqueta": "iStock (navegador)",
    },
    "Life of Pix": {"tipo": "web", "url": "https://www.lifeofpix.com/search/", "etiqueta": "Life of Pix (navegador)"},
    "Gratisography": {"tipo": "web", "url": "https://gratisography.com/?s=", "etiqueta": "Gratisography (navegador)"},
    "Shutterstock": {
        "tipo": "web",
        "url": "https://www.shutterstock.com/es/search/",
        "etiqueta": "Shutterstock (navegador)",
    },
    "Picjumbo": {"tipo": "web", "url": "https://picjumbo.com/search/", "etiqueta": "Picjumbo (navegador)"},
    "Kaboompics": {
        "tipo": "web",
        "url": "https://kaboompics.com/gallery?search=",
        "etiqueta": "Kaboompics (navegador)",
    },
}

WIKIMEDIA_URL = "https://commons.wikimedia.org/w/api.php"
NASA_URL = "https://images-api.nasa.gov/search"
FLICKR_FEED_URL = "https://www.flickr.com/services/feeds/photos_public.gne"
USER_AGENT = "ThePureScene/1.0 (https://github.com/entreunosyceros/the_pure_scene)"
CACHE_DIR = os.path.join(tempfile.gettempdir(), "the-pure-scene-buscador")


def _get_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


def _texto_plano(valor):
    if not valor:
        return ""
    return re.sub(r"<[^>]+>", "", str(valor)).strip()


def _cache_path(url):
    os.makedirs(CACHE_DIR, exist_ok=True)
    nombre = urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else "jpg"
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        ext = "jpg"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{digest}.{ext}")


def _descargar(url):
    if not url:
        return None
    destino = _cache_path(url)
    if os.path.isfile(destino) and os.path.getsize(destino) > 100:
        return destino
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as origen:
        datos = origen.read()
    if len(datos) < 100:
        return None
    with open(destino, "wb") as salida:
        salida.write(datos)
    return destino


def _con_preview(item):
    remoto = item.get("thumbnail") or item.get("url")
    try:
        local = _descargar(remoto)
    except Exception:
        local = None
        try:
            local = _descargar(item.get("url"))
        except Exception:
            local = None
    if not local:
        return None
    item["preview"] = local
    return item


def _buscar_wikimedia(termino, limite=24):
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": termino,
            "gsrnamespace": "6",
            "gsrlimit": str(limite),
            "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata",
            "iiurlwidth": "320",
            "format": "json",
        }
    )
    datos = _get_json(f"{WIKIMEDIA_URL}?{params}")
    items = []
    for pagina in ((datos.get("query") or {}).get("pages") or {}).values():
        info = (pagina.get("imageinfo") or [{}])[0]
        mime = info.get("mime") or ""
        if not mime.startswith("image/"):
            continue
        meta = info.get("extmetadata") or {}
        items.append(
            {
                "title": (pagina.get("title") or "").replace("File:", "", 1),
                "thumbnail": info.get("thumburl"),
                "url": info.get("url"),
                "foreign_landing_url": info.get("descriptionurl"),
                "creator": _texto_plano((meta.get("Artist") or {}).get("value")),
                "license": _texto_plano((meta.get("LicenseShortName") or {}).get("value")),
                "filetype": mime.split("/", 1)[-1],
                "source": "Wikimedia Commons",
            }
        )
    return items


def _buscar_nasa(termino, limite=24):
    params = urllib.parse.urlencode(
        {"q": termino, "media_type": "image", "page_size": str(limite)}
    )
    datos = _get_json(f"{NASA_URL}?{params}")
    items = []
    for fila in ((datos.get("collection") or {}).get("items") or [])[:limite]:
        info = (fila.get("data") or [{}])[0]
        enlaces = fila.get("links") or []
        thumb = next((l.get("href") for l in enlaces if l.get("rel") == "preview"), None)
        grande = next((l.get("href") for l in enlaces if l.get("rel") == "canonical"), None)
        if not grande:
            grande = next((l.get("href") for l in enlaces if l.get("rel") == "alternate"), thumb)
        if not (thumb or grande):
            continue
        nasa_id = info.get("nasa_id") or ""
        items.append(
            {
                "title": info.get("title") or nasa_id or "NASA",
                "thumbnail": thumb or grande,
                "url": grande or thumb,
                "foreign_landing_url": f"https://images.nasa.gov/details-{nasa_id}" if nasa_id else "",
                "creator": info.get("photographer") or info.get("secondary_creator") or "NASA",
                "license": "NASA (dominio público)",
                "filetype": "jpg",
                "source": "NASA",
            }
        )
    return items


def _buscar_flickr(termino, limite=24):
    tags = ",".join(parte for parte in re.split(r"\s+", termino) if parte)
    params = urllib.parse.urlencode(
        {"tags": tags, "tagmode": "all", "format": "json", "nojsoncallback": "1"}
    )
    datos = _get_json(f"{FLICKR_FEED_URL}?{params}")
    items = []
    for fila in (datos.get("items") or [])[:limite]:
        media = (fila.get("media") or {}).get("m") or ""
        if not media:
            continue
        grande = re.sub(r"_m\.(jpg|jpeg|png)$", r"_b.\1", media, flags=re.I)
        autor = fila.get("author") or ""
        match = re.search(r'\("(.*)"\)', autor)
        items.append(
            {
                "title": fila.get("title") or "Flickr",
                "thumbnail": media,
                "url": grande,
                "foreign_landing_url": fila.get("link") or "",
                "creator": match.group(1) if match else autor,
                "license": "",
                "filetype": "jpg",
                "source": "Flickr",
            }
        )
    return items


def _buscar_stocksnap(termino, limite=24):
    slug = urllib.parse.quote(termino.strip().replace(" ", "-"))
    url = f"https://stocksnap.io/search/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as respuesta:
        html = respuesta.read().decode("utf-8", "replace")
    ids = list(dict.fromkeys(re.findall(
        r"https://cdn\.stocksnap\.io/img-thumbs/280h/([A-Za-z0-9_-]+)\.jpg",
        html,
    )))
    items = []
    for identificador in ids[:limite]:
        if "_" not in identificador:
            continue
        nombre, codigo = identificador.rsplit("_", 1)
        items.append(
            {
                "title": nombre.replace("-", " ").title(),
                "thumbnail": f"https://cdn.stocksnap.io/img-thumbs/280h/{identificador}.jpg",
                "url": f"https://cdn.stocksnap.io/img-thumbs/960w/{identificador}.jpg",
                "foreign_landing_url": f"https://stocksnap.io/photo/{nombre}-{codigo}",
                "creator": "",
                "license": "CC0",
                "filetype": "jpg",
                "source": "Stocksnap",
            }
        )
    return items


def buscar_imagenes(termino, clave_fuente):
    fuente = FUENTES[clave_fuente]
    tipo = fuente["tipo"]
    if tipo == "wikimedia":
        lote = _buscar_wikimedia(termino)
    elif tipo == "nasa":
        lote = _buscar_nasa(termino)
    elif tipo == "flickr":
        lote = _buscar_flickr(termino)
    elif tipo == "stocksnap":
        lote = _buscar_stocksnap(termino)
    else:
        return []

    resultados = []
    for item in lote:
        preparado = _con_preview(item)
        if preparado:
            resultados.append(preparado)
    return resultados


def _nombre_archivo(item):
    titulo = re.sub(r"[^\w\-]+", "_", (item.get("title") or "imagen").strip())[:40] or "imagen"
    ext = (item.get("filetype") or "jpg").lstrip(".")
    return f"{titulo}.{ext}"


def _guardar_en_proyecto(item):
    url = item.get("url") or item.get("preview")
    local = _descargar(url)
    if not local:
        raise RuntimeError("archivo vacío")
    carpeta = os.path.join(BASE_DIR, "descargas")
    os.makedirs(carpeta, exist_ok=True)
    nombre = _nombre_archivo(item)
    destino = os.path.join(carpeta, nombre)
    base, ext = os.path.splitext(destino)
    indice = 1
    while os.path.exists(destino):
        destino = f"{base}_{indice}{ext}"
        indice += 1
    shutil.copyfile(local, destino)
    return destino


def crear_buscador(page, on_usar_imagen=None):
    query = ft.TextField(label="Buscar imágenes", expand=1, on_submit=lambda e: lanzar_busqueda())
    sitio = ft.Dropdown(
        label="Sitio",
        value="Wikimedia Commons",
        options=[
            ft.dropdown.Option(key=clave, text=datos["etiqueta"])
            for clave, datos in FUENTES.items()
        ],
        width=260,
    )
    estado = ft.Text(
        "Elige un sitio. Los marcados como (navegador) no permiten mostrar el listado aquí."
    )
    progreso = ft.ProgressBar(visible=False, color="purple")
    descarga_pendiente = {"url": None}

    galeria = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=160,
        child_aspect_ratio=1,
        spacing=8,
        run_spacing=8,
        height=360,
    )

    def on_guardar(e: ft.FilePickerResultEvent):
        destino = e.path
        url = descarga_pendiente["url"]
        if not destino or not url:
            return
        try:
            local = _descargar(url)
            if not local:
                raise RuntimeError("archivo vacío")
            with open(local, "rb") as origen, open(destino, "wb") as salida:
                salida.write(origen.read())
            estado.value = f"Imagen guardada en {destino}"
        except Exception as err:
            estado.value = f"No se pudo guardar la imagen: {err}"
        page.update()

    save_picker = ft.FilePicker(on_result=on_guardar)
    if save_picker not in page.overlay:
        page.overlay.append(save_picker)

    def mostrar_detalle(item):
        img_src = item.get("preview") or item.get("url")
        titulo = item.get("title") or "Sin título"
        creditos = " · ".join(p for p in (item.get("creator"), item.get("license"), item.get("source")) if p)

        def descargar(_e=None):
            descarga_pendiente["url"] = item.get("url") or item.get("preview")
            save_picker.save_file(file_name=_nombre_archivo(item))

        def usar_y_quitar(_e=None):
            try:
                destino = _guardar_en_proyecto(item)
            except Exception as err:
                estado.value = f"No se pudo descargar al proyecto: {err}"
                page.update()
                return
            page.close(detalle)
            page.close(buscador_dialog)
            if on_usar_imagen:
                on_usar_imagen(destino)

        def abrir_origen(_e=None):
            webbrowser.open(item.get("foreign_landing_url") or item.get("url") or "")

        detalle = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, max_lines=2),
            content=ft.Column(
                [
                    ft.Image(src=img_src, width=480, height=300, fit=ft.ImageFit.CONTAIN),
                    ft.Text(creditos, size=12),
                ],
                tight=True,
                width=500,
            ),
            actions=[
                ft.TextButton("Descargar", on_click=descargar),
                ft.TextButton("Quitar fondo", on_click=usar_y_quitar),
                ft.TextButton("Ver original", on_click=abrir_origen),
                ft.TextButton("Cerrar", on_click=lambda e: page.close(detalle)),
            ],
        )
        page.open(detalle)

    def pintar_resultados(items, nombre_sitio):
        galeria.controls.clear()
        for item in items:
            galeria.controls.append(
                ft.Container(
                    content=ft.Image(src=item["preview"], fit=ft.ImageFit.COVER, width=150, height=150),
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    tooltip=item.get("title") or "",
                    on_click=lambda e, actual=item: mostrar_detalle(actual),
                )
            )
        if items:
            estado.value = f"{len(items)} imágenes de {nombre_sitio}"
        else:
            estado.value = f"No se encontraron imágenes en {nombre_sitio}."

    def lanzar_busqueda(e=None):
        termino = (query.value or "").strip()
        clave = sitio.value
        if not termino:
            estado.value = "Escribe un término de búsqueda."
            page.update()
            return
        if not clave or clave not in FUENTES:
            estado.value = "Selecciona un sitio."
            page.update()
            return

        fuente = FUENTES[clave]
        galeria.controls.clear()

        if fuente["tipo"] == "web":
            webbrowser.open(fuente["url"] + urllib.parse.quote(termino))
            estado.value = (
                f"{clave} no permite mostrar su listado dentro de la aplicación "
                "(exige cuenta o API). Se abrió en el navegador."
            )
            page.update()
            return

        progreso.visible = True
        estado.value = f"Buscando en {clave}..."
        page.update()

        def trabajo():
            try:
                items = buscar_imagenes(termino, clave)
                pintar_resultados(items, clave)
            except urllib.error.HTTPError as err:
                estado.value = f"No se pudo consultar {clave} ({err.code})."
            except Exception as err:
                estado.value = f"Error al buscar en {clave}: {err}"
            finally:
                progreso.visible = False
                page.update()

        threading.Thread(target=trabajo, daemon=True).start()

    buscador_content = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        query,
                        sitio,
                        ft.ElevatedButton("Buscar", on_click=lanzar_busqueda),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                progreso,
                estado,
                galeria,
            ],
            spacing=12,
            width=740,
            height=520,
        ),
        padding=10,
        width=760,
        height=540,
    )

    buscador_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Buscador de Imágenes Gratuitas"),
        content=buscador_content,
        actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(buscador_dialog))],
        inset_padding=ft.Padding(20, 20, 20, 20),
    )

    page.open(buscador_dialog)
    page.update()
