import tkinter as tk
import datetime
import math
import controls.controls_service as controls_service
from data.data_updater import DataUpdater
from PIL import Image, ImageTk
import logging
from screeninfo import get_monitors
from settings import SettingsFrame

import theme

LOGO_BASE_SIZE = 48
LOGO_REFERENCE_SHORT_SIDE = 1080
LOGO_MAX_SIZE = 160
LOGO_TARGET_MM = 18
LOGO_SMALL_SCREEN_TARGET_MM = 22
LOGO_SMALL_SCREEN_DIAGONAL_MM = 190


class BlockClockApp:
    def __init__(self):
        self.root = tk.Tk()
        theme.init_fonts(self.root)
        self.root.title("Bitcoin Blockclock")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=theme.customizable_colors["background"])
        self.fullscreen = True
        self.backlight_on = True
        self.resize_id = None
        self.updater = DataUpdater()
        self.logo_size = None

        self.enabled_infos = [
            "Difficulty", "Halving", "Next Adjustment",
            "Tx Count", "Txs (Mempool)", "Block Fees",
            "Mempool Fees", "Hashrate"
        ]

        self.settings_frame = SettingsFrame(self.root, self)

        self.create_grid_layout()
        self.create_labels()
        self.update_data()
        controls_service.setup_key_bindings(self)
        self.root.bind("<Configure>", lambda event: controls_service.schedule_resize(self))

    def create_grid_layout(self):
        self.root.grid_rowconfigure(1, weight=3)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=3, minsize=400)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=10)
        self.root.grid_columnconfigure(2, weight=1)

    def create_labels(self):
        self.logo_source_image = Image.open("assets/bitcoin_logo.png")
        self.logo_photo = None
        self.logo_label = tk.Label(self.root, bg=theme.customizable_colors["background"])
        self.logo_label.grid(row=0, column=2, padx=10, pady=10, sticky="ne")
        self.logo_label.bind("<Button-1>", self.settings_frame.show)
        self.resize_logo()

        self.label_block_height = tk.Label(
            self.root, text="Loading...", font=theme.blockheight_font,
            fg=theme.customizable_colors["blockheight"], bg=theme.customizable_colors["background"]
        )
        self.label_block_height.grid(row=1, column=1, sticky="nsew", padx=20)

        self.label_last_block_time = tk.Label(
            self.root,
            text="",
            font=theme.detail_font,
            fg=theme.customizable_colors["text"],
            bg=theme.customizable_colors["background"],
            anchor="center",
            justify="center"
        )
        self.label_last_block_time.grid(row=2, column=1, sticky="nsew", padx=20, pady=(0, 30))


        self.detail_frame = tk.Frame(self.root, bg=theme.customizable_colors["background"])
        self.detail_frame.grid(row=3, column=1, sticky="nsew", padx=20, pady=10)
        self.detail_frame.grid_columnconfigure(0, weight=1)
        self.detail_frame.grid_columnconfigure(1, weight=1)

        self.detail_labels = []
        for i in range(8):
            row = i // 2
            col = i % 2
            wrapper = tk.Frame(self.detail_frame, bg=theme.customizable_colors["background"], bd=0,
                               highlightthickness=0)
            wrapper.grid(row=row, column=col, sticky="nsew")
            label = tk.Label(
                wrapper,
                text="",
                font=theme.detail_font,
                fg=theme.customizable_colors["text"],
                bg=theme.customizable_colors["background"],
                anchor="center",
                justify="center",
                bd=0,
                highlightthickness=0
            )
            label.pack(fill="both", expand=True, padx=20, pady=10)
            self.detail_labels.append(label)

        self.label_last_updated = tk.Label(
            self.root, text="Last update: loading...",
            font=theme.small_font_italic,
            fg=theme.customizable_colors["text"],
            bg=theme.customizable_colors["background"]
        )
        self.label_last_updated.grid(row=4, column=1, sticky="nsew", padx=10, pady=(10, 20))

    def update_data(self):
        try:
            snapshot = self.updater.fetch()

            # update UI
            self.label_block_height.config(text=str(snapshot.block_height))
            self.label_last_block_time.config(
                text=f"{snapshot.time_since_last_block_text}"
            )
            self.label_last_updated.config(
                text=f"Last update: {datetime.datetime.now().strftime('%H:%M:%S')}"
            )

            visible = snapshot.visible_detail_texts(self.enabled_infos)
            for i, label in enumerate(self.detail_labels):
                label.config(text=visible[i] if i < len(visible) else "")

        except Exception as e:
            logging.exception(f"Error fetching data: {e}")
            self.label_block_height.config(text="Error")

        self.root.after(20000, self.update_data)

    def update_enabled_infos(self, selected):
        self.enabled_infos = selected
        self.update_data()

    def resize_logo(self):
        monitor = self._get_active_monitor()
        size = self._logo_size_from_physical_size(monitor)
        if size is None:
            size = self._logo_size_from_resolution()

        if size == self.logo_size:
            return

        self.logo_size = size
        image = self.logo_source_image.resize((size, size))
        self.logo_photo = ImageTk.PhotoImage(image)
        self.logo_label.configure(image=self.logo_photo)

    def _get_active_monitor(self):
        try:
            self.root.update_idletasks()
            window_x = self.root.winfo_x()
            window_y = self.root.winfo_y()

            monitors = get_monitors()
            for monitor in monitors:
                if (monitor.x <= window_x < monitor.x + monitor.width and
                        monitor.y <= window_y < monitor.y + monitor.height):
                    return monitor

            return monitors[0] if monitors else None
        except Exception:
            return None

    def _logo_size_from_physical_size(self, monitor):
        if monitor is None:
            return None

        width_mm = getattr(monitor, "width_mm", 0) or 0
        height_mm = getattr(monitor, "height_mm", 0) or 0
        densities = []

        if width_mm > 0:
            densities.append(monitor.width / width_mm)
        if height_mm > 0:
            densities.append(monitor.height / height_mm)
        if not densities:
            return None

        target_mm = LOGO_TARGET_MM
        if width_mm > 0 and height_mm > 0:
            diagonal_mm = math.sqrt(width_mm ** 2 + height_mm ** 2)
            if diagonal_mm <= LOGO_SMALL_SCREEN_DIAGONAL_MM:
                target_mm = LOGO_SMALL_SCREEN_TARGET_MM

        pixels_per_mm = sum(densities) / len(densities)
        return self._clamp_logo_size(int(target_mm * pixels_per_mm))

    def _logo_size_from_resolution(self):
        width = self.root.winfo_width() or self.root.winfo_screenwidth()
        height = self.root.winfo_height() or self.root.winfo_screenheight()
        if width <= 1 or height <= 1:
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()

        short_side = max(1, min(width, height))
        scale = LOGO_REFERENCE_SHORT_SIDE / short_side
        return self._clamp_logo_size(int(LOGO_BASE_SIZE * scale))

    def _clamp_logo_size(self, size):
        return min(LOGO_MAX_SIZE, max(LOGO_BASE_SIZE, size))

    def run(self):
        self.root.mainloop()

    def refresh_theme(self):
        bg = theme.customizable_colors["background"]
        fg_text = theme.customizable_colors["text"]
        fg_blockheight = theme.customizable_colors["blockheight"]

        def apply_bg_recursive(widget):
            try:
                widget.configure(bg=bg, highlightthickness=0, bd=0)
            except:
                pass
            for child in widget.winfo_children():
                apply_bg_recursive(child)

        apply_bg_recursive(self.root)

        self.label_block_height.configure(fg=fg_blockheight)
        self.label_last_updated.configure(fg=fg_text)
        for label in self.detail_labels:
            label.configure(fg=fg_text)
