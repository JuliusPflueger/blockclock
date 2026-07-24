import datetime
import logging
import tkinter as tk
from zoneinfo import ZoneInfo

from PIL import Image, ImageTk

import controls.controls_service as controls_service
import theme
from data.data_updater import DataUpdater
from data import status_reporter
from settings import SettingsFrame


LOGO_BASE_SIZE = 42
CURSOR_HIDE_DELAY_MS = 10_000
LOS_ANGELES_TIMEZONE = ZoneInfo("America/Los_Angeles")


class BlockClockApp:
    """A distraction-free Bitcoin network display with a dashboard hierarchy."""

    def __init__(self):
        self.root = tk.Tk()
        theme.init_fonts(self.root)
        self.root.title("Blockclock")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=theme.customizable_colors["background"])
        self.fullscreen = True
        self.backlight_on = True
        self.resize_id = None
        self.cursor_hide_id = None
        self.update_after_id = None
        self.last_successful_refresh = "—"
        self.updater = DataUpdater()
        self.enabled_infos = [
            "Txs Last Block", "Mempool Txs", "Fees Last Block", "Mempool Fees",
            "Difficulty", "Halving", "Next Adjustment", "Hashrate"
        ]

        self.settings_frame = SettingsFrame(self.root, self)
        self.create_layout()
        self.update_data()
        controls_service.setup_key_bindings(self)
        self.root.bind("<Configure>", lambda event: controls_service.schedule_resize(self))
        self.root.bind_all("<Motion>", self.reset_cursor_timeout, add="+")
        self.hide_cursor()

    def reset_cursor_timeout(self, event=None):
        self.root.configure(cursor="")
        self.hide_cursor_after_inactivity()

    def hide_cursor_after_inactivity(self):
        if self.cursor_hide_id is not None:
            self.root.after_cancel(self.cursor_hide_id)
        self.cursor_hide_id = self.root.after(CURSOR_HIDE_DELAY_MS, self.hide_cursor)

    def hide_cursor(self):
        self.cursor_hide_id = None
        self.root.configure(cursor="none")

    def create_layout(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.header = tk.Frame(self.root, bg=theme.customizable_colors["background"])
        self.header.grid(row=0, column=0, sticky="ew", padx=48, pady=(30, 0))
        self.header.grid_columnconfigure(1, weight=1)

        logo_image = Image.open("assets/bitcoin_logo.png").resize((LOGO_BASE_SIZE, LOGO_BASE_SIZE))
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        self.logo_label = tk.Label(self.header, image=self.logo_photo, cursor="hand2",
                                   bg=theme.customizable_colors["background"], bd=0)
        self.logo_label.grid(row=0, column=2, sticky="e")
        self.logo_label.bind("<Button-1>", self.settings_frame.show)

        self.content = tk.Frame(self.root, bg=theme.customizable_colors["background"])
        self.content.grid(row=1, column=0, sticky="nsew", padx=48, pady=(20, 30))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.hero_card = self._card(self.content)
        self.hero_card.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        self.hero_card.grid_columnconfigure(0, weight=1)
        tk.Label(self.hero_card, text="LAST BLOCK", font=theme.eyebrow_font,
                 fg=theme.default_colors["muted"], bg=theme.default_colors["card_background"]).grid(row=0, column=0, pady=(28, 0))
        self.label_block_height = tk.Label(self.hero_card, text="—", font=theme.blockheight_font,
                                           fg=theme.customizable_colors["blockheight"], bg=theme.default_colors["card_background"])
        self.label_block_height.grid(row=1, column=0, pady=(0, 0))
        self.label_last_block_time = tk.Label(self.hero_card, text="Connecting to the network…", font=theme.detail_font,
                                              fg=theme.customizable_colors["text"], bg=theme.default_colors["card_background"])
        self.label_last_block_time.grid(row=2, column=0, pady=(0, 28))

        self.detail_frame = tk.Frame(self.content, bg=theme.customizable_colors["background"])
        self.detail_frame.grid(row=1, column=0, sticky="nsew")
        for column in range(4):
            self.detail_frame.grid_columnconfigure(column, weight=1, uniform="cards")
        for row in range(2):
            self.detail_frame.grid_rowconfigure(row, weight=1)

        self.detail_cards = []
        for index in range(8):
            card = self._card(self.detail_frame)
            card.grid(row=index // 4, column=index % 4, sticky="nsew", padx=7, pady=7)
            title = tk.Label(card, text="", font=theme.card_title_font, anchor="w",
                             fg=theme.default_colors["muted"], bg=theme.default_colors["card_background"])
            title.pack(fill="x", padx=22, pady=(20, 5))
            value = tk.Label(card, text="—", font=theme.card_value_font, anchor="w", justify="left",
                             fg=theme.customizable_colors["text"], bg=theme.default_colors["card_background"], wraplength=340)
            value.pack(fill="both", expand=True, padx=22, pady=(0, 16))
            self.detail_cards.append((card, title, value))

        self.label_last_updated = tk.Label(self.root, text="LAST REFRESH · CONNECTING", font=theme.tiny_font,
                                           fg=theme.default_colors["subtle"], bg=theme.customizable_colors["background"])
        self.label_last_updated.grid(row=2, column=0, pady=(0, 22))

    @staticmethod
    def _card(parent):
        return tk.Frame(parent, bg=theme.default_colors["card_background"],
                        highlightbackground=theme.default_colors["card_border"], highlightthickness=1, bd=0)

    @staticmethod
    def _card_title(name):
        return {
            "Halving": "HALVING (BLOCKS)",
            "Next Adjustment": "NEXT ADJUSTMENT (BLOCKS)",
        }.get(name, name.upper())

    def update_data(self):
        try:
            snapshot = self.updater.fetch()
            self.label_block_height.config(text=str(snapshot.block_height))
            self.label_last_block_time.config(text=f"{snapshot.time_since_last_block_text}  ·  {snapshot.block_finder_name}")
            self.last_successful_refresh = datetime.datetime.now(LOS_ANGELES_TIMEZONE).strftime("%H:%M:%S")
            self.label_last_updated.config(text=f"LAST REFRESH · {self.last_successful_refresh}")

            visible = snapshot.detail_cards(self.enabled_infos)
            for index, (card, title, value) in enumerate(self.detail_cards):
                if index < len(visible):
                    card.grid()
                    title.config(text=self._card_title(visible[index][0]))
                    value.config(text=visible[index][1])
                else:
                    card.grid_remove()
            # This is deliberately written only after the visible labels have
            # been updated
            self.root.update_idletasks()
            status_reporter.report_success(snapshot.block_height, snapshot.block_finder_name)
        except Exception as error:
            logging.exception("Error fetching data: %s", error)
            self.label_last_block_time.config(text="Unable to reach the Bitcoin network")
            self.label_last_updated.config(text=f"LAST REFRESH · {self.last_successful_refresh} · RETRYING")
            status_reporter.report_failure()

        self.update_after_id = self.root.after(10_000, self.update_data)

    def update_enabled_infos(self, selected):
        self.enabled_infos = list(selected)
        if self.update_after_id is not None:
            self.root.after_cancel(self.update_after_id)
            self.update_after_id = None
        self.update_data()

    def run(self):
        self.root.mainloop()

    def refresh_theme(self):
        bg = theme.customizable_colors["background"]
        card_bg = theme.default_colors["card_background"]
        self.root.configure(bg=bg)
        for widget in (self.header, self.content, self.detail_frame):
            widget.configure(bg=bg)
        for widget in (self.logo_label, self.label_last_updated):
            widget.configure(bg=bg)
        hero_bg = bg if theme.transparent_tiles else card_bg
        self.hero_card.configure(bg=hero_bg,
                                 highlightbackground=bg if theme.transparent_tiles else theme.default_colors["card_border"])
        for widget in self.hero_card.winfo_children():
            widget.configure(bg=hero_bg)
        self.label_block_height.configure(fg=theme.customizable_colors["blockheight"])
        self.label_last_block_time.configure(fg=theme.customizable_colors["text"])
        for card, title, value in self.detail_cards:
            tile_bg = bg if theme.transparent_tiles else card_bg
            card.configure(bg=tile_bg,
                           highlightbackground=bg if theme.transparent_tiles else theme.default_colors["card_border"])
            title.configure(bg=tile_bg)
            value.configure(bg=tile_bg, fg=theme.customizable_colors["text"])
