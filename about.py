import os
import flet as ft
import webbrowser
from constants import BASE_DIR

def abrir_ventana_acerca_de(page):
    about_image = ft.Image(
        src=os.path.join(BASE_DIR, "assets", "logo.jpeg"),
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN
    )
    
    # Descripción breve del programa
    descripcion = ft.Text(
        "The Pure Scene permite eliminar el fondo de imágenes de manera rápida y eficiente.",
        size=16,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.CENTER
    )
    
    # Enlace al repositorio de GitHub usando webbrowser
    enlace_github = ft.TextButton(
        text="Repositorio en GitHub",
        on_click=lambda e: webbrowser.open("https://github.com/entreunosyceros/the_pure_scene"),
        style=ft.ButtonStyle(color=ft.Colors.BLUE)
    )

    # Contenedor de la ventana "Acerca de"
    ventana_acerca_de = ft.AlertDialog(
        modal=True,
        title=ft.Text("Acerca de The Pure Scene", color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
        content=ft.Container(
            content=ft.Column(
                [
                    about_image,
                    descripcion,
                    enlace_github
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=ft.padding.all(20),
            width=300,
            height=400,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: page.close(ventana_acerca_de))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.BLACK,
        inset_padding=ft.Padding(20, 20, 20, 20),
    )

    # Añadir la ventana al overlay de la página y abrirla
    page.overlay.append(ventana_acerca_de)
    ventana_acerca_de.open = True
    page.update()
