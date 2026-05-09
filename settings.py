import tkinter as tk
import tkinter.colorchooser as colorchooser
from typing import Callable, Dict, Optional, Tuple, Union
import theme

CANVAS_WIDTH = 150
CANVAS_HEIGHT = 30
RADIUS_SMALL = 6
RADIUS_MEDIUM = 8

SWITCH_WIDTH = 50
SWITCH_HEIGHT = 30
SWITCH_KNOB_DIAMETER = 20
SWITCH_PADDING = 5

COLOR_BOX_SIZE = 40
COLOR_PADDING = 1
INNER_OFFSET_EXTRA = 2

TAB_NAMES = ("Info", "Colors")

def draw_rounded_rect(
        canvas: tk.Canvas,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        radius: int,
        fill: str,
        outline: str = None,
        tags: Optional[Union[str, Tuple[str, ...]]] = None,
):
    if outline is None:
        outline = fill

    canvas.create_arc(x0, y0, x0 + radius * 2, y0 + radius * 2,
                      start=90, extent=90, fill=fill, outline=outline, tags=tags)
    canvas.create_arc(x1 - radius * 2, y0, x1, y0 + radius * 2,
                      start=0, extent=90, fill=fill, outline=outline, tags=tags)
    canvas.create_arc(x0, y1 - radius * 2, x0 + radius * 2, y1,
                      start=180, extent=90, fill=fill, outline=outline, tags=tags)
    canvas.create_arc(x1 - radius * 2, y1 - radius * 2, x1, y1,
                      start=270, extent=90, fill=fill, outline=outline, tags=tags)

    canvas.create_rectangle(x0 + radius, y0, x1 - radius, y1,
                            fill=fill, outline=outline, tags=tags)
    canvas.create_rectangle(x0, y0 + radius, x1, y1 - radius,
                            fill=fill, outline=outline, tags=tags)


def create_pill_button(
        parent: tk.Widget,
        text: str,
        bg: str,
        fg: str,
        font,
        command: Callable[[], None],
) -> tk.Canvas:
    canvas = tk.Canvas(
        parent,
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT,
        bg=theme.default_colors["frame_background"],
        highlightthickness=0,
        bd=0
    )
    canvas.pack(pady=5)

    draw_rounded_rect(
        canvas,
        0, 0,
        CANVAS_WIDTH, CANVAS_HEIGHT,
        radius=RADIUS_SMALL,
        fill=bg,
        outline=bg
    )

    label = canvas.create_text(
        CANVAS_WIDTH // 2,
        CANVAS_HEIGHT // 2,
        text=text,
        fill=fg,
        font=font
    )

    canvas.tag_bind(label, "<Button-1>", lambda e: command())
    canvas.tag_bind("all", "<Button-1>", lambda e: command())

    return canvas

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent: tk.Widget, initial_state: bool, on_change: Callable[[bool], None], **kwargs):
        super().__init__(
            parent,
            width=SWITCH_WIDTH,
            height=SWITCH_HEIGHT,
            highlightthickness=0,
            **kwargs
        )
        self._state = initial_state
        self._on_change = on_change
        self.bind("<Button-1>", self._toggle)
        self._draw()

    @property
    def state(self) -> bool:
        return self._state

    def _toggle(self, _event=None):
        self._state = not self._state
        self._draw()
        self._on_change(self._state)

    def _draw(self):
        self.delete("all")
        bg_color = "#4CAF50" if self._state else "#555555"
        knob_x = (SWITCH_WIDTH - SWITCH_PADDING - SWITCH_KNOB_DIAMETER
                  if self._state else SWITCH_PADDING)

        draw_rounded_rect(
            self,
            0, 0,
            SWITCH_WIDTH, SWITCH_HEIGHT,
            radius=RADIUS_SMALL,
            fill=bg_color,
            outline=bg_color
        )

        self.create_oval(
            knob_x,
            (SWITCH_HEIGHT - SWITCH_KNOB_DIAMETER) // 2,
            knob_x + SWITCH_KNOB_DIAMETER,
            (SWITCH_HEIGHT - SWITCH_KNOB_DIAMETER) // 2 + SWITCH_KNOB_DIAMETER,
            fill="white",
            outline="white"
        )


