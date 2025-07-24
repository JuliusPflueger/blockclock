import platform

def toggle_fullscreen(root, fullscreen):
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)
    if not fullscreen:
        if platform.system() == "Windows":
            root.state("zoomed")
        else:
            root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    return fullscreen

def toggle_backlight(current_state):
    try:
        with open("/sys/class/graphics/fb0/blank", "w") as f:
            f.write("0" if not current_state else "1")
        return not current_state
    except Exception as e:
        print(f"Fehler beim Steuern des Backlights: {e}")
        return current_state
