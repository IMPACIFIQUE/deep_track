import os
import sys


if getattr(sys, "frozen", False):
    bundled_root = sys._MEIPASS
    tcl_library = os.path.join(bundled_root, "tcl", "tcl8.6")
    tk_library = os.path.join(bundled_root, "tcl", "tk8.6")
    if os.path.isfile(os.path.join(tcl_library, "init.tcl")):
        os.environ["TCL_LIBRARY"] = tcl_library
    if os.path.isfile(os.path.join(tk_library, "tk.tcl")):
        os.environ["TK_LIBRARY"] = tk_library
