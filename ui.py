"""Shared look & feel helpers: hover glow, reveal, badges, toasts."""

import customtkinter as ctk

from anim import animate, lerp_color, tween
from theme import (BG, BORDER, GLOW, GREEN, MUTED, PANEL, PANEL2, RED, FONT)


def glow(widget, idle=PANEL, hot=GLOW, ms=150, fg_idle=None, fg_hot=None):
    """Animated border highlight on hover (optionally also the fill)."""
    widget.configure(border_width=1, border_color=idle)

    def pointer_inside(event):
        x, y = widget.winfo_rootx(), widget.winfo_rooty()
        return (x <= event.x_root < x + widget.winfo_width()
                and y <= event.y_root < y + widget.winfo_height())

    def on_enter(_event):
        tween(widget, "border_color", idle, hot, ms, key="glow")
        if fg_idle and fg_hot:
            tween(widget, "fg_color", fg_idle, fg_hot, ms, key="glow-fg")

    def on_leave(event):
        if pointer_inside(event):
            return
        tween(widget, "border_color", hot, idle, ms, key="glow")
        if fg_idle and fg_hot:
            tween(widget, "fg_color", fg_hot, fg_idle, ms, key="glow-fg")

    widget.bind("<Enter>", on_enter, add="+")
    widget.bind("<Leave>", on_leave, add="+")
    return widget


def reveal(widget, idle=PANEL, color=BORDER, delay=0, ms=340):
    """Fade a row/card border in, so lists feel like they slide into place."""
    try:
        widget.configure(border_color=idle)
    except Exception:
        return

    def start():
        tween(widget, "border_color", idle, color, ms, key="reveal")

    if delay:
        widget.after(delay, start)
    else:
        start()


def badge(parent, text, color, text_color=None):
    return ctk.CTkLabel(
        parent, text=f"  {text}  ", text_color=text_color or color,
        fg_color=PANEL2, corner_radius=4, border_width=1, border_color=color,
        font=ctk.CTkFont(family=FONT, size=11, weight="bold"),
    )


def empty_state(parent, text, icon="alert", pad=30):
    return ctk.CTkLabel(
        parent, text=f"  {text}", text_color=MUTED,
        font=ctk.CTkFont(family=FONT, size=13),
        image=None,
    )


def ambient_background(widget):
    """Add a subtle grid and network motif to transparent CustomTkinter frames."""
    if isinstance(widget, ctk.CTkFrame):
        try:
            transparent = widget.cget("fg_color") == "transparent"
            canvas = widget._canvas
        except Exception:
            transparent = False
            canvas = None

        if transparent and canvas is not None:
            def draw(_event=None):
                try:
                    if not canvas.winfo_exists():
                        return
                    width, height = canvas.winfo_width(), canvas.winfo_height()
                    if width < 2 or height < 2:
                        return
                    canvas.delete("ambient-background")
                    for x in range(28, width, 56):
                        canvas.create_line(
                            x, 0, x, height, fill="#0d1b25",
                            tags="ambient-background")
                    for y in range(28, height, 56):
                        canvas.create_line(
                            0, y, width, y, fill="#0d1b25",
                            tags="ambient-background")

                    cx, cy = width * 0.86, height * 0.82
                    for radius, color in ((72, "#10232d"), (116, "#10212b"),
                                          (164, "#0f1e28")):
                        canvas.create_oval(
                            cx - radius, cy - radius, cx + radius, cy + radius,
                            outline=color, width=1, tags="ambient-background")

                    points = ((0.28, 0.30), (0.40, 0.38), (0.53, 0.33),
                              (0.65, 0.45), (0.77, 0.37), (0.88, 0.51),
                              (0.61, 0.58))
                    links = ((0, 1), (1, 2), (2, 3), (3, 4),
                             (4, 5), (3, 6), (6, 4))
                    coords = [(width * x, height * y) for x, y in points]
                    for start, end in links:
                        x1, y1 = coords[start]
                        x2, y2 = coords[end]
                        canvas.create_line(
                            x1, y1, x2, y2, fill="#122630",
                            tags="ambient-background")
                    for index, (x, y) in enumerate(coords):
                        radius = 3 if index % 3 == 0 else 2
                        color = "#285243" if index % 3 == 0 else "#1a3540"
                        canvas.create_oval(
                            x - radius, y - radius, x + radius, y + radius,
                            fill=color, outline="", tags="ambient-background")
                except Exception:
                    return

            canvas.bind("<Configure>",
                        lambda event, frame=widget: frame.after_idle(draw),
                        add="+")
            widget.after_idle(draw)

    for child in widget.winfo_children():
        ambient_background(child)


def toast(master, text, kind="info", ms=2200):
    """Small notification that slides up from the bottom-right corner."""
    try:
        if not getattr(master.winfo_toplevel(), "_notifications_enabled", True):
            return None
    except Exception:
        pass
    color = {"info": GREEN, "warn": "#ffd24a", "error": RED}.get(kind, GREEN)

    old = getattr(master, "_toast", None)
    if old is not None:
        try:
            old.destroy()
        except Exception:
            pass

    frame = ctk.CTkFrame(master, fg_color=PANEL2, corner_radius=8,
                         border_width=1, border_color=color)
    frame.place(relx=0.985, rely=1.02, anchor="se")

    ctk.CTkLabel(frame, text="●", text_color=color,
                 font=ctk.CTkFont(family=FONT, size=12)).pack(
        side="left", padx=(12, 6), pady=10)
    ctk.CTkLabel(frame, text=text, text_color=GREEN,
                 font=ctk.CTkFont(family=FONT, size=12)).pack(
        side="left", padx=(0, 16), pady=10)

    frame.lift()
    master._toast = frame

    animate(frame, 240, lambda t: frame.place_configure(rely=1.02 - 0.09 * t),
            key="toast-in")

    def close(_event=None):
        if not frame.winfo_exists():
            return
        animate(frame, 200,
                lambda t: frame.place_configure(rely=0.93 + 0.09 * t),
                on_done=lambda: frame.winfo_exists() and frame.destroy(),
                key="toast-out")

    frame.bind("<Button-1>", close)
    frame.after(ms, close)
    return frame


def hline(parent, padx=0, pady=0, color=None):
    return ctk.CTkFrame(parent, height=1, corner_radius=0,
                        fg_color=color or BORDER).pack(
        fill="x", padx=padx, pady=pady)


def switch_row(parent, label, hint="", value=True, command=None,
               row=0, pad=20):
    """Label + muted hint on the left, switch on the right. Returns the switch."""
    left = ctk.CTkFrame(parent, fg_color="transparent")
    left.grid(row=row, column=0, sticky="w", padx=pad, pady=10)

    ctk.CTkLabel(left, text=label,
                 font=ctk.CTkFont(family=FONT, size=14)).pack(anchor="w")
    if hint:
        ctk.CTkLabel(left, text=hint, text_color=MUTED,
                     font=ctk.CTkFont(family=FONT, size=11)).pack(anchor="w")

    sw = ctk.CTkSwitch(parent, text="", command=command)
    sw.grid(row=row, column=1, sticky="e", padx=pad, pady=10)
    if value:
        sw.select()
    else:
        sw.deselect()
    parent.grid_columnconfigure(0, weight=1)
    return sw
