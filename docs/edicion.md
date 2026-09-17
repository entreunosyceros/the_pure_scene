# Edición del resultado

Después de procesar **una sola imagen**, la columna **Resultado / comparación** permite revisar y retocar sin volver a pasar rembg (salvo el pincel, que trabaja sobre la máscara original).

En un lote, fondo, formato y ajustes se aplican si ya recortaste una imagen (las tarjetas están visibles). Si el lote es lo primero que procesas, se guarda el recorte en PNG transparente.

## Comparar y vista previa

| Control | Función |
| --- | --- |
| Deslizador | 0 % muestra el original, 100 % el resultado |
| Alternar antes/después | Cambia de golpe entre original y recorte |
| Tamaño real | Abre el resultado a 1:1 (con damero si hay transparencia) |

## Copiar al portapapeles

**Copiar** envía el recorte actual al portapapeles, sin diálogo de guardar.

En Linux hace falta `xclip` (X11) o `wl-copy` (Wayland):

```bash
sudo apt install xclip
```

## Girar, voltear y recortar a mano

| Botón | Acción |
| --- | --- |
| Girar 90° | Rota el resultado 90° en sentido antihorario |
| Voltear H | Espejo horizontal |
| Voltear V | Espejo vertical |
| Recortar a mano | Pantalla completa: arrastra un rectángulo y pulsa **Aplicar recorte** |

Los cambios se escriben sobre el archivo de destino ya exportado.

## Pincel de acierto / error

**Retocar bordes** abre un editor a pantalla completa. rembg a veces falla en pelo y bordes finos.

| Modo | Uso |
| --- | --- |
| Acierto: recuperar | Pinta para devolver píxeles del original (pelo, huecos) |
| Error: borrar fondo | Pinta para hacer transparentes restos de fondo |

También puedes cambiar el tamaño del pincel, **acercar o alejar** (botones +, −, deslizador o rueda del ratón), **mover la vista** con zoom activo, deshacer el último trazo y **Guardar y volver**. Al guardar se vuelven a aplicar recorte, fondo, ajustes y formato actuales.

## Siguiente categoría

- [Lotes e historial](lotes-historial.md)
