#!/usr/bin/env bash
# Genera the-pure-scene_VERSION_amd64.deb
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${VERSION:-1.0.2}"
ARCH="${ARCH:-amd64}"
PKG_NAME="the-pure-scene"
OUT_DIR="${ROOT}/dist"
STAGE="${OUT_DIR}/deb-stage"
PKG_ROOT="${STAGE}/${PKG_NAME}_${VERSION}_${ARCH}"
OPT_DIR="${PKG_ROOT}/opt/${PKG_NAME}"
BIN_DIR="${PKG_ROOT}/usr/bin"
APP_DIR="${PKG_ROOT}/usr/share/applications"
ICON_DIR="${PKG_ROOT}/usr/share/icons/hicolor/256x256/apps"
DOC_DIR="${PKG_ROOT}/usr/share/doc/${PKG_NAME}"
DEBIAN_DIR="${PKG_ROOT}/DEBIAN"

echo "==> Empaquetando ${PKG_NAME} ${VERSION} (${ARCH})"

rm -rf "${STAGE}"
mkdir -p "${OPT_DIR}" "${BIN_DIR}" "${APP_DIR}" "${ICON_DIR}" "${DOC_DIR}" "${DEBIAN_DIR}" "${OUT_DIR}"

PY_FILES=(
  main.py about.py add_texto.py buscador.py constants.py editor_pincel.py
  editor_recorte.py eliminar_fondo.py menu.py page_config.py portapapeles.py
  postproceso.py preferencias.py reset_app.py tray_icon.py ui_layout.py
  run_app.py _runtime_paths.py requirements.txt
)
for f in "${PY_FILES[@]}"; do
  cp "${ROOT}/${f}" "${OPT_DIR}/"
done
cp -a "${ROOT}/assets" "${OPT_DIR}/"
mkdir -p "${OPT_DIR}/temp" "${OPT_DIR}/descargas"
[[ -d "${ROOT}/docs" ]] && cp -a "${ROOT}/docs" "${OPT_DIR}/"
[[ -f "${ROOT}/LICENSE" ]] && cp "${ROOT}/LICENSE" "${DOC_DIR}/copyright"
[[ -f "${ROOT}/README.md" ]] && cp "${ROOT}/README.md" "${DOC_DIR}/"

if [[ -f "${ROOT}/assets/tray-icon.png" ]]; then
  cp "${ROOT}/assets/tray-icon.png" "${ICON_DIR}/${PKG_NAME}.png"
elif [[ -f "${ROOT}/assets/logo.jpeg" ]] && command -v convert >/dev/null; then
  convert "${ROOT}/assets/logo.jpeg" -resize 256x256 "${ICON_DIR}/${PKG_NAME}.png"
fi

cat > "${BIN_DIR}/${PKG_NAME}" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_ROOT="/opt/the-pure-scene"
export TPS_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/the-pure-scene"
mkdir -p "$TPS_HOME/temp" "$TPS_HOME/descargas"
VENV="$TPS_HOME/venv"
PYTHON="$VENV/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  echo "The Pure Scene: preparando entorno (primera ejecución)..."
  python3 -m venv "$VENV"
  "$PYTHON" -m pip install --upgrade pip
  "$PYTHON" -m pip install -r "$APP_ROOT/requirements.txt"
fi

# Preferir siempre la ventana de escritorio (Flet/Flutter).
# Solo abre el navegador si el usuario lo pide explícitamente: TPS_VIEW=web
export GDK_BACKEND="${GDK_BACKEND:-x11}"

