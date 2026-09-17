import io
import os
import platform
import shutil
import subprocess
import tempfile


def copiar_imagen(img):
    buf = io.BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    datos = buf.getvalue()
    sistema = platform.system()
    if sistema == "Linux":
        if shutil.which("wl-copy") and os.environ.get("WAYLAND_DISPLAY"):
            r = subprocess.run(["wl-copy", "-t", "image/png"], input=datos, check=False)
            if r.returncode == 0:
                return True
        if shutil.which("xclip"):
            r = subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", "image/png"],
                input=datos,
                check=False,
            )
            if r.returncode == 0:
                return True
        if shutil.which("xsel"):
            r = subprocess.run(["xsel", "--clipboard", "--input"], input=datos, check=False)
            if r.returncode == 0:
                return True
    elif sistema == "Darwin":
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(datos)
            ruta = tmp.name
        try:
            r = subprocess.run(
                ["osascript", "-e", f'set the clipboard to (read (POSIX file "{ruta}") as «class PNGf»)'],
                check=False,
            )
            return r.returncode == 0
        finally:
            os.unlink(ruta)
    elif sistema == "Windows":
        try:
            import win32clipboard
            from PIL import Image

            salida = io.BytesIO()
            Image.open(io.BytesIO(datos)).convert("RGB").save(salida, "BMP")
            bmp = salida.getvalue()[14:]
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp)
            win32clipboard.CloseClipboard()
            return True
        except Exception:
            return False
    return False
