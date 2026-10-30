import customtkinter as ctk

# ---- Hacking Mode palette ----
BG        = "#09141c"
PANEL     = "#101e28"
PANEL2    = "#172a35"
ENTRY     = "#0b1720"
BORDER    = "#263d49"
GREEN     = "#58e0ad"
GREEN_DIM = "#32b987"
MUTED     = "#8da3ad"
BTN       = "#193b35"
HOVER     = "#24564b"
ACTIVE    = "#193b35"
GLOW      = "#a0f3d0"
TRACK     = "#263744"
RED       = "#ff7180"
RED_BTN   = "#42242b"
RED_HOVER = "#63323c"

FONT = "Consolas"


def apply_theme():
    """Call once, BEFORE the window is created."""
    ctk.set_default_color_theme("blue")
    t = ctk.ThemeManager.theme

    t["CTk"]["fg_color"] = BG
    t["CTkToplevel"]["fg_color"] = BG
    t["CTkFrame"].update(fg_color=PANEL, top_fg_color=PANEL2, border_color=BORDER)

    t["CTkButton"].update(
        fg_color=BTN, hover_color=HOVER, text_color=GREEN,
        text_color_disabled=MUTED, corner_radius=4,
        border_color=BORDER,
    )
    t["CTkLabel"]["text_color"] = GREEN
    t["CTkEntry"].update(
        fg_color=ENTRY, border_color=BORDER, text_color=GREEN,
        placeholder_text_color=MUTED, corner_radius=4,
    )
    t["CTkCheckBox"].update(
        fg_color=GREEN_DIM, border_color=BORDER, hover_color=HOVER,
        checkmark_color=BG, text_color=GREEN, text_color_disabled=MUTED,
    )
    t["CTkSwitch"].update(
        fg_color=TRACK, progress_color=GREEN_DIM, button_color=GREEN,
        button_hover_color=GLOW, text_color=GREEN, text_color_disabled=MUTED,
    )
    t["CTkSlider"].update(
        fg_color=TRACK, progress_color=GREEN_DIM, button_color=GREEN,
        button_hover_color=GLOW,
    )
    t["CTkOptionMenu"].update(
        fg_color=BTN, button_color=HOVER, button_hover_color=GREEN_DIM,
        text_color=GREEN, text_color_disabled=MUTED,
    )
    t["CTkScrollbar"].update(button_color=BORDER, button_hover_color=GREEN_DIM)
    t["CTkTextbox"].update(
        fg_color=ENTRY, border_color=BORDER, text_color=GREEN,
        scrollbar_button_color=BORDER, scrollbar_button_hover_color=GREEN_DIM,
    )
    t["CTkScrollableFrame"]["label_fg_color"] = PANEL2
    t["DropdownMenu"].update(fg_color=PANEL, hover_color=BTN, text_color=GREEN)

    # monospace font everywhere (works with old and new CustomTkinter)
    font_theme = t["CTkFont"]
    if "Windows" in font_theme:          # older CustomTkinter
        font_theme["Windows"]["family"] = FONT
        font_theme["Windows"]["size"] = 14
    else:                                # newer CustomTkinter
        font_theme["family"] = FONT
        font_theme["size"] = 14
