import customtkinter as ctk

from anim import animate, ease_out_cubic, tween
from theme import (BORDER, BTN, FONT, GLOW, GREEN, GREEN_DIM, MUTED, PANEL,
                   PANEL2, RED)
from ui import badge, glow
from utils import load_icon, page_title

CARD_DEFS = [
    ("devices", "Devices", "device"),
    ("online", "RDP Reachable", "control"),
    ("tasks", "Local Tasks", "task"),
    ("alerts", "RDP Unreachable", "alert"),
]


class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.navigate = None
        self.refresh = None
        self._values = {}
        self._labels = {}
        self._colors = {}

        page_title(self, "Home", "home")

        intro = ctk.CTkFrame(self, fg_color="transparent")
        intro.pack(fill="x", padx=30)
        ctk.CTkLabel(intro, text="> command center overview", text_color=MUTED,
                     font=ctk.CTkFont(family=FONT, size=12)).pack(side="left")
        badge(intro, "REMOTE DESKTOP", GREEN_DIM).pack(side="right")

        # ---------------- stat cards ----------------
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(12, 8))

        for i, (key, caption, icon) in enumerate(CARD_DEFS):
            cards.grid_columnconfigure(i, weight=1, uniform="card")
            card = ctk.CTkFrame(cards, corner_radius=8, border_width=1,
                                border_color=BORDER, fg_color=PANEL)
            card.grid(row=0, column=i, padx=6, sticky="ew")
            glow(card, fg_idle=PANEL, fg_hot=PANEL2)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(12, 0))
            ctk.CTkLabel(top, text="", image=load_icon(icon, 18)).pack(side="left")
            ctk.CTkLabel(top, text=caption.upper(), text_color=MUTED,
                         font=ctk.CTkFont(family=FONT, size=10, weight="bold")
                         ).pack(side="left", padx=(8, 0))

            value = ctk.CTkLabel(card, text="0",
                                 font=ctk.CTkFont(family=FONT, size=30, weight="bold"),
                                 text_color=GREEN)
            value.pack(anchor="w", padx=14)
            self._labels[key] = value
            self._values[key] = 0
            self._colors[key] = GREEN

            ctk.CTkLabel(card, text="View details  ↗", text_color=GREEN_DIM,
                         font=ctk.CTkFont(family=FONT, size=10)
                         ).pack(anchor="w", padx=14, pady=(0, 10))

            target_page = "Task" if key == "tasks" else "Device"
            self._bind_card_action(card, target_page)

        # ---------------- chart + telemetry ----------------
        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=30, pady=(4, 8))
        lower.grid_columnconfigure(0, weight=3)
        lower.grid_columnconfigure(1, weight=2)
        lower.grid_rowconfigure(0, weight=1)

        chart_card = ctk.CTkFrame(lower, corner_radius=8, border_width=1,
                                  border_color=BORDER, fg_color=PANEL)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        chart_head = ctk.CTkFrame(chart_card, fg_color="transparent")
        chart_head.pack(fill="x", padx=14, pady=(10, 0))
        ctk.CTkLabel(chart_head, text="REMOTE SESSION CHECKLIST", text_color=GREEN,
                     font=ctk.CTkFont(family=FONT, size=11, weight="bold")
                     ).pack(side="left")
        steps = (
            ("01", "Install RustDesk on both PCs for cross-platform support."),
            ("02", "The person at the remote PC must approve the session."),
            ("03", "Use Windows RDP only with trusted accounts and networks."),
        )
        for number, text in steps:
            item = ctk.CTkFrame(chart_card, fg_color=PANEL2, corner_radius=6)
            item.pack(fill="x", padx=14, pady=(10, 0))
            ctk.CTkLabel(item, text=number, width=36, text_color=GREEN,
                         font=ctk.CTkFont(family=FONT, size=12, weight="bold")
                         ).pack(side="left", padx=(8, 2), pady=8)
            ctk.CTkLabel(item, text=text, text_color=MUTED, anchor="w",
                         font=ctk.CTkFont(family=FONT, size=11), wraplength=390,
                         justify="left").pack(side="left", fill="x", expand=True,
                                              padx=(4, 8), pady=8)

        telemetry = ctk.CTkFrame(lower, corner_radius=8, border_width=1,
                                 border_color=BORDER, fg_color=PANEL)
        telemetry.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(telemetry, text="LOCAL OVERVIEW", text_color=GREEN,
                     font=ctk.CTkFont(family=FONT, size=11, weight="bold")
                     ).pack(anchor="w", padx=16, pady=(12, 6))

        self._tele = {}
        for key, label in (("devices", "Saved connections"),
                           ("online", "RDP reachable"),
                           ("tasks", "Open tasks"), ("uptime", "App uptime")):
            row = ctk.CTkFrame(telemetry, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(row, text=label, text_color=MUTED,
                         font=ctk.CTkFont(family=FONT, size=12)
                         ).pack(side="left")
            value = ctk.CTkLabel(row, text="--", text_color=GREEN,
                                 font=ctk.CTkFont(family=FONT, size=12, weight="bold"))
            value.pack(side="right")
            self._tele[key] = value

        # ---------------- quick actions ----------------
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=30, pady=(0, 6))
        ctk.CTkLabel(actions, text="QUICK ACTIONS", text_color=MUTED,
                     font=ctk.CTkFont(family=FONT, size=10, weight="bold")
                     ).pack(side="left", padx=(0, 12))

        for text, page, icon in (("Connect a PC", "Device", "control"),
                                 ("New Task", "Task", "task"),
                                 ("Settings", "Settings", "settings")):
            btn = ctk.CTkButton(actions, text=text, image=load_icon(icon, 14),
                                compound="left", width=118, height=32,
                                fg_color=BTN, hover_color=PANEL2,
                                command=lambda p=page: self._go(p))
            glow(btn, idle=PANEL, hot=GLOW)
            btn.pack(side="left", padx=5)


    def _bind_card_action(self, widget, page):
        """Let the whole dashboard card act as a clear shortcut."""
        widget.bind("<Button-1>",
                    lambda _event, target=page: self._go(target), add="+")
        try:
            widget.configure(cursor="hand2")
        except Exception:
            pass
        for child in widget.winfo_children():
            self._bind_card_action(child, page)

    # ------------------------------------------------------------------
    def _go(self, page):
        if self.navigate:
            self.navigate(page)

    # ------------------------------------------------------------------
    def set_stats(self, stats):
        for key, _caption, _icon in CARD_DEFS:
            value = int(stats.get(key, 0))
            old = self._values.get(key, 0)
            label = self._labels[key]
            self._values[key] = value

            if old != value:
                animate(self, 520,
                        lambda t, l=label, a=old, b=value:
                        l.configure(text=str(int(round(a + (b - a) * t)))),
                        ease=ease_out_cubic, key=f"stat-{key}")

            target = RED if (key == "alerts" and value) else GREEN
            if target != self._colors[key]:
                tween(label, "text_color", self._colors[key], target, 250,
                      key="stat-color")
                self._colors[key] = target

        self._tele["uptime"].configure(text=self._fmt_uptime(stats.get("uptime", 0)))
        self._tele["devices"].configure(text=str(stats.get("devices", 0)))
        self._tele["online"].configure(text=str(stats.get("online", 0)))
        self._tele["tasks"].configure(text=str(stats.get("tasks", 0)))

    @staticmethod
    def _fmt_uptime(seconds):
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

