from screeninfo import get_monitors
import platform
import theme

def get_scaled_font(root, base_size):
    monitor_width, monitor_height = get_active_monitor_geometry(root)
    scale_factor_width = monitor_width / 1920
    scale_factor_height = monitor_height / 1080
    scale_factor = min(scale_factor_width, scale_factor_height)

    scaled_size = int(base_size * scale_factor)
    return max(20, min(scaled_size, base_size * 2.0))

def get_active_monitor_geometry(root):
    root.update_idletasks()
    window_x = root.winfo_x()
    window_y = root.winfo_y()

    for monitor in get_monitors():
        if (monitor.x <= window_x < monitor.x + monitor.width and
                monitor.y <= window_y < monitor.y + monitor.height):
            return monitor.width, monitor.height

    return root.winfo_screenwidth(), root.winfo_screenheight()

def toggle_fullscreen(root, fullscreen: bool):
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)

    if not fullscreen:
        if platform.system() == "Windows":
            root.state("zoomed")
        else:
            root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

def toggle_backlight(backlight_on: bool):
    try:
        if backlight_on:
            print("Backlight currently on")
            with open("/sys/class/graphics/fb0/blank", "w") as f:
                f.write("1")
            return False
        else:
            print("Backlight currently off")
            with open("/sys/class/graphics/fb0/blank", "w") as f:
                f.write("0")
            return True
    except Exception as e:
        print(f"Fehler beim Steuern des Backlights: {e}")
        return backlight_on

def resize_fonts(root, block_label, *detail_labels):
    theme.update_fonts(root)
    block_label.config(font=theme.blockheight_font)

    for label in detail_labels:
        label.config(font=theme.detail_font)

def is_exit_click(root, event):
    screen_height = root.winfo_screenheight()
    click_y = event.y
    return click_y >= screen_height * 0.8
