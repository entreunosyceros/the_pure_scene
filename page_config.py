import flet as ft

def configure_page(page):
    page.title = "The Pure Scene"
    page.theme_mode = "dark"
    page.window.width = 1100
    page.window.height = 860
    page.window.min_width = 980
    page.window.min_height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 16
