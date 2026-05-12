from tkinter import font
import view_utils

BLOCK_HEIGHT_FONT_SIZE = 300

FAMILY = "Roboto"

blockheight_font = None
detail_font = None
small_font = None
small_font_italic = None
tiny_font = None

customizable_colors = {
    "background": "#000000",
    "text": "#7c8680",
    "blockheight": "#e8eceb"
}

default_colors = {
    "frame_background": "#1e1e1e",
    "white": "white",
    "btc_orange": "#F7931A",
    "red": "#ff3333",
}

def init_fonts(root):
    update_fonts(root)

def update_fonts(root):
    global blockheight_font, detail_font, small_font, small_font_italic, tiny_font

    blockheight_font = font.Font(
        family=FAMILY,
        size=view_utils.get_scaled_font(root, BLOCK_HEIGHT_FONT_SIZE),
        weight="normal"
    )

    detail_font = font.Font(
        family=FAMILY,
        size=view_utils.get_scaled_font(root, 45),
        weight="normal"
    )

    small_font = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 25))
    small_font_italic = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 25), slant="italic")
    tiny_font = font.Font(family=FAMILY, size=10)
