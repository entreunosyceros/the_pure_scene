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
dist/the-pure-scene_1.0.0_amd64.deb
```

Instalación:

```bash
sudo apt install ./dist/the-pure-scene_1.0.0_amd64.deb
# o
sudo dpkg -i dist/the-pure-scene_1.0.0_amd64.deb
```

Después ejecuta `the-pure-scene` o ábrelo desde el menú de aplicaciones.

La **primera ejecución** crea un entorno virtual en `~/.local/share/the-pure-scene/` e instala las dependencias de Python (hace falta red; puede tardar por rembg/onnxruntime).

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
