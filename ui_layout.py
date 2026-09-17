import flet as ft


def _tarjeta(titulo, cuerpo, color_borde="#9C27B0"):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(titulo, weight=ft.FontWeight.BOLD, size=16),
                cuerpo,
            ],
            spacing=12,
        ),
        padding=16,
        border=ft.border.all(1, color_borde),
        border_radius=10,
        bgcolor="#24102C",
    )


def create_ui(page, **w):
    page.scroll = ft.ScrollMode.AUTO
    page.add(
        ft.Column(
            [
                w["zona_soltar"],
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Original", weight=ft.FontWeight.BOLD),
                                    w["original_image_preview"],
                                    ft.Row([w["img_input"]], expand=True),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "Cargar imagen(es)",
                                                on_click=w["cargar_imagen"],
                                                tooltip="Ctrl+O",
                                            ),
                                            ft.ElevatedButton(
                                                "Procesar carpeta",
                                                on_click=w["seleccionar_carpeta_imagenes"],
                                            ),
                                        ],
                                        wrap=True,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            padding=10,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Resultado / comparación", weight=ft.FontWeight.BOLD),
                                    w["removed_bg_image_preview"],
                                    w["compare_slider"],
                                    ft.Row(
                                        [
                                            w["alternar_btn"],
                                            w["tamano_real_btn"],
                                            w["copiar_btn"],
                                        ],
                                        wrap=True,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    ft.Row(
                                        [
                                            w["girar_btn"],
                                            w["voltear_h_btn"],
                                            w["voltear_v_btn"],
                                            w["recorte_btn"],
                                            w["retocar_btn"],
                                        ],
                                        wrap=True,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "Carpeta destino",
                                                on_click=w["seleccionar_carpeta_destino"],
                                            ),
                                            w["abrir_carpeta_btn"],
                                            w["historial_btn"],
                                        ],
                                        wrap=True,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            padding=10,
                            expand=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=28, color="#9C27B0", thickness=1),
                _tarjeta(
                    "Opciones de procesado",
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    w["recortar_sw"],
                                    w["omitir_sw"],
                                ],
                                spacing=24,
                                wrap=True,
                            ),
                            ft.Row(
                                [
                                    w["procesar_imagenes_btn"],
                                    w["cancelar_btn"],
                                ],
                                spacing=16,
                                wrap=True,
                            ),
                            ft.Column(
                                [w["progress_text"], w["progress"]],
                                spacing=6,
                            ),
                        ],
                        spacing=12,
                    ),
                    color_borde="#555555",
                ),
                w["panel_postcorte"],
                w["snack_bar"],
            ],
            spacing=14,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )
