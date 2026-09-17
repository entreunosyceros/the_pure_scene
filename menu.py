import flet as ft
from buscador import crear_buscador  # Importar la función para abrir el buscador
from add_texto import abrir_ventana_texto_imagen  # Importar la función para añadir texto
from about import abrir_ventana_acerca_de  # Importar la función para la ventana "Acerca de"
from tray_icon import cerrar_aplicacion

class Menu:
    def __init__(self, page, on_usar_imagen=None):
        self.page = page
        self.on_usar_imagen = on_usar_imagen
        self._close_dialog = None
        self.create_menu()
        self.setup_close_confirmation()  # Manejar el cierre de la ventana principal

    def create_menu(self):
        # Crear un botón de menú en la app bar
        menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text="Cómo funciona", on_click=self.open_help_window),
                ft.PopupMenuItem(text="Buscador de Imágenes", on_click=self.open_image_search),
                ft.PopupMenuItem(text="Añadir Texto a Imagen", on_click=self.open_add_text_window),
                ft.PopupMenuItem(text="Acerca de", on_click=self.open_about_window),  
                ft.PopupMenuItem(text="Cerrar aplicación", on_click=self.confirm_exit),
            ]
        )
        
        # Asignar el appbar con el menú
        self.page.appbar = ft.AppBar(
            title=ft.Text("The Pure Scene"),
            center_title=True,
            bgcolor="purple",
            actions=[menu]
        )

    def open_image_search(self, e):
        # Llamar a la función para abrir la ventana de búsqueda
        crear_buscador(self.page, on_usar_imagen=self.on_usar_imagen)

    def open_add_text_window(self, e):
        # Llama a la función para abrir la ventana de añadir texto
        abrir_ventana_texto_imagen(self.page)

    def open_about_window(self, e):
        # Llama a la función para abrir la ventana "Acerca de"
        abrir_ventana_acerca_de(self.page)

    def confirm_exit(self, e=None):
        if self._close_dialog is None:
            self._close_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("¿Estás seguro de que quieres salir?"),
                content=ft.Text("Cualquier progreso no guardado se perderá."),
                actions=[
                    ft.TextButton("Sí", on_click=lambda e: cerrar_aplicacion(self.page)),
                    ft.TextButton("No", on_click=lambda e: self.page.close(self._close_dialog)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.overlay.append(self._close_dialog)
        self._close_dialog.open = True
        self.page.update()

    def open_help_window(self, e):
        # Crear un AlertDialog para explicar el funcionamiento con tamaño controlado
        help_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cómo funciona el programa", color=ft.Colors.WHITE),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "The Pure Scene elimina el fondo de imágenes.",
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.RED
                        ),
                        ft.Text("0. Selecciona la opción buscar imágenes gratuitas en el menú, y descárgalas a tu equipo.",
                                color=ft.Colors.WHITE),
                        ft.Text("1. Arrastra, pega (Ctrl+V) o pulsa la zona superior para elegir imágenes o una carpeta.",
                                color=ft.Colors.WHITE),
                        ft.Text("2. Selecciona destino y pulsa Procesar (Enter). El recorte sale con transparencia.",
                                color=ft.Colors.WHITE),
                        ft.Text("3. Después aparecen fondo, formato y ajustes. En un lote puedes cancelar u omitir *_sinfondo.",
                                color=ft.Colors.WHITE),
                        ft.Text("4. Compara, copia, gira o recorta el resultado. Atajos: Ctrl+O abrir, Enter procesar, Esc cancelar lote.",
                                color=ft.Colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                padding=ft.padding.all(10),  # Padding interno
                width=400,  # Ancho fijo para el diálogo
                height=320,
                alignment=ft.alignment.center  # Centrar contenido dentro del contenedor
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.page.close(help_dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.BLACK,
            inset_padding=ft.Padding(20, 20, 20, 20),  # Padding externo ajustado
        )
        self.page.overlay.append(help_dialog)
        help_dialog.open = True  # Abrir el diálogo de ayuda
        self.page.update()

    def setup_close_confirmation(self):
        # Manejar el evento de cierre de la ventana (cuando se pulsa la X)
        def handle_window_event(e):
            if e.data == "close":
                self.confirm_exit()  # Abrir el diálogo de confirmación de salida

        self.page.window.prevent_close = True  # Evitar el cierre directo de la ventana
        self.page.window.on_event = handle_window_event  # Asignar el evento de cierre