# Si el driver NVIDIA del kernel no coincide con las librerías, OpenGL falla
# y la ventana de escritorio no puede iniciarse. Avisar con claridad.
if [[ "${TPS_VIEW:-}" != "web" && "${TPS_VIEW:-}" != "browser" ]]; then
  if [[ -r /proc/driver/nvidia/version ]]; then
    kernel_ver="$(awk '/NVRM version/ {print $8}' /proc/driver/nvidia/version 2>/dev/null || true)"
    user_ver=""
    if command -v nvidia-smi >/dev/null 2>&1; then
      user_ver="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 || true)"
    fi
    if [[ -z "$user_ver" ]] && nvidia-smi 2>&1 | grep -qi 'version mismatch'; then
      echo "================================================================="
      echo "The Pure Scene necesita OpenGL para la ventana de escritorio."
      echo "Hay un desajuste del driver NVIDIA (kernel vs librerías)."
      echo "Reinicia el equipo y vuelve a ejecutar: the-pure-scene"
      echo "================================================================="
      echo "Kernel NVRM: ${kernel_ver:-desconocido}"
      exit 1
    fi
    if [[ -n "$kernel_ver" && -n "$user_ver" && "$kernel_ver" != "$user_ver" ]]; then
      echo "================================================================="
      echo "The Pure Scene: desajuste NVIDIA detectado."
      echo "  Módulo del kernel: $kernel_ver"
      echo "  Librerías/usuario: $user_ver"
      echo "Reinicia el equipo para cargar el driver correcto."
      echo "================================================================="
      exit 1
    fi
  fi
  if command -v glxinfo >/dev/null 2>&1 && ! glxinfo -B >/dev/null 2>&1; then
    echo "================================================================="
    echo "The Pure Scene: OpenGL/GLX no funciona en este equipo."
    echo "La app de escritorio (Flet/Flutter) lo necesita."
    echo "Si usas NVIDIA, reinicia tras actualizar el driver."
    echo "Comprueba con: glxinfo -B"
    echo "================================================================="
    exit 1
  fi
fi

if [[ "${TPS_SOFTWARE_GL:-}" == "1" ]]; then
  export LIBGL_ALWAYS_SOFTWARE=1
  export __GLX_VENDOR_LIBRARY_NAME="${__GLX_VENDOR_LIBRARY_NAME:-mesa}"
  export GALLIUM_DRIVER="${GALLIUM_DRIVER:-llvmpipe}"
fi

cd "$APP_ROOT"
export TPS_DATA_DIR="$TPS_HOME"
exec "$PYTHON" "$APP_ROOT/main.py" "$@"
EOF
chmod 755 "${BIN_DIR}/${PKG_NAME}"

cat > "${APP_DIR}/${PKG_NAME}.desktop" << EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=The Pure Scene
GenericName=Quitar fondo de imágenes
Comment=Elimina el fondo de imágenes con rembg
Exec=${PKG_NAME}
Icon=${PKG_NAME}
Terminal=false
Categories=Graphics;Photography;Utility;
StartupNotify=true
Keywords=background;remove;image;png;
EOF

INSTALLED_SIZE="$(du -sk "${PKG_ROOT}" | awk '{print $1}')"
cat > "${DEBIAN_DIR}/control" << EOF
Package: ${PKG_NAME}
Version: ${VERSION}
Section: graphics
Priority: optional
Architecture: ${ARCH}
Installed-Size: ${INSTALLED_SIZE}
Depends: python3 (>= 3.10), python3-venv, python3-pip, libgtk-3-0 | libgtk-3-0t64, libgl1, libegl1, libepoxy0
Recommends: mesa-utils, libgl1-mesa-dri
Maintainer: entreunosyceros <https://github.com/entreunosyceros>
Homepage: https://github.com/entreunosyceros/the_pure_scene
Description: The Pure Scene - quitar fondo de imágenes
 The Pure Scene es una aplicación de escritorio creada con Python y Flet
 para eliminar el fondo de imágenes (rembg), exportar en varios formatos
 y retocar el resultado.
 Si OpenGL/GLX no funciona (p. ej. desajuste del driver NVIDIA),
 reinicia el equipo; la app usa ventana de escritorio, no el navegador.
EOF

cat > "${DEBIAN_DIR}/postinst" << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
fi
echo "The Pure Scene instalado. Ejecuta: the-pure-scene"
echo "La primera ejecución descargará dependencias de Python (puede tardar)."
echo "Si falla OpenGL con NVIDIA, reinicia tras actualizar el driver."
EOF
chmod 755 "${DEBIAN_DIR}/postinst"

cat > "${DEBIAN_DIR}/postrm" << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q || true
fi
EOF
chmod 755 "${DEBIAN_DIR}/postrm"

find "${PKG_ROOT}" -type d -exec chmod 755 {} \;
find "${PKG_ROOT}" -type f -exec chmod 644 {} \;
chmod 755 "${BIN_DIR}/${PKG_NAME}" "${DEBIAN_DIR}/postinst" "${DEBIAN_DIR}/postrm"

DEB_FILE="${OUT_DIR}/${PKG_NAME}_${VERSION}_${ARCH}.deb"
fakeroot dpkg-deb --build "${PKG_ROOT}" "${DEB_FILE}"
echo
echo "Listo: ${DEB_FILE}"
ls -lh "${DEB_FILE}"
dpkg-deb -I "${DEB_FILE}" | sed -n '1,30p'
