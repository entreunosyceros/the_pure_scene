# Fondos de salida

Por defecto el recorte es transparente. La tarjeta **Fondo de salida** aparece **después** de procesar una imagen. Al cambiar la opción, el resultado se actualiza al momento, sin volver a pasar rembg.

## Tipos disponibles

| Opción | Resultado |
| --- | --- |
| Transparente | Mantiene el canal alfa (recomendado para PNG y WebP) |
| Blanco | Fondo blanco opaco |
| Negro | Fondo negro opaco |
| Chroma verde | Verde puro `#00FF00`, útil para vídeo |
| Chroma azul | Azul puro `#0000FF` |
| Color personalizado | Un color hexadecimal (campo **Color 1**) |
| Degradado | De **Color 1** a **Color 2**, de arriba abajo |
| Patrón damero | Cuadrícula clara, para ver recortes o maquetas |
| Otra imagen | Elige un archivo que se redimensiona al tamaño del sujeto |

Si eliges **JPEG**, no hay transparencia: si el fondo sigue en *Transparente*, se aplana a blanco al guardar. Para JPEG con color, chroma o degradado, elige esa opción con el recorte ya visible.

En un lote, estas opciones se usan si ya recortaste una imagen antes (la tarjeta está visible). Si no, el lote se guarda como PNG transparente.

## Siguiente categoría

- [Formatos y tamaños](formatos-tamanos.md)