class ColorSwatch(tk.Canvas):
    def __init__(self, parent: tk.Widget, color: str, on_pick: Callable[[str], None], **kwargs):
        super().__init__(
            parent,
            width=COLOR_BOX_SIZE,
            height=COLOR_BOX_SIZE,
            highlightthickness=0,
            **kwargs
        )
        self._current_color = color
        self._on_pick = on_pick
        self.bind("<Button-1>", self._pick)
        self._draw()

    def update_color(self, color):
        self._current_color = color
        self.itemconfig("color", fill=color, outline=color)

    def _draw(self):
        self.delete("all")
        white = theme.default_colors["white"]
        radius = RADIUS_SMALL
        padding = COLOR_PADDING
        inner_offset = padding + INNER_OFFSET_EXTRA
        r = radius - padding

        draw_rounded_rect(
            self,
            0, 0,
            COLOR_BOX_SIZE, COLOR_BOX_SIZE,
            radius=radius,
            fill=white,
            outline=white
        )

        self.create_arc(
            inner_offset,
            inner_offset,
            inner_offset + r * 2,
            inner_offset + r * 2,
            start=90, extent=90,
            fill=self._current_color,
            outline=self._current_color,
            tags="color"
        )
        self.create_arc(
            COLOR_BOX_SIZE - (r * 2 + inner_offset),
            inner_offset,
            COLOR_BOX_SIZE - inner_offset,
            inner_offset + r * 2,
            start=0, extent=90,
            fill=self._current_color,
            outline=self._current_color,
            tags="color"
        )
        self.create_arc(
            inner_offset,
            COLOR_BOX_SIZE - (r * 2 + inner_offset),
            inner_offset + r * 2,
            COLOR_BOX_SIZE - inner_offset,
            start=180, extent=90,
            fill=self._current_color,
            outline=self._current_color,
            tags="color"
        )
        self.create_arc(
            COLOR_BOX_SIZE - (r * 2 + inner_offset),
            COLOR_BOX_SIZE - (r * 2 + inner_offset),
            COLOR_BOX_SIZE - inner_offset,
            COLOR_BOX_SIZE - inner_offset,
            start=270, extent=90,
            fill=self._current_color,
            outline=self._current_color,
            tags="color"
        )

        self.create_rectangle(
            inner_offset + r,
            inner_offset,
            COLOR_BOX_SIZE - (r + inner_offset),
            COLOR_BOX_SIZE - inner_offset,
            fill=self._current_color,
            outline=self._current_color,
            tags="color"
        )
        self.create_rectangle(
            inner_offset,
            inner_offset + r,
            COLOR_BOX_SIZE - inner_offset,
            COLOR_BOX_SIZE - (r + inner_offset),
            fill=self._current_color,
            outline=self._current_color,
            tags="color"
        )

    def _pick(self, _event=None):
        color = colorchooser.askcolor(initialcolor=self._current_color)[1]
        if color:
            self.update_color(color)
            self._on_pick(color)


