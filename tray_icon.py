import os
import platform
import signal
import subprocess
import sys
import threading
from PIL import Image
import pystray
from pystray import MenuItem as Item


def _pids_hijos(ppid):
    hijos = []
    try:
        entradas = os.listdir("/proc")
    except OSError:
        return hijos
    for nombre in entradas:
        if not nombre.isdigit():
            continue
        try:
            with open(os.path.join("/proc", nombre, "stat"), encoding="utf-8") as f:
                stat = f.read()
            resto = stat[stat.rfind(")") + 2:].split()
            if int(resto[1]) == ppid:
                hijos.append(int(nombre))
        except (OSError, ValueError, IndexError):
            continue
    return hijos


def _cmdline(pid):
    try:
        with open(os.path.join("/proc", str(pid), "cmdline"), "rb") as f:
            return f.read().replace(b"\x00", b" ").decode("utf-8", "replace").lower()
    except OSError:
        return ""


def _cerrar_cliente_flet_linux():
    """Mata el proceso de la ventana Flutter. destroy() dispara FlutterEngineRemoveView en Linux."""
    hijos = _pids_hijos(os.getpid())
    objetivo = [pid for pid in hijos if "flet" in _cmdline(pid)] or hijos
    for pid in objetivo:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def cerrar_aplicacion(page=None):
    if sys.platform.startswith("linux"):
        _cerrar_cliente_flet_linux()
        os._exit(0)
    if page is not None:
        try:
            page.window.prevent_close = False
            page.window.destroy()
            return
        except Exception:
            pass
    os._exit(0)

# Función para abrir la carpeta de destino
def abrir_carpeta_destino(carpeta):
    try:
        if platform.system() == "Windows":
            subprocess.run(["explorer", carpeta])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", carpeta])
        else:
            print("Sistema operativo no soportado")
    except Exception as e:
        print(f"Error al abrir la carpeta: {e}")

def create_tray_icon(page, base_dir):
    def quit_action(icon, item):
        cerrar_aplicacion(page)

    image = Image.open(os.path.join(base_dir, "assets/tray-icon.png"))
    icon = pystray.Icon("The Pure Scene", image, menu=pystray.Menu(
        Item('Mostrar ventana', lambda: None),
        Item('Salir', quit_action)
    ))

    def run_tray():
        icon.run()

    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()
