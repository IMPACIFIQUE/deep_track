import json
import math
import os
import re
import shutil
import socket
import subprocess
import threading
import time

import customtkinter as ctk

from anim import animate, lerp_color, tween
from theme import (BORDER, BTN, FONT, GLOW, GREEN, GREEN_DIM, MUTED, PANEL,
                   PANEL2, RED, RED_BTN, RED_HOVER)
from ui import glow, reveal, toast
from utils import load_icon, page_title, user_data_dir


class DevicePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._device_file = os.path.join(user_data_dir(), "devices.json")
        self.devices = self._load_devices()
        self._scanning = False
        self.icon_trash = load_icon("trash", 16)
        self.icon_device = load_icon("device", 22)

        page_title(self, "Remote PCs", "device")

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=30, pady=(0, 6))

        self.connection_type = ctk.CTkOptionMenu(
            row, values=["RustDesk", "Windows RDP"], width=126, height=38,
            command=self._update_address_hint)
        self.connection_type.pack(side="left", padx=(0, 8))

        self.host_entry = ctk.CTkEntry(
            row, placeholder_text="RustDesk ID", height=38)
        self.host_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.host_entry.bind("<Return>", lambda e: self.connect_address())

        connect_button = ctk.CTkButton(
            row, text="Connect & Save", width=126, height=38,
            command=self.connect_address)
        glow(connect_button, idle=PANEL, hot=GREEN)
        connect_button.pack(side="right")

        self.scan_button = ctk.CTkButton(
            row, text="Check RDP", width=98, height=38,
            fg_color=BTN, hover_color=PANEL2, command=self.scan)
        glow(self.scan_button, idle=PANEL, hot=GLOW)
        self.scan_button.pack(side="right", padx=(0, 8))

        ctk.CTkLabel(
            self,
            text="Enter a trusted PC address to launch a remote session. Successful launches are saved here automatically; the remote user must approve access.",
            text_color=MUTED, font=ctk.CTkFont(family=FONT, size=10),
        ).pack(anchor="w", padx=30, pady=(0, 5))

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(fill="x", padx=30, pady=(0, 4))
        self.count_lbl = ctk.CTkLabel(info, text="0 saved · 0 RDP port(s) open",
                                      text_color=MUTED,
                                      font=ctk.CTkFont(family=FONT, size=11))
        self.count_lbl.pack(side="left")

        self.search = ctk.CTkEntry(info, placeholder_text="Filter devices…", width=200,
                                   height=30)
        self.search.pack(side="right")
        self.search.bind("<KeyRelease>", lambda _e: self._filter_rows())

        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(4, 30))

        self.empty = ctk.CTkLabel(
            self.list_frame,
            text="> no recent PCs — enter a RustDesk ID or Windows RDP address above",
            text_color=MUTED, font=ctk.CTkFont(family=FONT, size=12))
        self.empty.pack(anchor="w", pady=10, padx=6)

        self.refresh()
        self._tick()

    # ==================================================================
    def _load_devices(self):
        try:
            with open(self._device_file, "r", encoding="utf-8") as file:
                records = json.load(file)
        except (OSError, ValueError, TypeError):
            return []
        if not isinstance(records, list):
            return []

        devices = []
        for record in records:
            if not isinstance(record, dict):
                continue
            name = str(record.get("name", "")).strip()
            connection_type = record.get("connection_type", "Windows RDP")
            address = str(record.get("address", record.get("host", ""))).strip()
            if connection_type not in ("RustDesk", "Windows RDP"):
                continue
            if name and self._valid_address(connection_type, address):
                devices.append({"name": name, "connection_type": connection_type,
                                "address": address, "online": None,
                                "row": None, "dot": None, "pill": None})
        return devices

    def _save_devices(self):
        records = [{"name": device["name"],
                    "connection_type": device["connection_type"],
                    "address": device["address"]}
                   for device in self.devices]
        try:
            os.makedirs(os.path.dirname(self._device_file), exist_ok=True)
            with open(self._device_file, "w", encoding="utf-8") as file:
                json.dump(records, file, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    @staticmethod
    def _valid_address(connection_type, address):
        if connection_type == "RustDesk":
            return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", address))
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*(?::\d{1,5})?", address):
            return False
        if ":" in address:
            port = int(address.rsplit(":", 1)[1])
            return 1 <= port <= 65535
        return True

    def _update_address_hint(self, value):
        self.host_entry.configure(
            placeholder_text="RustDesk ID" if value == "RustDesk"
            else "Windows PC host name or IP address")

    def connect_address(self):
        address = self.host_entry.get().strip()
        connection_type = self.connection_type.get()
        if not address:
            toast(self.winfo_toplevel(),
                  "Enter a RustDesk ID or Windows RDP host", "warn")
            return
        if not self._valid_address(connection_type, address):
            toast(self.winfo_toplevel(),
                  "Enter a valid RustDesk ID or RDP host address", "warn")
            return
        name = address if connection_type == "Windows RDP" else f"RustDesk {address[-6:]}"
        device = {"name": name, "connection_type": connection_type,
                  "address": address, "online": None,
                  "row": None, "dot": None, "pill": None}
        self.connect(device)
        self.host_entry.delete(0, "end")

    def _remember_connection(self, device):
        existing = next((item for item in self.devices
                         if item["connection_type"] == device["connection_type"]
                         and item["address"].casefold() == device["address"].casefold()),
                        None)
        if existing is not None:
            self.devices.remove(existing)
        self.devices.insert(0, {**device, "online": None, "row": None,
                                "dot": None, "pill": None})
        saved = self._save_devices()
        self.refresh()
        toast(self.winfo_toplevel(),
              f"Connection launched · {device['name']}" if saved else
              "Connection launched; could not save it",
              "info" if saved else "warn")

    def remove(self, device):
        if device not in self.devices:
            return
        self.devices.remove(device)
        saved = self._save_devices()
        self.refresh()
        toast(self.winfo_toplevel(),
              f"Device removed: {device['name']}" if saved else
              "Device removed for this session; could not save the list",
              "warn")

    def scan(self):
        devices = [d for d in self.devices
                   if d["connection_type"] == "Windows RDP"]
        if not devices:
            toast(self.winfo_toplevel(), "Launch or save a Windows RDP connection first", "warn")
            return
        if self._scanning:
            return
        if os.name != "nt":
            toast(self.winfo_toplevel(),
                  "RDP checks are available from Windows", "warn")
            return

        self._scanning = True
        self.scan_button.configure(state="disabled", text="Checking…")
        devices = list(devices)

        def check_hosts():
            results = []
            for device in devices:
                host, port = self._split_host(device["address"])
                try:
                    connection = socket.create_connection(
                        (host, port), timeout=1.2)
                    connection.close()
                    reachable = True
                except (OSError, ValueError, OverflowError):
                    reachable = False
                results.append((device, reachable))
            try:
                self.after(0, lambda: self._finish_scan(results))
            except Exception:
                pass

        threading.Thread(target=check_hosts, daemon=True).start()

    @staticmethod
    def _split_host(value):
        host, separator, port_text = value.rpartition(":")
        if separator and port_text.isdigit() and host:
            return host, int(port_text)
        return value, 3389

    def _finish_scan(self, results):
        if not self.winfo_exists():
            return
        for device, reachable in results:
            if device in self.devices:
                device["online"] = reachable
        self._scanning = False
        self.scan_button.configure(state="normal", text="Check RDP")
        self.refresh()
        reachable = sum(1 for _device, ready in results if ready)
        toast(self.winfo_toplevel(),
              f"RDP reachable · {reachable} of {len(results)} PC(s)")

    def connect(self, device):
        if device["connection_type"] == "RustDesk":
            executable = self._find_rustdesk()
            if executable is None:
                toast(self.winfo_toplevel(),
                      "Install RustDesk on this PC to open the session", "warn")
                return
            try:
                subprocess.Popen([executable], shell=False)
                self.clipboard_clear()
                self.clipboard_append(device["address"])
                self._remember_connection(device)
            except OSError as exc:
                toast(self.winfo_toplevel(),
                      f"Could not launch RustDesk: {exc}", "error")
            return

        if os.name != "nt":
            toast(self.winfo_toplevel(),
                  "Windows Remote Desktop is only available on Windows", "warn")
            return
        executable = self._find_mstsc()
        if executable is None:
            toast(self.winfo_toplevel(),
                  "Windows Remote Desktop was not found", "error")
            return
        try:
            subprocess.Popen(
                [executable, f"/v:{device['address']}"], shell=False)
            self._remember_connection(device)
        except OSError as exc:
            toast(self.winfo_toplevel(),
                  f"Could not launch Remote Desktop: {exc}", "error")

    @staticmethod
    def _find_mstsc():
        executable = shutil.which("mstsc.exe") or shutil.which("mstsc")
        if executable is not None:
            return executable
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        candidate = os.path.join(system_root, "System32", "mstsc.exe")
        return candidate if os.path.isfile(candidate) else None

    @staticmethod
    def _find_rustdesk():
        executable = shutil.which("rustdesk") or shutil.which("rustdesk.exe")
        if executable is not None:
            return executable
        if os.name == "nt":
            roots = (os.environ.get("ProgramFiles", r"C:\Program Files"),
                     os.environ.get("LOCALAPPDATA", ""))
            for root in roots:
                candidate = os.path.join(root, "RustDesk", "rustdesk.exe")
                if os.path.isfile(candidate):
                    return candidate
        elif os.name == "posix" and os.uname().sysname == "Darwin":
            candidate = "/Applications/RustDesk.app/Contents/MacOS/RustDesk"
            if os.path.isfile(candidate):
                return candidate
        return None

    # ==================================================================
    def refresh(self):
        for w in self.list_frame.winfo_children():
            if w is not self.empty:
                w.destroy()

        self.empty.pack_forget()
        if not self.devices:
            self.empty.pack(anchor="w", pady=10, padx=6)

        for device in self.devices:
            row = ctk.CTkFrame(self.list_frame, fg_color=PANEL, corner_radius=8,
                               border_width=1, border_color=BORDER)
            row.pack(fill="x", pady=4, padx=2)

            dot = ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=18),
                               text_color=GREEN if device["online"] is True else
                               RED if device["online"] is False else MUTED,
                               width=18)
            dot.pack(side="left", padx=(14, 4), pady=10)

            details = ctk.CTkFrame(row, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True, padx=6, pady=5)
            ctk.CTkLabel(details, text=f" {device['name']}",
                         image=self.icon_device, compound="left", anchor="w",
                         font=ctk.CTkFont(size=14, weight="bold")
                         ).pack(anchor="w")
            ctk.CTkLabel(details, text=device["address"], text_color=MUTED,
                         anchor="w", font=ctk.CTkFont(family=FONT, size=10)
                         ).pack(anchor="w", padx=(28, 0))

            remove = ctk.CTkButton(
                row, text="Remove", image=self.icon_trash, compound="left",
                width=100, height=30, fg_color=RED_BTN, hover_color=RED_HOVER,
                text_color=RED, command=lambda d=device: self.remove(d))
            glow(remove, idle=RED_BTN, hot=RED)
            remove.pack(side="right", padx=10, pady=8)

            if device["connection_type"] == "RustDesk":
                status_text, status_color = "RUSTDESK ID", MUTED
            else:
                status_text = ("PORT OPEN" if device["online"] is True else
                               "UNREACHABLE" if device["online"] is False else
                               "NOT CHECKED")
                status_color = (GREEN if device["online"] is True else
                                RED if device["online"] is False else MUTED)
            pill = ctk.CTkLabel(
                row, text=f"  {status_text}  ", width=100, height=28,
                corner_radius=4,
                fg_color=BTN if device["online"] is True else PANEL2,
                text_color=status_color,
                font=ctk.CTkFont(family=FONT, size=10, weight="bold"))
            pill.pack(side="right", padx=4)

            connect = ctk.CTkButton(
                row, text="Connect", width=88, height=30,
                command=lambda d=device: self.connect(d))
            glow(connect, idle=PANEL, hot=GLOW)
            connect.pack(side="right", padx=4)

            device["row"] = row
            device["dot"] = dot
            device["pill"] = pill
            reveal(row)

        self._filter_rows()

        online = sum(1 for d in self.devices
                     if d["connection_type"] == "Windows RDP"
                     and d["online"] is True)
        self.count_lbl.configure(
            text=f"{len(self.devices)} saved · {online} RDP port(s) open · "
                 f"{sum(1 for d in self.devices if d['connection_type'] == 'RustDesk')} RustDesk ID(s)")

    def _filter_rows(self):
        query = self.search.get().strip().casefold()
        for device in self.devices:
            row = device.get("row")
            if row is not None:
                if (query in device["name"].casefold()
                        or query in device["address"].casefold()):
                    row.pack(fill="x", pady=4, padx=2)
                else:
                    row.pack_forget()

    # ==================================================================
    #  shared pulse ticker for every online dot (one loop, not one per row)
    # ==================================================================
    def _tick(self):
        if self.winfo_ismapped():
            phase = (1 + math.sin(time.perf_counter() * 2.6)) / 2
            color = lerp_color(GREEN, GREEN_DIM, phase)
            for device in self.devices:
                dot = device["dot"]
                if (dot is not None and device["connection_type"] == "Windows RDP"
                        and device["online"] is True):
                    try:
                        dot.configure(text_color=color)
                    except Exception:
                        pass
        self.after(70, self._tick)
