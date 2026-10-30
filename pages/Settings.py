import customtkinter as ctk

import anim
from theme import (BORDER, FONT, GLOW, GREEN, GREEN_DIM, MUTED, PANEL,
                   PANEL2)
from ui import badge, glow, hline, switch_row, toast
from utils import page_title

SHORTCUTS = (
    ("Ctrl + 1 … 3", "jump straight to a page"),
    ("Ctrl + K", "focus the terminal"),
    ("Tab", "autocomplete command / page"),
    ("Up / Down", "walk through history"),
    ("Enter", "run the command"),
    ("Esc", "clear the terminal input"),
)


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.app = None

        page_title(self, "Settings", "settings")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(0, 24))
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # ---------------- preferences ----------------
        panel = ctk.CTkFrame(content, corner_radius=8, border_width=1,
                             border_color=BORDER, fg_color=PANEL)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.anim_switch = switch_row(
            panel, "Animations",
            "page slides, glows, counters and typing effects",
            True, self._toggle_animations, row=0)

        self.notif_switch = switch_row(
            panel, "Notifications",
            "show toast messages in the bottom-right corner",
            True, self._toggle_notifications, row=1)

        self.term_switch = switch_row(
            panel, "Show terminal",
            "keep the console expanded below the page",
            True, self._toggle_terminal, row=2)

        self.auto_switch = switch_row(
            panel, "Start with system",
            "not wired in this build",
            False, self._toggle_autostart, row=3)

        ctk.CTkFrame(panel, height=1, corner_radius=0,
                     fg_color=BORDER).grid(row=4, column=0, columnspan=2,
                                           sticky="ew", padx=20, pady=(14, 0))

        accent = ctk.CTkFrame(panel, fg_color="transparent")
        accent.grid(row=5, column=0, columnspan=2, sticky="ew",
                    padx=20, pady=(10, 18))

        left = ctk.CTkFrame(accent, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="Accent color",
                     font=ctk.CTkFont(family=FONT, size=14)).pack(anchor="w")
        ctk.CTkLabel(left, text="#58E0AD · mint terminal green",
                     text_color=MUTED,
                     font=ctk.CTkFont(family=FONT, size=11)).pack(anchor="w")

        swatch = ctk.CTkLabel(accent, text="", width=48, height=24,
                              corner_radius=4, fg_color=GREEN)
        glow(swatch, idle=GREEN_DIM, hot=GLOW)
        swatch.pack(side="right")

        # ---------------- keyboard cheatsheet ----------------
        tips = ctk.CTkFrame(content, corner_radius=8, border_width=1,
                            border_color=BORDER, fg_color=PANEL)
        tips.grid(row=0, column=1, sticky="nsew")

        head = ctk.CTkFrame(tips, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(head, text="KEYBOARD", text_color=GREEN,
                     font=ctk.CTkFont(family=FONT, size=11, weight="bold")
                     ).pack(side="left")
        badge(head, "HANDY", GREEN_DIM).pack(side="right")

        ctk.CTkLabel(tips, text="Every action is one keystroke away.",
                     text_color=MUTED,
                     font=ctk.CTkFont(family=FONT, size=11)
                     ).pack(anchor="w", padx=16)

        for keys, what in SHORTCUTS:
            row = ctk.CTkFrame(tips, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(row, text=keys, width=96, anchor="w",
                         text_color=GREEN_DIM,
                         font=ctk.CTkFont(family=FONT, size=12, weight="bold")
                         ).pack(side="left")
            ctk.CTkLabel(row, text=what, text_color=MUTED,
                         font=ctk.CTkFont(family=FONT, size=12)
                         ).pack(side="left")

        hline(tips, padx=16, pady=(10, 8))

        ctk.CTkLabel(tips, text="Try the console:  help · status · devices",
                     text_color=GREEN_DIM,
                     font=ctk.CTkFont(family=FONT, size=11)
                     ).pack(anchor="w", padx=16)
        ctk.CTkLabel(tips, text="DeepTracker · neon terminal edition",
                     text_color=MUTED,
                     font=ctk.CTkFont(family=FONT, size=10)
                     ).pack(anchor="w", padx=16, pady=(2, 14))

    # ==================================================================
    def _notify(self, text, kind="info"):
        if self.notif_switch.get():
            toast(self.winfo_toplevel(), text, kind)

    def _toggle_animations(self):
        anim.ANIMATIONS = bool(self.anim_switch.get())
        toast(self.winfo_toplevel(),
              "Animations enabled" if anim.ANIMATIONS else "Animations disabled",
              "info")

    def _toggle_notifications(self):
        if self.app is not None:
            self.app._notifications_enabled = bool(self.notif_switch.get())
        if self.notif_switch.get():
            toast(self.winfo_toplevel(), "Notifications enabled", "info")

    def _toggle_terminal(self):
        if self.app is not None:
            self.app.terminal.set_visible(bool(self.term_switch.get()))

    def _toggle_autostart(self):
        if self.auto_switch.get():
            self.auto_switch.deselect()
            self._notify("Autostart is not available in this build", "warn")
