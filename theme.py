from tkinter import font
import view_utils

BLOCK_HEIGHT_FONT_SIZE = 210

# Tk falls back gracefully when a family is not installed.  These are the
# platform fonts that get closest to the quiet, high-contrast system look.
FAMILY = "SF Pro Display" if __import__("platform").system() == "Darwin" else "Roboto"

blockheight_font = None
detail_font = None
card_value_font = None
card_title_font = None
eyebrow_font = None
small_font = None
small_font_italic = None
tiny_font = None

customizable_colors = {
    "background": "#0B0B0D",
    "text": "#A1A1AA",
    "blockheight": "#F5F5F7"
}

# This is a display preference rather than a color, but lives with the theme
# because it controls how the dashboard surface is rendered.
transparent_tiles = False

default_colors = {
    "frame_background": "#17171B",
    "card_background": "#17171B",
    "card_border": "#2A2A30",
    "white": "#F5F5F7",
    "muted": "#8E8E93",
    "subtle": "#63636B",
    "btc_orange": "#F7931A",
    "green": "#30D158",
    "red": "#FF453A",
}

def init_fonts(root):
    update_fonts(root)

def update_fonts(root):
    global blockheight_font, detail_font, card_value_font, card_title_font, eyebrow_font, small_font, small_font_italic, tiny_font

    blockheight_font = font.Font(
        family=FAMILY,
        size=view_utils.get_scaled_font(root, BLOCK_HEIGHT_FONT_SIZE),
        weight="normal"
    )

    detail_font = font.Font(
        family=FAMILY,
        size=view_utils.get_scaled_font(root, 32),
        weight="normal"
    )

    card_value_font = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 28), weight="bold")
    card_title_font = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 16), weight="normal")
    eyebrow_font = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 16), weight="bold")

    small_font = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 20))
    small_font_italic = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 18), slant="italic")
    tiny_font = font.Font(family=FAMILY, size=view_utils.get_scaled_font(root, 14))
