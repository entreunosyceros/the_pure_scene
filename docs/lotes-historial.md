# Lotes e historial

## Procesar una carpeta o varias imágenes

1. **Procesar carpeta** o selecciona varios archivos.
2. Elige la [carpeta de destino](quitar-fondo.md).
3. Pulsa **Procesar imágenes** (Enter). El lote recorta a PNG transparente, salvo que ya hayas recortado una imagen y tengas visibles [fondo](fondos-salida.md), [formato](formatos-tamanos.md) y [ajustes](ajustes-stickers.md).

Durante el lote aparece la barra de progreso. **Cancelar lote** (o **Esc**) detiene el trabajo al terminar la imagen en curso; las ya guardadas no se borran.

## Omitir archivos `_sinfondo`

La opción **Omitir archivos _sinfondo o ya exportados** (activada por defecto):

- No vuelve a procesar archivos cuyo nombre ya termina en `_sinfondo`.
- No sobrescribe un destino que ya existe con el mismo nombre de salida.

Así puedes dejar mezcladas fotos originales y recortes en la misma carpeta.

## Carpetas recordadas

En `temp/preferencias.json` se guardan:

- la última carpeta de origen
- la última carpeta de destino
- el último formato y tamaño de exportación

Al reabrir el programa, los selectores de archivo parten de esas carpetas.

## Historial reciente

**Historial reciente** lista los últimos procesados (hasta 12):

- Un clic en la fila carga de nuevo origen y resultado, si los archivos siguen ahí.
- **Carpeta** abre la carpeta de destino en el explorador.

## Siguiente categoría

- [Buscador de imágenes](buscador.md)
- [Atajos e interfaz](atajos-interfaz.md)