class SettingsFrame(tk.Toplevel):
    INFO_LABELS = [
        "Difficulty", "Halving", "Next Adjustment", "Tx Count",
        "Txs (Mempool)", "Block Fees", "Mempool Fees", "Hashrate"
    ]

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.title("Settings")
        self.configure(bg=theme.default_colors["frame_background"])
        self.geometry("600x800")

        self.temp_colors: Dict[str, str] = theme.customizable_colors.copy()

        self._tabs: Dict[str, tk.Label] = {}
        self._tab_frames: Dict[str, tk.Frame] = {}
        self._active_tab: Optional[str] = None

        self._build_ui()
        self._show_tab("Info")

        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def _build_ui(self):
        self.content = tk.Frame(self, bg=theme.default_colors["frame_background"])
        self.content.pack(fill="both", expand=True)

        self._build_tab_header()
        self._build_tab_body()
        self._build_tabs()
        self._add_action_buttons_to_tabs()

    def _build_tab_header(self):
        self.tab_header = tk.Frame(self.content, bg=theme.default_colors["frame_background"])
        self.tab_header.pack(fill="x")

        for col in range(len(TAB_NAMES)):
            self.tab_header.columnconfigure(col, weight=1)

        for idx, tab_name in enumerate(TAB_NAMES):
            tab_btn = tk.Label(
                self.tab_header,
                text=tab_name,
                font=theme.small_font,
                fg=theme.default_colors["white"],
                bg=theme.default_colors["frame_background"],
                pady=10,
                width=8
            )
            tab_btn.grid(row=0, column=idx, sticky="nsew")
            tab_btn.bind("<Button-1>", lambda _e, name=tab_name: self._show_tab(name))
            self._tabs[tab_name] = tab_btn

    def _build_tab_body(self):
        self.tab_body = tk.Frame(self.content, bg=theme.default_colors["frame_background"])
        self.tab_body.pack(fill="both", expand=True)

    def _build_tabs(self):
        self._tab_frames = {
            "Info": tk.Frame(self.tab_body, bg=theme.default_colors["frame_background"]),
            "Colors": tk.Frame(self.tab_body, bg=theme.default_colors["frame_background"]),
        }

        # Info-Tab
        info_inner = tk.Frame(self._tab_frames["Info"], bg=theme.default_colors["frame_background"])
        info_inner.pack(pady=20)

        for row, label_text in enumerate(self.INFO_LABELS):
            self._create_info_row(info_inner, row, label_text)

        # Colors-Tab
        color_inner = tk.Frame(self._tab_frames["Colors"], bg=theme.default_colors["frame_background"])
        color_inner.pack(pady=20)

        for row, key in enumerate(theme.customizable_colors):
            self._create_color_row(color_inner, row, key)

    def _add_action_buttons_to_tabs(self):
        for frame in self._tab_frames.values():
            btn_frame = tk.Frame(frame, bg=theme.default_colors["frame_background"])
            btn_frame.pack(side="bottom", pady=30)

            # Apply
            wrapper_apply = tk.Frame(btn_frame, bg=theme.default_colors["frame_background"])
            wrapper_apply.pack(side="left", padx=10)
            create_pill_button(
                wrapper_apply,
                "Apply",
                theme.default_colors["btc_orange"],
                "white",
                theme.tiny_font,
                self._apply_settings
            )

            # Shutdown
            wrapper_shutdown = tk.Frame(btn_frame, bg=theme.default_colors["frame_background"])
            wrapper_shutdown.pack(side="left", padx=10)
            create_pill_button(
                wrapper_shutdown,
                "Shut down",
                theme.default_colors["red"],
                "white",
                theme.tiny_font,
                self.master.destroy
            )

    def _show_tab(self, tab_name: str):
        for frame in self._tab_frames.values():
            frame.pack_forget()

        self._tab_frames[tab_name].pack(fill="both", expand=True)

        for name, tab in self._tabs.items():
            tab.configure(
                bg=theme.default_colors["btc_orange"]
                if name == tab_name else theme.default_colors["frame_background"]
            )

        self._active_tab = tab_name

    def _create_info_row(self, parent: tk.Widget, row: int, label_text: str):
        def on_toggle(state: bool):
            if state:
                if label_text not in self.app.enabled_infos:
                    self.app.enabled_infos.append(label_text)
            else:
                if label_text in self.app.enabled_infos:
                    self.app.enabled_infos.remove(label_text)

        switch = ToggleSwitch(
            parent,
            initial_state=(label_text in self.app.enabled_infos),
            on_change=on_toggle,
            bg=theme.default_colors["frame_background"]
        )
        switch.grid(row=row, column=0, padx=20, pady=6, sticky="w")

        label = tk.Label(
            parent,
            text=label_text,
            font=theme.small_font,
            bg=theme.default_colors["frame_background"],
            fg=theme.default_colors["white"],
            anchor="w"
        )
        label.grid(row=row, column=1, padx=10, sticky="w")

    def _create_color_row(self, parent: tk.Widget, row: int, key: str):
        def on_pick(color: str):
            self.temp_colors[key] = color

        swatch = ColorSwatch(
            parent,
            color=self.temp_colors[key],
            on_pick=on_pick,
            bg=theme.default_colors["frame_background"]
        )
        swatch.grid(row=row, column=0, padx=20, pady=6, sticky="w")

        label = tk.Label(
            parent,
            text=key,
            font=theme.small_font,
            bg=theme.default_colors["frame_background"],
            fg=theme.default_colors["white"]
        )
        label.grid(row=row, column=1, padx=10, sticky="w")

    def _apply_settings(self):
        try:
            theme.customizable_colors.update(self.temp_colors)
            self.app.refresh_theme()
            self.app.update_enabled_infos(self.app.enabled_infos)
            self.withdraw()
        except ValueError:
            print("Invalid input")

    def show(self, event=None):
        self.refresh_theme()
        self.deiconify()
        self.lift()
        self.focus_force()

    def refresh_theme(self):
        frame_bg = theme.default_colors["frame_background"]

        def apply(widget):
            try:
                if isinstance(widget, tk.Canvas):
                    widget.configure(bg=frame_bg)
                else:
                    widget.configure(bg=frame_bg)
            except Exception:
                pass
            for child in widget.winfo_children():
                apply(child)

        apply(self)

        if self._active_tab:
            self._show_tab(self._active_tab)
