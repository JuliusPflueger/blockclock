import tkinter as tk
import tkinter.colorchooser as colorchooser

import theme


class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, initial_state, on_change):
        super().__init__(parent, width=52, height=32, highlightthickness=0,
                         bg=theme.default_colors["card_background"], bd=0, cursor="hand2")
        self.state = initial_state
        self.on_change = on_change
        self.bind("<Button-1>", self.toggle)
        self.draw()

    def toggle(self, _event=None):
        self.state = not self.state
        self.draw()
        self.on_change(self.state)

    def draw(self):
        self.delete("all")
        track = theme.default_colors["btc_orange"] if self.state else "#3A3A40"
        self.create_oval(0, 1, 30, 31, fill=track, outline=track)
        self.create_oval(22, 1, 52, 31, fill=track, outline=track)
        self.create_rectangle(15, 1, 37, 31, fill=track, outline=track)
        x = 22 if self.state else 2
        self.create_oval(x, 3, x + 26, 29, fill=theme.default_colors["white"], outline=theme.default_colors["white"])


class SettingsFrame(tk.Toplevel):
    INFO_LABELS = ["Difficulty", "Halving", "Next Adjustment", "Tx Count",
                   "Txs (Mempool)", "Block Fees", "Mempool Fees", "Hashrate"]

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Blockclock Settings")
        self.configure(bg=theme.customizable_colors["background"])
        self.geometry("720x660")
        self.minsize(620, 580)
        self.resizable(True, True)
        self.temp_colors = theme.customizable_colors.copy()
        self.temp_enabled_infos = list(app.enabled_infos)
        self.temp_transparent_tiles = theme.transparent_tiles
        self.active_tab = "Overview"
        self.tab_buttons = {}
        self.tab_frames = {}
        self.metric_switches = {}
        self.color_swatches = {}
        self._build_ui()
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def _build_ui(self):
        bg = theme.customizable_colors["background"]
        self.header = tk.Frame(self, bg=bg)
        self.header.pack(fill="x", padx=34, pady=(30, 18))
        tk.Label(self.header, text="SETTINGS", font=theme.eyebrow_font, fg=theme.default_colors["btc_orange"], bg=bg).pack(anchor="w")

        tabs = tk.Frame(self, bg=bg)
        tabs.pack(fill="x", padx=34)
        for name in ("Overview", "Appearance"):
            button = tk.Label(tabs, text=name, font=theme.tiny_font, padx=16, pady=10, cursor="hand2")
            button.pack(side="left", padx=(0, 8))
            button.bind("<Button-1>", lambda _event, tab=name: self.show_tab(tab))
            self.tab_buttons[name] = button

        self.body = tk.Frame(self, bg=bg)
        self.body.pack(fill="both", expand=True, padx=34, pady=(18, 10))
        self._build_overview()
        self._build_appearance()

        actions = tk.Frame(self, bg=bg)
        actions.pack(fill="x", padx=34, pady=(8, 30))
        self._button(actions, "Shut down", self.app.root.destroy, danger=True).pack(side="left")
        self._button(actions, "Cancel", self.withdraw, secondary=True).pack(side="right")
        self._button(actions, "Apply changes", self.apply_settings).pack(side="right", padx=(0, 10))
        self.show_tab("Overview")

    def _build_overview(self):
        frame = self._panel(self.body)
        self.tab_frames["Overview"] = frame
        tk.Label(frame, text="Visible metrics", font=theme.small_font, fg=theme.default_colors["white"], bg=theme.default_colors["card_background"]).pack(anchor="w", padx=24, pady=(22, 2))
        grid = tk.Frame(frame, bg=theme.default_colors["card_background"])
        grid.pack(fill="both", expand=True, padx=16, pady=(10, 14))
        for column in range(2):
            grid.grid_columnconfigure(column, weight=1)
        for index, name in enumerate(self.INFO_LABELS):
            row = index // 2
            column = index % 2
            item = tk.Frame(grid, bg=theme.default_colors["card_background"])
            item.grid(row=row, column=column, sticky="ew", padx=8, pady=5)
            switch = ToggleSwitch(item, name in self.temp_enabled_infos,
                                  lambda enabled, label=name: self._set_metric(label, enabled))
            switch.pack(side="left")
            self.metric_switches[name] = switch
            tk.Label(item, text=name, font=theme.tiny_font, fg=theme.default_colors["white"], bg=theme.default_colors["card_background"]).pack(side="left", padx=10)

    def _build_appearance(self):
        frame = self._panel(self.body)
        self.tab_frames["Appearance"] = frame
        tk.Label(frame, text="Color palette", font=theme.small_font, fg=theme.default_colors["white"], bg=theme.default_colors["card_background"]).pack(anchor="w", padx=24, pady=(22, 2))
        for key, label in (("background", "Background"), ("blockheight", "Block height"), ("text", "Detail text")):
            row = tk.Frame(frame, bg=theme.default_colors["card_background"])
            row.pack(fill="x", padx=24, pady=8)
            tk.Label(row, text=label, font=theme.tiny_font, fg=theme.default_colors["white"], bg=theme.default_colors["card_background"]).pack(side="left")
            swatch = tk.Label(row, text="", width=5, height=1, cursor="hand2", relief="flat")
            swatch.pack(side="right")
            self._paint_swatch(swatch, key)
            self.color_swatches[key] = swatch
            swatch.bind("<Button-1>", lambda _event, color_key=key, widget=swatch: self.pick_color(color_key, widget))

        tile_row = tk.Frame(frame, bg=theme.default_colors["card_background"])
        tile_row.pack(fill="x", padx=24, pady=(12, 18))
        tk.Label(tile_row, text="Transparent tiles", font=theme.tiny_font,
                 fg=theme.default_colors["white"], bg=theme.default_colors["card_background"]).pack(side="left")
        self.transparent_switch = ToggleSwitch(tile_row, self.temp_transparent_tiles, self._set_transparent_tiles)
        self.transparent_switch.pack(side="right")

    @staticmethod
    def _panel(parent):
        return tk.Frame(parent, bg=theme.default_colors["card_background"], highlightbackground=theme.default_colors["card_border"], highlightthickness=1)

    def _button(self, parent, text, command, secondary=False, danger=False):
        bg = theme.default_colors["red"] if danger else ("#2A2A30" if secondary else theme.default_colors["btc_orange"])
        fg = theme.default_colors["white"]
        button = tk.Label(parent, text=text, font=theme.tiny_font, fg=fg, bg=bg, padx=16, pady=10, cursor="hand2")
        button.bind("<Button-1>", lambda _event: command())
        return button

    def _set_metric(self, name, enabled):
        if enabled and name not in self.temp_enabled_infos:
            self.temp_enabled_infos.append(name)
        elif not enabled and name in self.temp_enabled_infos:
            self.temp_enabled_infos.remove(name)

    def _set_transparent_tiles(self, enabled):
        self.temp_transparent_tiles = enabled

    def _paint_swatch(self, widget, key):
        widget.configure(bg=self.temp_colors[key], highlightbackground=theme.default_colors["card_border"], highlightthickness=1)

    def pick_color(self, key, widget):
        selected = colorchooser.askcolor(initialcolor=self.temp_colors[key], parent=self)[1]
        if selected:
            self.temp_colors[key] = selected
            self._paint_swatch(widget, key)

    def show_tab(self, name):
        self.active_tab = name
        for tab_name, frame in self.tab_frames.items():
            if tab_name == name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
        for tab_name, button in self.tab_buttons.items():
            active = tab_name == name
            button.configure(bg=theme.default_colors["btc_orange"] if active else theme.default_colors["frame_background"],
                             fg=theme.default_colors["white"] if active else theme.default_colors["muted"])

    def apply_settings(self):
        theme.customizable_colors.update(self.temp_colors)
        theme.transparent_tiles = self.temp_transparent_tiles
        self.app.refresh_theme()
        self.app.update_enabled_infos(self.temp_enabled_infos)
        self.withdraw()

    def show(self, _event=None):
        self.temp_colors = theme.customizable_colors.copy()
        self.temp_enabled_infos = list(self.app.enabled_infos)
        self.temp_transparent_tiles = theme.transparent_tiles
        self.transparent_switch.state = self.temp_transparent_tiles
        self.transparent_switch.draw()
        for key, swatch in self.color_swatches.items():
            self._paint_swatch(swatch, key)
        for name, switch in self.metric_switches.items():
            switch.state = name in self.temp_enabled_infos
            switch.draw()
        self.deiconify()
        self.lift()
        self.focus_force()
