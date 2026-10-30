import customtkinter as ctk

from anim import animate, ease_out_cubic, lerp_color, tween
from theme import (BORDER, BTN, FONT, GREEN, GREEN_DIM, MUTED, PANEL, PANEL2,
                   RED, RED_BTN, RED_HOVER, TRACK)
from ui import glow, reveal, toast
from utils import load_icon, page_title


class TaskPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.tasks = []          # {text, done, row, box, color}
        self.filter_mode = "All"
        self.icon_plus = load_icon("plus", 16)
        self.icon_trash = load_icon("trash", 16)

        page_title(self, "Task", "task")

        # ---------------- progress panel ----------------
        panel = ctk.CTkFrame(self, corner_radius=8, border_width=1,
                             border_color=BORDER, fg_color=PANEL)
        panel.pack(fill="x", padx=30, pady=(0, 8))

        head = ctk.CTkFrame(panel, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(10, 0))
        ctk.CTkLabel(head, text="TASK PROGRESS", text_color=GREEN,
                     font=ctk.CTkFont(family=FONT, size=11, weight="bold")
                     ).pack(side="left")

        clear = ctk.CTkButton(head, text="Clear done", width=92, height=26,
                              fg_color="transparent", hover_color=RED_BTN,
                              text_color=MUTED, command=self.clear_done)
        glow(clear, idle=PANEL, hot=RED)
        clear.pack(side="right")

        self.progress_lbl = ctk.CTkLabel(head, text="0 / 0 complete",
                                         text_color=MUTED,
                                         font=ctk.CTkFont(family=FONT, size=11))
        self.progress_lbl.pack(side="right", padx=12)

        self.bar = ctk.CTkProgressBar(panel, height=6, progress_color=GREEN,
                                      fg_color=TRACK)
        self.bar.set(0)
        self.bar.pack(fill="x", padx=16, pady=(6, 14))

        # ---------------- add row ----------------
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=30, pady=8)

        self.entry = ctk.CTkEntry(row, placeholder_text="> New task...", height=38)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.add_task())

        self.search = ctk.CTkEntry(row, placeholder_text="Search tasks…", height=38,
                                   width=190)
        self.search.pack(side="right", padx=(10, 0))
        self.search.bind("<KeyRelease>", lambda _e: self._apply_filters())

        add = ctk.CTkButton(row, text="Add", image=self.icon_plus,
                            compound="left", width=100, height=38,
                            command=self.add_task)
        glow(add, idle=PANEL, hot=GREEN)
        add.pack(side="right")

        # ---------------- filters ----------------
        filters = ctk.CTkFrame(self, fg_color="transparent")
        filters.pack(fill="x", padx=30, pady=(0, 4))
        self.filter_buttons = {}
        for mode in ("All", "Open", "Done"):
            button = ctk.CTkButton(filters, text=mode, width=70, height=28,
                                   command=lambda value=mode: self._set_filter(value))
            button.pack(side="left", padx=(0, 6))
            self.filter_buttons[mode] = button

        # ---------------- list ----------------
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(6, 30))

        self.empty = ctk.CTkLabel(
            self.list_frame,
            text="> no tasks yet — type a task above and press Enter",
            text_color=MUTED, font=ctk.CTkFont(family=FONT, size=12))
        self.empty.pack(anchor="w", pady=10, padx=6)

        self._set_filter("All")

    # ==================================================================
    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            return
        if any(t["text"].lower() == text.lower() for t in self.tasks):
            toast(self.winfo_toplevel(), f"Task already exists: {text}", "warn")
            return

        row = ctk.CTkFrame(self.list_frame, fg_color=PANEL, corner_radius=6,
                           border_width=1, border_color=BORDER)
        row.pack(fill="x", pady=4, padx=2)

        box = ctk.CTkCheckBox(row, text=text,
                              font=ctk.CTkFont(family=FONT, size=14))
        box.pack(side="left", padx=12, pady=10)

        delete = ctk.CTkButton(
            row, text="Delete", image=self.icon_trash, compound="left",
            width=92, height=28, fg_color=RED_BTN, hover_color=RED_HOVER,
            text_color=RED,
        )
        delete.pack(side="right", padx=8, pady=8)

        task = {"text": text, "done": False, "row": row, "box": box,
                "color": GREEN}
        box.configure(command=lambda t=task: self.toggle(t))
        delete.configure(command=lambda t=task: self.remove(t))

        self.tasks.append(task)
        self.empty.pack_forget()
        reveal(row)
        self._refresh_progress()
        self.entry.delete(0, "end")
        self._apply_filters()

    # ==================================================================
    def toggle(self, task):
        task["done"] = bool(task["box"].get())
        done = task["done"]

        font = ctk.CTkFont(family=FONT, size=14, overstrike=done)
        task["box"].configure(font=font)

        target = MUTED if done else GREEN
        tween(task["box"], "text_color", task["color"], target, 240,
              key="task-text")
        task["color"] = target

        tween(task["row"], "fg_color", PANEL, PANEL2 if done else PANEL, 240,
              key="task-bg")
        tween(task["row"], "border_color", BORDER,
              GREEN_DIM if done else BORDER, 240, key="task-line")

        self._refresh_progress()
        self._apply_filters()

    # ==================================================================
    def remove(self, task):
        if task not in self.tasks:
            return
        self.tasks.remove(task)
        row = task["row"]

        animate(row, 200,
                lambda t: row.configure(
                    fg_color=lerp_color(PANEL, PANEL2, t),
                    border_color=lerp_color(BORDER, PANEL2, t)),
                on_done=lambda: row.winfo_exists() and row.destroy(),
                key="task-out")

        if not self.tasks:
            self.empty.pack(anchor="w", pady=10, padx=6)
        self._refresh_progress()
        self._apply_filters()

    def _set_filter(self, mode):
        self.filter_mode = mode
        for name, button in self.filter_buttons.items():
            button.configure(fg_color=BTN if name == mode else PANEL,
                             text_color=GREEN if name == mode else MUTED)
        self._apply_filters()

    def _apply_filters(self):
        if not hasattr(self, "filter_buttons"):
            return
        query = self.search.get().strip().casefold()
        visible = 0
        for task in self.tasks:
            matches_state = (self.filter_mode == "All"
                             or (self.filter_mode == "Done") == task["done"])
            matches_text = query in task["text"].casefold()
            if matches_state and matches_text:
                task["row"].pack(fill="x", pady=4, padx=2)
                visible += 1
            else:
                task["row"].pack_forget()
        if self.tasks and visible == 0:
            self.empty.configure(text="> no tasks match this filter")
            self.empty.pack(anchor="w", pady=10, padx=6)
        else:
            self.empty.configure(text="> no tasks yet — type a task above and press Enter")
            if self.tasks:
                self.empty.pack_forget()

    def clear_done(self):
        done = [t for t in self.tasks if t["done"]]
        if not done:
            toast(self.winfo_toplevel(), "Nothing completed yet", "warn")
            return
        for i, task in enumerate(done):
            task["row"].after(i * 45, lambda t=task: self.remove(t))
        toast(self.winfo_toplevel(), f"Cleared {len(done)} completed task(s)")

    # ==================================================================
    def _refresh_progress(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["done"])
        target = done / total if total else 0.0

        current = self.bar.get()
        animate(self, 380,
                lambda t: self.bar.set(current + (target - current) * t),
                ease=ease_out_cubic, key="progress")

        self.progress_lbl.configure(
            text=f"{done} / {total} complete" + (f"  ·  {int(target * 100)}%" if total else ""))
