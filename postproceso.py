import base64
import io
import os
from urllib.parse import unquote, urlparse

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

EXTENSIONES = (".png", ".jpg", ".jpeg", ".webp", ".ico")

FORMATOS = {
    "png": "PNG (transparencia)",
    "jpeg": "JPEG (con fondo)",
    "webp": "WebP",
    "ico": "ICO",
}

TAMANOS = {
    "original": "Tamaño original",
    "avatar_512": "Avatar 512×512",
    "miniatura_256": "Miniatura 256×256",
    "instagram": "Instagram 1080×1080",
    "story": "Story 1080×1920",
    "facebook": "Facebook 1200×630",
}

TAMANOS_PX = {
    "avatar_512": (512, 512),
    "miniatura_256": (256, 256),
    "instagram": (1080, 1080),
    "story": (1080, 1920),
    "facebook": (1200, 630),
}

EFECTOS = {
    "ninguno": "Sin efecto",
    "contorno": "Contorno (sticker)",
    "sombra": "Sombra",
}

FONDOS = {
    "transparente": "Transparente",
    "blanco": "Blanco",
    "negro": "Negro",
    "chroma_verde": "Chroma verde",
    "chroma_azul": "Chroma azul",
    "personalizado": "Color personalizado",
    "degradado": "Degradado",
    "damero": "Patrón damero",
    "imagen": "Otra imagen",
}

COLORES_SOLIDOS = {
    "blanco": (255, 255, 255, 255),
    "negro": (0, 0, 0, 255),
    "chroma_verde": (0, 255, 0, 255),
    "chroma_azul": (0, 0, 255, 255),
}


def parse_hex(valor, por_defecto=(255, 255, 255, 255)):
    texto = (valor or "").strip().lstrip("#")
    if len(texto) == 3:
        texto = "".join(c * 2 for c in texto)
    if len(texto) != 6:
        return por_defecto
    try:
        r = int(texto[0:2], 16)
        g = int(texto[2:4], 16)
        b = int(texto[4:6], 16)
        return (r, g, b, 255)
    except ValueError:
        return por_defecto


def recortar_sujeto(img, padding=12):
    img = img.convert("RGBA")
    bbox = img.getchannel("A").getbbox()
    if not bbox:
        return img
    izq, arriba, der, abajo = bbox
    izq = max(0, izq - padding)
    arriba = max(0, arriba - padding)
    der = min(img.width, der + padding)
    abajo = min(img.height, abajo + padding)
    return img.crop((izq, arriba, der, abajo))


def _degradado(size, color1, color2, vertical=True):
    ancho, alto = size
    if vertical:
        t = np.linspace(0, 1, alto, dtype=np.float32)[:, None]
        shape = (alto, ancho, 4)
        t = np.broadcast_to(t, (alto, ancho))
    else:
        t = np.linspace(0, 1, ancho, dtype=np.float32)[None, :]
        shape = (alto, ancho, 4)
        t = np.broadcast_to(t, (alto, ancho))
    arr = np.empty(shape, dtype=np.uint8)
    c1 = np.array(color1, dtype=np.float32)
    c2 = np.array(color2, dtype=np.float32)
    for i in range(4):
        arr[:, :, i] = (c1[i] * (1 - t) + c2[i] * t).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def _fondo_imagen(size, ruta):
    fondo = Image.open(ruta).convert("RGBA")
    return fondo.resize(size, Image.Resampling.LANCZOS)


