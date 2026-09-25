# Instaladores

Puedes generar paquetes de instalación para Linux (`.deb`) y Windows (`.exe`).

## Linux (.deb)

En Ubuntu/Debian (o cualquier sistema con `dpkg-deb` y `fakeroot`):

```bash
chmod +x packaging/build_deb.sh
./packaging/build_deb.sh
```

El paquete queda en:

```text
dist/the-pure-scene_1.0.2_amd64.deb
```

Instalación:

```bash
sudo apt install ./dist/the-pure-scene_1.0.2_amd64.deb
# o
sudo dpkg -i dist/the-pure-scene_1.0.2_amd64.deb
```

Después ejecuta `the-pure-scene` o ábrelo desde el menú de aplicaciones.

La **primera ejecución** crea un entorno virtual en `~/.local/share/the-pure-scene/` e instala las dependencias de Python (hace falta red; puede tardar por rembg/onnxruntime).

### OpenGL / errores Gdk-CRITICAL

Flet de escritorio usa Flutter + GTK y **necesita OpenGL**. The Pure Scene **no se abre en el navegador** salvo que lo pidas tú.

Si al arrancar ves `Failed to initialize GLArea` o spam de `fl_keyboard_manager`, suele ser un **desajuste del driver NVIDIA** (módulo del kernel distinto de las librerías). Comprueba:

```bash
cat /proc/driver/nvidia/version
nvidia-smi
glxinfo -B
```

Si `nvidia-smi` dice `Driver/library version mismatch`, **reinicia el equipo** y vuelve a lanzar `the-pure-scene`. Tras el reinicio, el módulo y las librerías coinciden y la ventana de escritorio debería funcionar.

Solo si quieres forzar el navegador a propósito:

```bash
TPS_VIEW=web the-pure-scene
```

Desinstalación:

```bash
sudo apt remove the-pure-scene
```

Variable de versión opcional:

```bash
VERSION=1.0.1 ./packaging/build_deb.sh
```

## Windows (.exe)

El `.exe` debe construirse en **Windows** (PyInstaller no cruza bien desde Linux). Opciones:

### Opción A — GitHub Actions (recomendada)

1. Sube el código a [the_pure_scene](https://github.com/entreunosyceros/the_pure_scene).
2. En **Actions** → **Build installers** → **Run workflow**.
3. Descarga el artefacto `the-pure-scene-exe`.

También se dispara al crear una etiqueta `v1.0.0`.

### Opción B — En un PC con Windows

En PowerShell, desde la carpeta del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
```

Salida esperada:

```text
dist\ThePureScene-1.0.0-windows-x64.exe
```

## Notas

- El `.deb` no incluye el modelo de rembg: se descarga en la primera ejecución.
- El `.exe` de Windows incluye las librerías empaquetadas y suele ser un archivo grande.
- `dist/` está en `.gitignore` y no se sube al repositorio.
