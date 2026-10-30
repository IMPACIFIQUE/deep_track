import datetime
import os
import time

import tkinter as tk

import customtkinter as ctk

from anim import animate, cancel, ease_out_cubic, pulse, tween
from theme import (ACTIVE, BG, BORDER, ENTRY, GLOW, GREEN, GREEN_DIM, HOVER,
                   MUTED, PANEL, PANEL2, RED, apply_theme)
from terminal import Terminal
from ui import ambient_background, glow, reveal, toast
from utils import ICON_DIR, load_brand_icon, load_icon

from pages.Home import HomePage
from pages.Task import TaskPage
from pages.Device import DevicePage
from pages.Settings import SettingsPage

# Links in the TOP bar (label, page class, icon)
TOP_PAGES = [
    ("Home", HomePage, "home"),
    ("Task", TaskPage, "task"),
    ("Settings", SettingsPage, "settings"),
]


class DeepTrackerApp(ctk.CTk):
    def __init__(self):
        apply_theme()
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title("DeepTracker")
        self.geometry("1250x800+2+2")
        self.minsize(1080, 700)
        self.after(40, self._fit_to_screen)

        ico = os.path.join(ICON_DIR, "app.ico")
        if os.path.exists(ico):
            self.after(200, lambda: self.iconbitmap(ico))

        self.buttons = {}
        self.pages = {}
        self.current = None
        self.icons = {}
        self._snapshot = None
        self.devices_open = True
        self._started = time.time()
        self._nav_fg = {}
        self._ind_x = 0.0
        self._ind_w = 0.0
        self._toast = None
        self._booting = False
        self._notifications_enabled = True

        self._build_topbar()
        self._build_aside()
        self._build_pages()
        self._wire()
        self._bind_shortcuts()

        self.show_page("Home", animated=False)
        self.refresh_devices()
        self._tick()

        self._boot()
        self.after(1900, lambda: toast(self, "All systems online", "info", 1800))

    # ==================================================================
    #  screen fit
    # ==================================================================
    def _fit_to_screen(self):
        """Shrink the whole UI when the display is smaller than the design."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        try:
            from customtkinter.windows.widgets.scaling.scaling_tracker import (
                ScalingTracker,
            )
            dpi = ScalingTracker.get_window_dpi_scaling(self) or 1.0
        except Exception:
            dpi = 1.0

        # Tk reports virtualized pixels when the process is DPI-unaware,
        # so the real desktop is (logical size * dpi scaling).
        physical_w = screen_w * dpi
        physical_h = screen_h * dpi

        target = min(1.25, (physical_w - 24) / 1250, (physical_h - 100) / 800)
        factor = max(0.35, target / dpi)

        if factor < 0.995:
            ctk.set_window_scaling(factor)
            ctk.set_widget_scaling(factor)
            self.geometry("1250x800+2+2")

    # ==================================================================
    #  layout
    # ==================================================================
    def _build_topbar(self):
        self.topbar = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.topbar.pack(side="top", fill="x")
        self.topbar.pack_propagate(False)

        brand_group = ctk.CTkFrame(self.topbar, fg_color="transparent")
        brand_group.pack(side="left", padx=(18, 10), pady=7)
        self.brand_icon = load_brand_icon(32)
        ctk.CTkLabel(brand_group, text="", image=self.brand_icon,
                     width=32, height=32).pack(side="left", padx=(0, 9))
        brand_copy = ctk.CTkFrame(brand_group, fg_color="transparent")
        brand_copy.pack(side="left")
        self.brand = ctk.CTkLabel(
            brand_copy, text="DeepTracker",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=GREEN,
        )
        self.brand.pack(anchor="w")
        ctk.CTkLabel(brand_copy, text="DEVICE CONSOLE", text_color=MUTED,
                     font=ctk.CTkFont(size=9, weight="bold")).pack(anchor="w")
        pulse(self.brand, "text_color", GREEN, GLOW, period=4200, key="brand")

        first = True
        for label, _page_class, icon_name in TOP_PAGES:
            self.icons[label] = load_icon(icon_name)
            btn = ctk.CTkButton(
                self.topbar, text=label, image=self.icons[label], compound="left",
                width=126, height=36,
                fg_color=PANEL, text_color=GREEN,
                hover_color=HOVER,
                command=lambda name=label: self.show_page(name),
            )
            glow(btn)
            left_margin = 16 if first else 3
            first = False
            btn.pack(side="left", padx=(left_margin, 3), pady=12)
            self.buttons[label] = btn
            self._nav_fg[label] = PANEL

        # ---- live status (right side) ----
        status = ctk.CTkFrame(self.topbar, fg_color="transparent")
        status.pack(side="right", padx=(0, 18))

        self.dot = ctk.CTkLabel(status, text="●", text_color=GREEN,
                                font=ctk.CTkFont(size=14))
        self.dot.pack(side="left")
        pulse(self.dot, "text_color", GREEN, GREEN_DIM, period=1700, key="dot")

        ctk.CTkLabel(status, text="READY", text_color=MUTED,
                     font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=(5, 14))

        self.clock = ctk.CTkLabel(status, text="--:--:--", text_color=GREEN_DIM,
                                  font=ctk.CTkFont(size=12))
        self.clock.pack(side="left")

        # Settings sits on the far right, after the status block
        settings_btn = self.buttons["Settings"]
        settings_btn.pack_forget()
        settings_btn.pack(side="right", padx=(0, 18), pady=12)

        # ---- sliding active-tab indicator (created last = on top) ----
        # plain tk.Frame: this CustomTkinter build forbids width/height in place()
        self.nav_indicator = tk.Frame(self.topbar, bg=GREEN, height=2,
                                      highlightthickness=0, bd=0)
        self.nav_indicator.place(x=0, y=55, width=0, height=2)

        self.topbar.bind("<Configure>", lambda e: self._move_indicator(
            self.buttons.get(self.current), animated=False))

        # green line under the top bar
        ctk.CTkFrame(self, height=2, corner_radius=0,
                     fg_color=BORDER).pack(side="top", fill="x")

    def _build_aside(self):
        middle = ctk.CTkFrame(self, fg_color="transparent")
        middle.pack(side="top", fill="both", expand=True)

        self.aside = ctk.CTkFrame(middle, width=220, corner_radius=0)
        self.aside.pack(side="left", fill="y")
        self.aside.pack_propagate(False)

        head = ctk.CTkFrame(self.aside, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(20, 3))

        self.icons["Device"] = load_icon("device")
        self.buttons["Device"] = ctk.CTkButton(
            head, text="Device", image=self.icons["Device"], compound="left",
            anchor="w", height=40,
            fg_color=PANEL, text_color=GREEN, hover_color=HOVER,
            command=lambda: self.show_page("Device"),
        )
        glow(self.buttons["Device"])
        self.buttons["Device"].pack(side="left", fill="x", expand=True)
        self._nav_fg["Device"] = PANEL

        self.chev = ctk.CTkButton(
            head, text="▾", width=34, height=40,
            fg_color="transparent", hover_color=HOVER, text_color=GREEN,
            command=self.toggle_devices,
        )
        self.chev.configure(hover=False)
        self.chev.pack(side="right", padx=(3, 0))

        self.device_list = ctk.CTkFrame(self.aside, fg_color="transparent")
        self.device_list.pack(fill="x", padx=(30, 10))

        # body: terminal at the bottom, pages above
        self.body = ctk.CTkFrame(middle, fg_color="transparent")
        self.body.pack(side="right", fill="both", expand=True)

        self.terminal = Terminal(self.body)
        self.terminal.pack(side="bottom", fill="x", padx=30, pady=(0, 18))

        self.container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)

    def _build_pages(self):
        self.pages["Device"] = DevicePage(self.container)
        for label, page_class, _icon in TOP_PAGES:
            self.pages[label] = page_class(self.container)
        for page in self.pages.values():
            ambient_background(page)

    def _wire(self):
        self.terminal.navigate = self.show_page
        self.terminal.page_names = list(self.pages.keys())
        self.terminal.stats = self._stats
        self.terminal.devices = lambda: self.pages["Device"].devices
        self.terminal.notify = lambda text, kind="info": toast(self, text, kind)

        self.pages["Home"].navigate = self.show_page
        self.pages["Settings"].app = self

    def _bind_shortcuts(self):
        for i, (_label, _cls, _icon) in enumerate(TOP_PAGES, start=1):
            name = _label
            self.bind(f"<Control-Key-{i}>", lambda e, n=name: self.show_page(n))
        self.bind("<Control-Key-k>", lambda e: self.terminal.entry.focus_set())
        self.bind("<Escape>", lambda e: self.terminal.entry.delete(0, "end"))

    # ==================================================================
    #  navigation
    # ==================================================================
    def show_page(self, name, animated=True):
        if name not in self.pages:
            return
        if name == self.current:
            return

        previous = self.current
        order = list(self.pages)
        direction = 1
        if previous is not None:
            direction = 1 if order.index(name) >= order.index(previous) else -1
            # stop a slide that may still be running, otherwise its next frame
            # would place the old page again after we hide it
            cancel(self.pages[previous], "page-slide")
            self.pages[previous].place_forget()

        page = self.pages[name]
        cancel(page, "page-slide")
        page.lift()

        if animated:
            offset = 0.018 * direction
            page.place(relx=offset, rely=0, relwidth=1, relheight=1)
            animate(page, 240,
                    lambda t: page.place_configure(relx=offset * (1 - t)),
                    ease=ease_out_cubic, key="page-slide")
        else:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.current = name
        self._update_nav(name)
        self._move_indicator(self.buttons.get(name), animated=animated)

    def _update_nav(self, name):
        for label, btn in self.buttons.items():
            start = self._nav_fg.get(label, PANEL)
            end = ACTIVE if label == name else PANEL
            if start == end:
                continue
            self._nav_fg[label] = end
            tween(btn, "fg_color", start, end, 240, key="nav-fg")

    def _move_indicator(self, btn, animated=True):
        if btn is None or not btn.winfo_exists():
            return
        self.topbar.update_idletasks()
        x = btn.winfo_x() + 8
        width = max(18, btn.winfo_width() - 16)
        x0, w0 = self._ind_x, self._ind_w
        self._ind_x, self._ind_w = x, width

        if not animated:
            self.nav_indicator.place_configure(x=x, width=width)
            return

        animate(self.nav_indicator, 260,
                lambda t: self.nav_indicator.place_configure(
                    x=x0 + (x - x0) * t, width=w0 + (width - w0) * t),
                key="indicator")

    # ==================================================================
    #  aside device list
    # ==================================================================
    def toggle_devices(self):
        self.devices_open = not self.devices_open
        if self.devices_open:
            self.device_list.pack(fill="x", padx=(30, 10))
            self.chev.configure(text="▾")
        else:
            self.device_list.pack_forget()
            self.chev.configure(text="▸")

    def refresh_devices(self):
        """Keep the aside list in sync with the Device page (checks every second)."""
        devices = self.pages["Device"].devices
        snapshot = [(d["name"], d["online"]) for d in devices]
        if snapshot != self._snapshot:
            self._snapshot = snapshot
            for w in self.device_list.winfo_children():
                w.destroy()
            if not snapshot:
                ctk.CTkLabel(
                    self.device_list, text="No devices yet", text_color=MUTED
                ).pack(anchor="w", pady=4)
            for name, online in snapshot:
                row = ctk.CTkFrame(self.device_list, fg_color="transparent")
                row.pack(fill="x", pady=2)
                dot = ctk.CTkLabel(
                    row, text="●", width=16,
                    text_color=GREEN if online is True else
                    RED if online is False else MUTED,
                )
                dot.pack(side="left")
                ctk.CTkLabel(row, text=name, anchor="w").pack(side="left", padx=4)
                reveal(row)
        self.after(1000, self.refresh_devices)

    # ==================================================================
    #  live stats
    # ==================================================================
    def _stats(self):
        devices = self.pages["Device"].devices
        tasks = self.pages["Task"].tasks
        online = sum(1 for d in devices
                     if d.get("connection_type") == "Windows RDP"
                     and d["online"] is True)
        return {
            "devices": len(devices),
            "online": online,
            "tasks": sum(1 for t in tasks if not t["done"]),
            "done": sum(1 for t in tasks if t["done"]),
            "alerts": sum(1 for d in devices
                          if d.get("connection_type") == "Windows RDP"
                          and d["online"] is False),
            "uptime": int(time.time() - self._started),
        }

    def _tick(self):
        stats = self._stats()
        self.pages["Home"].set_stats(stats)
        checked_rdp = [d for d in self.pages["Device"].devices
                       if d.get("connection_type") == "Windows RDP"
                       and d["online"] is not None]
        self.dot.configure(text_color=GREEN if not checked_rdp or
                           any(d["online"] is True for d in checked_rdp) else RED)
        self.clock.configure(text=datetime.datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick)

    # ==================================================================
    #  boot overlay
    # ==================================================================
    def _boot(self):
        self._booting = True
        overlay = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()

        box = ctk.CTkFrame(overlay, fg_color="transparent")
        box.place(relx=0.5, rely=0.46, anchor="center")

        ctk.CTkLabel(box, text="DeepTracker",
                     font=ctk.CTkFont(size=46, weight="bold"),
                     text_color=GREEN).pack()
        ctk.CTkLabel(box, text="SECURE DEVICE CONSOLE  //  v1.0",
                     text_color=MUTED,
                     font=ctk.CTkFont(size=11)).pack(pady=(0, 20))

        log = ctk.CTkTextbox(box, width=440, height=92, fg_color=ENTRY,
                             border_width=1, border_color=BORDER,
                             text_color=GREEN, font=ctk.CTkFont(size=12))
        log.pack()

        bar = ctk.CTkProgressBar(box, width=440, height=4,
                                 progress_color=GREEN, fg_color=PANEL2)
        bar.set(0)
        bar.pack(pady=(12, 0))

        lines = [
            "starting DeepTracker .... ok",
            "loading saved connections  ok",
            "preparing dashboard ...... ok",
            "checking local settings .. ok",
        ]
        state = {"done": False}

        def finish(_event=None):
            if state["done"]:
                return
            state["done"] = True
            self._booting = False
            animate(overlay, 280,
                    lambda t: overlay.place_configure(rely=-1.0 * t),
                    on_done=lambda: overlay.winfo_exists() and overlay.destroy(),
                    key="boot-out")

        def step(i=0):
            if state["done"]:
                return
            if i < len(lines):
                log.insert("end", f"> {lines[i]}\n")
                log.see("end")
                bar.set((i + 1) / len(lines))
                overlay.after(140, lambda: step(i + 1))
            else:
                bar.set(1)
                overlay.after(220, finish)

        overlay.bind("<Button-1>", finish)
        overlay.after(140, step)


if __name__ == "__main__":
    DeepTrackerApp().mainloop()
