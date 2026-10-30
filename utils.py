import os
import customtkinter as ctk
from PIL import Image,ImageOps,ImageDraw, ImageFont



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(BASE_DIR, "assets", "icons")
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "fa-solid-900.ttf")
APP_ICON_PATH = os.path.join(ICON_DIR, "app.ico")

# icon name -> Font Awesome (Free, Solid) unicode
ICONS = {
    "home":         "\uf015",   # house
    "task":         "\uf0ae",   # list-check
    "hacking":      "\uf120",   # terminal
    "control":      "\uf1de",   # sliders
    "admin":        "\uf505",   # user-shield
    "settings":     "\uf013",   # gear
    "device":       "\uf108",   # desktop
    "play":         "\uf04b",   # play
    "stop":         "\uf04d",   # stop
    "plus":         "\uf067",   # plus
    "trash":        "\uf1f8",   # trash
    "user":         "\uf007",   # user
    "user_plus":    "\uf234",   # user-plus
    "alert":        "\uf071",   # triangle-exclamation
    "chevron_down": "\uf078",   # chevron-down
    "chevron_up":   "\uf077",   # chevron-up
    "user_circle":  "\uf2bd",   # circle-user
    "screen":       "\uf108",   # desktop
    "camera":       "\uf030",   # camera
    "mic":          "\uf130",   # microphone
    "headphones":   "\uf025",   # headphones
    "image":        "\uf03e",   # image
}

WHITE = (57, 255, 20, 255)   # #39ff14
DARK = (57, 255, 20, 255)    # #39ff14

_cache = {}
_warned = False


def _render(char, color, px=128):
    """Draw one Font Awesome glyph, centered, on a transparent square."""
    font = ImageFont.truetype(FONT_PATH, int(px * 0.78))
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    left, top, right, bottom = d.textbbox((0, 0), char, font=font)
    x = (px - (right - left)) / 2 - left
    y = (px - (bottom - top)) / 2 - top
    d.text((x, y), char, font=font, fill=color)
    return img


def load_icon(name, size=20):
    """Use assets/icons/<name>.png if it exists, otherwise a Font Awesome icon."""
    global _warned
    key = (name, size)
    if key in _cache:
        return _cache[key]

    # 1) custom PNG file
    png_path = os.path.join(ICON_DIR, f"{name}.png")
    if os.path.exists(png_path):
        img = Image.open(png_path).convert("RGBA")
        _cache[key] = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        return _cache[key]

    # 2) Font Awesome
    if name not in ICONS:
        return None
    if not os.path.exists(FONT_PATH):
        if not _warned:
            print(f"[icons] Font file not found: {FONT_PATH}")
            _warned = True
        return None

    char = ICONS[name]
    _cache[key] = ctk.CTkImage(
        light_image=_render(char, DARK),
        dark_image=_render(char, WHITE),
        size=(size, size),
    )
    return _cache[key]


def load_brand_icon(size=30):
    """Load the app's actual Windows icon for the in-app brand mark."""
    key = ("__brand__", size)
    if key in _cache:
        return _cache[key]
    if not os.path.exists(APP_ICON_PATH):
        return None
    try:
        with Image.open(APP_ICON_PATH) as source:
            image = source.convert("RGBA")
        _cache[key] = ctk.CTkImage(
            light_image=image, dark_image=image, size=(size, size))
        return _cache[key]
    except Exception as exc:
        print(f"[icons] Could not load app icon: {exc}")
        return None


def user_data_dir():
    """Return a per-user folder for local app settings and device labels."""
    root = os.environ.get("LOCALAPPDATA")
    if not root:
        root = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(root, "DeepTracker")


def page_title(parent, text, icon_name):
    """Page heading with an icon on the left."""
    lbl = ctk.CTkLabel(
        parent, text=f"  {text}", image=load_icon(icon_name, 28), compound="left",
        font=ctk.CTkFont(size=28, weight="bold"),
    )
    lbl.pack(anchor="w", padx=30, pady=(30, 10))
    return lbl
