import os
import subprocess
import sys

# Obtener el directorio donde se encuentra el archivo run_app.py
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# Nombre del entorno virtual
VENV_DIR = os.path.join(DIRECTORIO_SCRIPT, "venv")

# Determinar el ejecutable de Python dentro del entorno virtual
def obtener_python_ejecutable():
    if os.name == 'nt':  # Windows
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:  # Linux/macOS
        return os.path.join(VENV_DIR, "bin", "python")

# Comprobar si el entorno virtual está creado
def entorno_virtual_existe():
    return os.path.isdir(VENV_DIR)

# Crear el entorno virtual
def crear_entorno_virtual():
    print("Creando el entorno virtual...")
    # Preferir venv (incluido en Python). virtualenv es un paquete extra
    # que no siempre está instalado.
    for modulo in ("venv", "virtualenv"):
        resultado = subprocess.run(
            [sys.executable, "-m", modulo, VENV_DIR],
            capture_output=True,
            text=True,
        )
        if resultado.returncode == 0:
            return
        print(f"No se pudo crear el entorno con {modulo}.")
        if resultado.stderr:
            print(resultado.stderr.strip())

    print(
        "No se pudo crear el entorno virtual. "
        "Instala el módulo venv de Python o el paquete virtualenv e inténtalo de nuevo."
    )
    sys.exit(1)

# Instalar pip si no está instalado
def asegurar_pip(python_executable):
    try:
        subprocess.run([python_executable, "-m", "pip", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("pip no está instalado. Intentando instalar pip manualmente...")
        subprocess.run([python_executable, "-m", "ensurepip", "--upgrade"], check=True)

# Instalar las dependencias desde requirements.txt
def instalar_dependencias(python_executable):
    print("Instalando dependencias...")
    asegurar_pip(python_executable)
    
    ruta_requirements = os.path.join(DIRECTORIO_SCRIPT, "requirements.txt")
    
    if os.path.exists(ruta_requirements):
        subprocess.run([python_executable, "-m", "pip", "install", "-r", ruta_requirements], check=True)
    else:
        print("No se encontró el archivo requirements.txt.")

# Ejecutar el script principal dentro del entorno virtual
def ejecutar_app():
    python_executable = obtener_python_ejecutable()
    ruta_main = os.path.join(DIRECTORIO_SCRIPT, "main.py")

    if os.path.isfile(python_executable):
        # Por defecto ventana de escritorio. Solo web si TPS_VIEW=web.
        env = os.environ.copy()
        env.setdefault("GDK_BACKEND", "x11")
        subprocess.run([python_executable, ruta_main], check=True, env=env)
    else:
        print(f"El ejecutable no se encuentra: {python_executable}")

# Lógica principal
def main():
    python_executable = obtener_python_ejecutable()

    if not entorno_virtual_existe():
        # Si no existe el entorno virtual, crearlo e instalar dependencias
        print("El entorno virtual no existe. Creando uno nuevo...")
        crear_entorno_virtual()
        instalar_dependencias(python_executable)
    else:
        # Si el entorno virtual ya existe
        print("El entorno virtual ya existe.")
        instalar_dependencias(python_executable)

    # Ejecutar la aplicación
    ejecutar_app()

# Ejecutar el script
if __name__ == "__main__":
    main()
