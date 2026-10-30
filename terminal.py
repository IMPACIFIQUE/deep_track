import datetime
import difflib
import getpass

import customtkinter as ctk

from anim import ANIMATIONS, animate, tween
from theme import (BORDER, ENTRY, FONT, GLOW, GREEN, GREEN_DIM, HOVER, MUTED,
                   PANEL, RED)
from utils import load_icon

COMMANDS = [
    "help", "pages", "open", "time", "clear", "status", "devices",
    "tasks", "uptime", "whoami", "echo", "banner",
]

BANNER = (
    "  ____                 _____             _             \n"
    " |  _ \\  ___  ___ _ __|_   _| _ __ __ _  ___| | _____ _ __ \n"
    " | | | |/ _ \\/ _ \\ '_ \\ | || '__/ _` |/ __| |/ / _ \\ '__|\n"
    " | |_| |  __/  __/ |_) || || | | (_| | (__|   <  __/ |   \n"
    " |____/ \\___|\\___| .__/ |_||_|  \\__,_|\\___|_|\\_\\___|_|   \n"
    "                 |_|   remote support console"
)


class Terminal(ctk.CTkFrame):
    def __init__(self, master, navigate=None, page_names=None):
        super().__init__(master, corner_radius=8, border_width=1,
                         border_color=BORDER)
        self.navigate = navigate
        self.page_names = page_names or []
        self.stats = None
        self.devices = None
        self.notify = None

        self.history = []
        self.hist_i = 0
        self.collapsed = False

        self._queue = []
        self._typing = False
        self._gen = 0

        # ---- header ----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(8, 0))

        ctk.CTkLabel(
            header, text=" TERMINAL", image=load_icon("hacking", 16),
            compound="left",
            font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
        ).pack(side="left")

        self.collapse_btn = ctk.CTkButton(
            header, text="▾", width=30, height=26,
            fg_color="transparent", hover_color=HOVER,
            command=self.toggle,
        )
        self.collapse_btn.pack(side="right")

        ctk.CTkButton(
            header, text="Clear", width=60, height=26,
            fg_color="transparent", hover_color=HOVER,
            text_color=GREEN, command=self.clear,
        ).pack(side="right", padx=4)

        # ---- content ----
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="x", padx=12, pady=(6, 12))

        self.output = ctk.CTkTextbox(
            self.content, height=120, fg_color=ENTRY, text_color=GREEN,
            font=ctk.CTkFont(family=FONT, size=13), state="disabled",
            border_width=1, border_color=BORDER,
        )
        self.output.pack(fill="x")

        self.entry = ctk.CTkEntry(
            self.content, placeholder_text="$ type a command (try: help)",
            font=ctk.CTkFont(family=FONT, size=13), height=34,
        )
        self.entry.pack(fill="x", pady=(8, 0))
        self.entry.bind("<Return>", self.run)
        self.entry.bind("<Up>", self.prev_cmd)
        self.entry.bind("<Down>", self.next_cmd)
        self.entry.bind("<Tab>", self.complete)
        self.entry.bind("<FocusIn>", lambda e: tween(
            self, "border_color", BORDER, GLOW, 160, key="term-focus"))
        self.entry.bind("<FocusOut>", lambda e: tween(
            self, "border_color", GLOW, BORDER, 200, key="term-focus"))

        self.bind("<Button-1>", lambda e: self.entry.focus_set())

        self.write("DeepTracker console ready. Type 'help'.", instant=True)

    # ==================================================================
    #  output (typewriter)
    # ==================================================================
    def write(self, text, instant=False):
        """Queue one or more lines for the console."""
        for line in str(text).splitlines() or [""]:
            self._queue.append((line, instant))
        if len(self._queue) > 120:
            self._queue = self._queue[-120:]
        if not self._typing:
            self._type_next()

    def _type_next(self):
        if not self._queue:
            self._typing = False
            return

        text, instant = self._queue.pop(0)
        self._typing = True
        gen = self._gen

        if instant or not ANIMATIONS:
            self._emit(text)
            self.after(12, self._type_next)
            return

        self._type_line(text, 0, gen)

    def _type_line(self, text, i, gen):
        if gen != self._gen or not self.winfo_exists():
            self._typing = False
            return

        if i == 0:
            self._insert("")
        if i < len(text):
            self._insert(text[i:i + 2])
            self.after(9, lambda: self._type_line(text, i + 2, gen))
        else:
            self._insert("\n")
            self.after(22, self._type_next)

    def _insert(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _emit(self, text):
        self._insert(f"{text}\n")

    def clear(self):
        self._gen += 1
        self._typing = False
        self._queue.clear()
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    # ==================================================================
    #  collapse / expand
    # ==================================================================
    def toggle(self):
        if self.collapsed:
            self.collapsed = False
            self.content.pack(fill="x", padx=12, pady=(6, 12))
            self.output.configure(height=1)
            animate(self.output, 180,
                    lambda t: self.output.configure(height=max(1, int(120 * t))),
                    key="term-height")
            self.collapse_btn.configure(text="▾")
        else:
            self.collapsed = True
            start = max(1, self.output.winfo_height())
            animate(self.output, 150,
                    lambda t: self.output.configure(height=max(1, int(start * (1 - t)))),
                    on_done=self.content.pack_forget, key="term-height")
            self.collapse_btn.configure(text="▸")

    def set_visible(self, visible):
        if visible == (not self.collapsed):
            return
        self.toggle()

    # ==================================================================
    #  command history
    # ==================================================================
    def prev_cmd(self, event=None):
        if self.history and self.hist_i > 0:
            self.hist_i -= 1
            self._set_entry(self.history[self.hist_i])
        return "break"

    def next_cmd(self, event=None):
        if self.hist_i < len(self.history) - 1:
            self.hist_i += 1
            self._set_entry(self.history[self.hist_i])
        else:
            self.hist_i = len(self.history)
            self._set_entry("")
        return "break"

    def _set_entry(self, text):
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self.entry.icursor("end")

    # ==================================================================
    #  tab completion
    # ==================================================================
    def complete(self, event=None):
        text = self.entry.get()

        if " " in text:
            head, _, arg = text.partition(" ")
            if head.lower() == "open":
                matches = [p for p in self.page_names
                           if p.lower().startswith(arg.lower())]
                if len(matches) == 1:
                    self._set_entry(f"open {matches[0].lower()}")
                elif matches:
                    self.write("  " + "   ".join(matches), instant=True)
            return "break"

        matches = [c for c in COMMANDS if c.startswith(text.lower())]
        if len(matches) == 1:
            self._set_entry(matches[0] + " ")
        elif matches:
            self.write("  " + "   ".join(matches), instant=True)
        return "break"

    # ==================================================================
    #  commands
    # ==================================================================
    def run(self, event=None):
        cmd = self.entry.get().strip()
        if not cmd:
            return "break"

        self.history.append(cmd)
        self.hist_i = len(self.history)
        self.entry.delete(0, "end")
        self.write(f"$ {cmd}", instant=True)

        name, _, arg = cmd.partition(" ")
        name, arg = name.lower(), arg.strip()

        handler = getattr(self, f"_cmd_{name}", None)
        if handler is not None:
            handler(arg)
            return "break"

        close = difflib.get_close_matches(name, COMMANDS, n=1)
        hint = f" — did you mean '{close[0]}'?" if close else " (type 'help')"
        self.write(f"  command not found: {name}{hint}")
        if self.notify:
            self.notify(f"Unknown command: {name}", "error")
        return "break"

    # ------------------------------------------------------------------
    def _cmd_help(self, arg):
        rows = [
            ("help", "show this list"),
            ("pages", "list all pages"),
            ("open <page>", "go to a page (example: open task)"),
            ("status", "local connection + task summary"),
            ("devices", "list saved connection shortcuts"),
            ("tasks", "task counts"),
            ("uptime", "how long the console has been up"),
            ("time", "current date and time"),
            ("whoami", "current operator"),
            ("echo <text>", "print text back"),
            ("banner", "print the console banner"),
            ("clear", "clear the terminal"),
        ]
        for cmd, what in rows:
            self.write(f"  {cmd:<14}{what}", instant=True)

    def _cmd_pages(self, arg):
        self.write("  " + "   ".join(self.page_names))

    def _cmd_open(self, arg):
        match = next((p for p in self.page_names if p.lower() == arg.lower()), None)
        if match is None:
            match = next((p for p in self.page_names
                          if p.lower().startswith(arg.lower())), None) if arg else None
        if match and self.navigate:
            self.navigate(match)
            self.write(f"  opened {match}")
        else:
            self.write(f"  unknown page: '{arg}' (type 'pages')")
            if self.notify:
                self.notify(f"Unknown page: {arg or '(empty)'}", "error")

    def _cmd_time(self, arg):
        self.write("  " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _cmd_status(self, arg):
        stats = self.stats() if self.stats else {}
        self.write(f"  devices  : {stats.get('online', 0)} online / "
                   f"{stats.get('devices', 0)} total")
        self.write(f"  tasks    : {stats.get('tasks', 0)} open / "
                   f"{stats.get('done', 0)} done")
        self.write(f"  uptime   : {self._fmt_uptime(stats.get('uptime', 0))}")

    def _cmd_devices(self, arg):
        devices = self.devices() if self.devices else []
        if not devices:
            self.write("  no devices registered")
            return
        for device in devices:
            if device.get("connection_type") == "RustDesk":
                mark, status = "◈", "RustDesk ID saved"
            else:
                mark = "●" if device["online"] is True else "○"
                status = "RDP port open" if device["online"] is True else (
                    "unreachable" if device["online"] is False else "not checked")
            self.write(f"  {mark} {device['name']:<20}{status}")

    def _cmd_tasks(self, arg):
        stats = self.stats() if self.stats else {}
        self.write(f"  open: {stats.get('tasks', 0)}   "
                   f"done: {stats.get('done', 0)}")

    def _cmd_uptime(self, arg):
        stats = self.stats() if self.stats else {}
        self.write("  uptime " + self._fmt_uptime(stats.get("uptime", 0)))

    def _cmd_whoami(self, arg):
        self.write(f"  local Windows user: {getpass.getuser()}")

    def _cmd_echo(self, arg):
        self.write(f"  {arg}")

    def _cmd_banner(self, arg):
        for line in BANNER.splitlines():
            self.write(line, instant=True)

    def _cmd_clear(self, arg):
        self.clear()

    @staticmethod
    def _fmt_uptime(seconds):
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
