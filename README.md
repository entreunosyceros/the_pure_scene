## The Pure Scene

<p align="center">
<img width="1917" height="1046" alt="about_the_pure_scene" src="https://github.com/user-attachments/assets/56bd1bfc-fdde-47b0-894e-6155f7e52c96" />
</p>

**The Pure Scene** es una aplicación de escritorio creada con [Python](https://www.python.org/) y [Flet](https://flet.dev/) para quitar el fondo de imágenes con [rembg](https://github.com/danielgatis/rembg), exportarlas en varios formatos y tamaños, retocar bordes y buscar imágenes gratuitas.

## Documentación por categorías

<p align="center">
<img width="1917" height="1048" alt="interfaz_the_pure_scene" src="https://github.com/user-attachments/assets/7fb80eaf-00fa-47e3-a044-03c893afe19f" />
</p>


| Categoría | Contenido |
| --- | --- |
| [Instalación y arranque](docs/instalacion.md) | Entorno virtual, dependencias y primer inicio |
| [Quitar fondo](docs/quitar-fondo.md) | Cargar imágenes, destino y procesado |
| [Fondos de salida](docs/fondos-salida.md) | Tras el recorte: transparencia, color, chroma, degradado, patrón e imagen |
| [Formatos y tamaños](docs/formatos-tamanos.md) | Tras el recorte: PNG, JPEG, WebP, ICO y tamaños de redes |
| [Ajustes y stickers](docs/ajustes-stickers.md) | Tras el recorte: brillo, contraste, saturación, nitidez, contorno y sombra |
| [Edición del resultado](docs/edicion.md) | Comparar, copiar, girar, voltear, recortar y pincel |
| [Lotes e historial](docs/lotes-historial.md) | Cancelar lote, omitir `_sinfondo` y carpetas recordadas |
| [Buscador de imágenes](docs/buscador.md) | Sitios in-app, navegador y quitar fondo al descargar |
| [Añadir texto](docs/anadir-texto.md) | Superponer texto sobre una imagen |
| [Atajos e interfaz](docs/atajos-interfaz.md) | Menú, bandeja, Acerca de y atajos de teclado |

## Inicio rápido

```bash
python3 run_app.py
```

La primera vez crea el entorno virtual e instala las dependencias. Después, elige una imagen o carpeta, una carpeta de destino y pulsa **Procesar imágenes** (o Enter).

> [!NOTE]
> Al iniciar la aplicación por primera vez tardará un poco: se está creando el entorno virtual. Los siguientes arranques son más rápidos.

![fondo-eliminado](https://github.com/user-attachments/assets/26f6e6a3-a296-45ca-b7bd-59298b0c795b)

## Estructura del proyecto

<p align="center">

<img width="1919" height="1045" alt="como_funciona_the_pure_scene" src="https://github.com/user-attachments/assets/89ecf2a1-f27a-4b57-be5c-1876df416340" />

</p>


```
/Eliminar-fondos
├── main.py                 # Ventana principal y flujo de procesado
├── run_app.py              # Crea el venv, instala dependencias y lanza la app
├── menu.py                 # Menú: ayuda, buscador, texto, acerca de, salir
├── ui_layout.py            # Distribución de la ventana principal
├── page_config.py          # Título, tema y tamaño de ventana
├── eliminar_fondo.py       # rembg, lotes y omisión de archivos
├── postproceso.py          # Fondo, recorte, ajustes, formato y tamaño
├── editor_pincel.py        # Pincel de acierto/error
├── editor_recorte.py       # Recorte manual del resultado
├── add_texto.py            # Editor de texto sobre imagen
├── buscador.py             # Buscador de imágenes gratuitas
├── about.py                # Ventana Acerca de
├── preferencias.py         # Últimas carpetas e historial
├── portapapeles.py         # Copiar el recorte sin guardar
├── tray_icon.py            # Icono de bandeja y cierre
├── constants.py            # Rutas base
├── reset_app.py            # Reinicio de previsualizaciones
├── requirements.txt
├── assets/                 # Logo, icono de bandeja, imagen por defecto y fuentes
├── descargas/              # Imágenes bajadas desde el buscador (se crea al usar)
├── temp/                   # Preferencias y archivos temporales
└── docs/                   # Documentación por categorías
```

## Contribuciones

Las contribuciones son bienvenidas. Crea un fork del [repositorio](https://github.com/entreunosyceros/the_pure_scene) y envía un pull request con tus cambios.

## Licencia

Este proyecto está bajo [GPL-3.0](LICENSE).