def aplicar_fondo(img, opciones):
    img = img.convert("RGBA")
    tipo = opciones.get("fondo", "transparente")
    if tipo == "transparente":
        return img

    if tipo == "degradado":
        c1 = parse_hex(opciones.get("color1"), (40, 40, 80, 255))
        c2 = parse_hex(opciones.get("color2"), (180, 80, 180, 255))
        base = _degradado(img.size, c1, c2, vertical=True)
    elif tipo == "damero":
        base = damero(img.size, casilla=max(8, img.width // 40))
    elif tipo == "imagen":
        ruta = opciones.get("fondo_imagen")
        if ruta and os.path.isfile(ruta):
            base = _fondo_imagen(img.size, ruta)
        else:
            base = Image.new("RGBA", img.size, (255, 255, 255, 255))
    elif tipo == "personalizado":
        base = Image.new("RGBA", img.size, parse_hex(opciones.get("color1")))
    else:
        color = COLORES_SOLIDOS.get(tipo, (255, 255, 255, 255))
        base = Image.new("RGBA", img.size, color)
    return Image.alpha_composite(base, img)


def ajustar_tonos(img, opciones):
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    rgb = img.convert("RGB")
    brillo = float(opciones.get("brillo", 1.0))
    contraste = float(opciones.get("contraste", 1.0))
    saturacion = float(opciones.get("saturacion", 1.0))
    nitidez = float(opciones.get("nitidez", 1.0))
    if abs(brillo - 1.0) > 0.01:
        rgb = ImageEnhance.Brightness(rgb).enhance(brillo)
    if abs(contraste - 1.0) > 0.01:
        rgb = ImageEnhance.Contrast(rgb).enhance(contraste)
    if abs(saturacion - 1.0) > 0.01:
        rgb = ImageEnhance.Color(rgb).enhance(saturacion)
    if abs(nitidez - 1.0) > 0.01:
        rgb = ImageEnhance.Sharpness(rgb).enhance(nitidez)
    salida = rgb.convert("RGBA")
    salida.putalpha(alpha)
    return salida


def aplicar_contorno(img, grosor=6, color=(255, 255, 255, 255)):
    img = img.convert("RGBA")
    grosor = max(1, int(grosor))
    pad = grosor + 2
    lienzo = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    lienzo.paste(img, (pad, pad), img)
    alpha = lienzo.getchannel("A")
    nucleo = grosor * 2 + 1
    if nucleo % 2 == 0:
        nucleo += 1
    nucleo = min(nucleo, max(3, (min(lienzo.size) // 2) * 2 + 1))
    if min(lienzo.size) < 3:
        return lienzo
    borde = alpha.filter(ImageFilter.MaxFilter(nucleo))
    capa = Image.new("RGBA", lienzo.size, color)
    capa.putalpha(borde)
    return Image.alpha_composite(capa, lienzo)


def aplicar_sombra(img, desplazamiento=10, desenfoque=12, opacidad=160):
    img = img.convert("RGBA")
    extra = desplazamiento + desenfoque * 2
    lienzo = Image.new(
        "RGBA",
        (img.width + extra + desplazamiento, img.height + extra + desplazamiento),
        (0, 0, 0, 0),
    )
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    alpha = img.getchannel("A").point(lambda a: int(a * opacidad / 255))
    sombra.putalpha(alpha)
    sombra = sombra.filter(ImageFilter.GaussianBlur(desenfoque))
    origen = (desplazamiento + desenfoque, desplazamiento + desenfoque)
    lienzo.paste(sombra, origen, sombra)
    sujeto = (desenfoque, desenfoque)
    lienzo.paste(img, sujeto, img)
    return lienzo


def aplicar_efecto(img, opciones):
    efecto = opciones.get("efecto", "ninguno")
    if efecto == "contorno":
        return aplicar_contorno(img, grosor=6, color=parse_hex(opciones.get("contorno_color"), (255, 255, 255, 255)))
    if efecto == "sombra":
        return aplicar_sombra(img)
    return img


def redimensionar(img, opciones):
    clave = opciones.get("tamano", "original")
    caja = TAMANOS_PX.get(clave)
    if not caja:
        return img
    img = img.convert("RGBA")
    copia = img.copy()
    copia.thumbnail(caja, Image.Resampling.LANCZOS)
    lienzo = Image.new("RGBA", caja, (0, 0, 0, 0))
    x = (caja[0] - copia.width) // 2
    y = (caja[1] - copia.height) // 2
    lienzo.alpha_composite(copia, (x, y))
    return lienzo


def extension_formato(formato):
    formato = (formato or "png").lower()
    return {"jpeg": "jpg", "jpg": "jpg", "webp": "webp", "ico": "ico"}.get(formato, "png")


def ruta_con_formato(ruta, formato):
    base, _ext = os.path.splitext(ruta)
    return f"{base}.{extension_formato(formato)}"


def _aplanar_si_hace_falta(img, opciones, formato):
    formato = (formato or "png").lower()
    img = img.convert("RGBA")
    if formato in ("jpeg", "jpg") and opciones.get("fondo", "transparente") == "transparente":
        return aplicar_fondo(img, {**opciones, "fondo": "blanco"}).convert("RGB")
    if formato in ("jpeg", "jpg"):
        return img.convert("RGB")
    return img


def exportar(img, ruta, opciones=None):
    opciones = opciones or {}
    formato = (opciones.get("formato") or "png").lower()
    if formato == "jpg":
        formato = "jpeg"
    ruta = ruta_con_formato(ruta, formato)
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    img = _aplanar_si_hace_falta(img, opciones, formato)
    if formato == "jpeg":
        img.save(ruta, "JPEG", quality=92)
    elif formato == "webp":
        img.save(ruta, "WEBP", quality=90)
    elif formato == "ico":
        ico = img.convert("RGBA")
        ico.thumbnail((256, 256), Image.Resampling.LANCZOS)
        lienzo = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        lienzo.alpha_composite(ico, ((256 - ico.width) // 2, (256 - ico.height) // 2))
        lienzo.save(ruta, "ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    else:
        img.convert("RGBA").save(ruta, "PNG")
    return ruta


def postprocesar(img, opciones):
    img = img.convert("RGBA")
    if opciones.get("recortar", False):
        img = recortar_sujeto(img, padding=int(opciones.get("padding", 12)))
    img = ajustar_tonos(img, opciones)
    img = aplicar_efecto(img, opciones)
    img = aplicar_fondo(img, opciones)
    return redimensionar(img, opciones)


def damero(size, casilla=12):
    ancho, alto = size
    img = Image.new("RGBA", size, (200, 200, 200, 255))
    draw = ImageDraw.Draw(img)
    for y in range(0, alto, casilla):
        for x in range(0, ancho, casilla):
            if ((x // casilla) + (y // casilla)) % 2 == 0:
                draw.rectangle((x, y, x + casilla - 1, y + casilla - 1), fill=(240, 240, 240, 255))
    return img


def encajar(img, caja, con_damero=True):
    img = img.convert("RGBA")
    copia = img.copy()
    copia.thumbnail(caja, Image.Resampling.LANCZOS)
    lienzo = damero(caja) if con_damero else Image.new("RGBA", caja, (0, 0, 0, 0))
    x = (caja[0] - copia.width) // 2
    y = (caja[1] - copia.height) // 2
    lienzo.alpha_composite(copia, (x, y))
    return lienzo


def mezclar_previews(original, resultado, t, caja=(280, 280)):
    a = encajar(original, caja)
    b = encajar(resultado, caja)
    t = min(1.0, max(0.0, float(t)))
    return Image.blend(a, b, t)


def ya_tiene_sinfondo(nombre):
    base, _ext = os.path.splitext(nombre)
    return base.endswith("_sinfondo")


def img_a_b64(img):
    buf = io.BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def parsear_rutas(texto):
    if not texto:
        return []
    rutas = []
    bruto = texto.replace("\r", "\n").replace("file://", "\nfile://")
    for linea in bruto.split("\n"):
        linea = linea.strip().strip('"').strip("'")
        if not linea or linea in ("copy", "cut", "x-special/gnome-copied-files"):
            continue
        if linea.startswith("file:"):
            parsed = urlparse(linea)
            linea = unquote(parsed.path)
        if os.path.exists(linea):
            rutas.append(linea)
    return rutas
