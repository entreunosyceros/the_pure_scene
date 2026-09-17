def reset_app(page, default_image_path, img_input, original_image_preview, removed_bg_image_preview, progress, progress_text):
    img_input.value = "No hay imagen seleccionada"
    original_image_preview.src = default_image_path
    original_image_preview.src_base64 = None
    removed_bg_image_preview.src = default_image_path
    removed_bg_image_preview.src_base64 = None
    progress.value = 0
    progress.visible = False
    progress_text.visible = False
    page.update()
