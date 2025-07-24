import view_utils

def setup_key_bindings(app):
    root = app.root
    root.bind("<Button-1>", lambda event: handle_exit_click(app, event))
    root.bind("<F11>", lambda event: toggle_fullscreen(app))
    root.bind("<Escape>", lambda event: exit_program(app))

def handle_exit_click(app, event):
    if view_utils.is_exit_click(app.root, event):
        exit_program(app)

def toggle_fullscreen(app):
    app.fullscreen = view_utils.toggle_fullscreen(app.root, app.fullscreen)

def exit_program(app):
    app.root.destroy()

def schedule_resize(app):
    if app.resize_id is not None:
        app.root.after_cancel(app.resize_id)
    app.resize_id = app.root.after(
        150,
        lambda: view_utils.resize_fonts(app.root, app.label_block_height, *app.detail_labels)
    )
