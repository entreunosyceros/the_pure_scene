# Quitar fondo

Esta es la función principal: cargar una o varias imágenes, elegir destino y generar un archivo sin fondo (u con el [fondo de salida](fondos-salida.md) que hayas elegido).

Formatos de entrada admitidos: **PNG, JPEG, WebP e ICO**.

## Cómo cargar imágenes

En la zona superior de la ventana puedes:

- Pulsar para elegir uno o varios archivos (**Ctrl+O**).
- Elegir una carpeta completa.
- Pegar rutas de archivos o carpetas con **Ctrl+V** (por ejemplo, copiadas desde el explorador).

La previsualización **Original** muestra la imagen cargada (o la primera del lote).

## Carpeta de destino

Antes de procesar hay que indicar dónde se guardarán los resultados:

1. Pulsa **Carpeta destino**.
2. Elige una carpeta.
3. **Abrir carpeta destino** la abre en el explorador del sistema.

El programa [recuerda la última carpeta de origen y de destino](lotes-historial.md).

## Procesar

Pulsa **Procesar imágenes** o **Enter**.

- Una sola imagen: se muestra el resultado, se puede [comparar, copiar y editar](edicion.md).
- Varias imágenes o una carpeta: se procesan en lote, con barra de progreso. Ver [Lotes e historial](lotes-historial.md).

El archivo se nombra igual que el original, con el sufijo `_sinfondo` y la extensión del [formato de exportación](formatos-tamanos.md). El primer recorte se guarda en PNG transparente; al cambiar formato, el nombre se actualiza. Ejemplo: `foto.jpg` → `foto_sinfondo.png`.

## Recortar al sujeto

La opción **Recortar al sujeto** (activada por defecto) recorta el PNG al contorno de la persona u objeto, con un pequeño margen, para no dejar mucho vacío alrededor.

## Orden del procesado

1. rembg separa el sujeto del fondo.
2. Recorte al sujeto (si está activado).
3. Se muestran las tarjetas de [fondo](fondos-salida.md), [formato y tamaño](formatos-tamanos.md) y [ajustes](ajustes-stickers.md).
4. Cada cambio se aplica sobre el recorte, sin volver a quitar el fondo.

## Siguiente categoría

- [Fondos de salida](fondos-salida.md)
- [Lotes e historial](lotes-historial.md)
