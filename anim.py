"""Tiny animation toolkit for Tkinter / CustomTkinter.

Everything runs on Tk's own event loop (``widget.after``), so there is no
extra thread and no external dependency.  Set ``anim.ANIMATIONS = False``
to make every animation snap straight to its final state (the Settings
page uses that switch).
"""

import math
import time

ANIMATIONS = True
_FRAME_MS = 16          # ~60 fps
_jobs = {}


# ------------------------------------------------------------------ easing
def linear(t):
    return t


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t ** 3
    return 1 - (-2 * t + 2) ** 3 / 2


def ease_out_quad(t):
    return 1 - (1 - t) ** 2


def ease_out_back(t, overshoot=1.2):
    c = overshoot + 1
    return 1 + c * (t - 1) ** 3 + overshoot * (t - 1) ** 2


# ------------------------------------------------------------------ colors
def hex_to_rgb(color):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in rgb)


def lerp_color(a, b, t):
    """Interpolate two ``#rrggbb`` colors (or (r, g, b) tuples)."""
    ra = hex_to_rgb(a) if isinstance(a, str) else a
    rb = hex_to_rgb(b) if isinstance(b, str) else b
    return rgb_to_hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def is_hex(color):
    return isinstance(color, str) and color.startswith("#") and len(color) in (4, 7)


# ----------------------------------------------------------------- engine
def cancel(widget, key="default"):
    """Stop a running animation for ``(widget, key)`` if there is one."""
    job = _jobs.pop((str(widget), key), None)
    if job is not None:
        try:
            widget.after_cancel(job)
        except Exception:
            pass


def animate(widget, duration, on_frame, on_done=None,
            ease=ease_out_cubic, key="default"):
    """Call ``on_frame(t)`` with t going 0 -> 1 over ``duration`` ms."""
    k = (str(widget), key)
    cancel(widget, key)

    if not ANIMATIONS or duration <= 0:
        try:
            on_frame(1.0)
        except Exception:
            pass
        if on_done:
            on_done()
        return

    started = time.perf_counter()
    seconds = duration / 1000.0

    def step():
        try:
            if not widget.winfo_exists():
                _jobs.pop(k, None)
                return
        except Exception:
            _jobs.pop(k, None)
            return

        progress = (time.perf_counter() - started) / seconds
        finished = progress >= 1.0
        value = 1.0 if finished else max(0.0, progress)

        try:
            on_frame(ease(value))
        except Exception:
            _jobs.pop(k, None)
            return

        if finished:
            _jobs.pop(k, None)
            if on_done:
                try:
                    on_done()
                except Exception:
                    pass
        else:
            _jobs[k] = widget.after(_FRAME_MS, step)

    _jobs[k] = widget.after(_FRAME_MS, step)


def set_opt(widget, option, value):
    try:
        widget.configure(**{option: value})
    except Exception:
        pass


def tween(widget, option, start, end, duration=160, key=None, ease=ease_out_cubic):
    """Smoothly move a color option from ``start`` to ``end``."""
    key = key or f"tween:{option}"

    if not (is_hex(start) and is_hex(end)):
        set_opt(widget, option, end)
        return

    animate(
        widget, duration,
        lambda t: set_opt(widget, option, lerp_color(start, end, t)),
        ease=ease, key=key,
    )


def pulse(widget, option, color_a, color_b, period=1400, key="pulse"):
    """Endlessly breathe a color option between two colors (sine wave)."""
    k = (str(widget), key)
    cancel(widget, key)

    if not ANIMATIONS:
        set_opt(widget, option, color_b)
        return

    started = time.perf_counter()
    seconds = max(0.1, period / 1000.0)

    def step():
        if not ANIMATIONS:
            _jobs.pop(k, None)
            set_opt(widget, option, color_b)
            return
        try:
            if not widget.winfo_exists():
                return
            phase = (1 + math.sin((time.perf_counter() - started) / seconds * math.tau)) / 2
            widget.configure(**{option: lerp_color(color_a, color_b, phase)})
        except Exception:
            return
        _jobs[k] = widget.after(40, step)

    step()


def stop_pulse(widget, key="pulse"):
    cancel(widget, key)


def count_up(widget, start, end, duration=520, fmt="{:.0f}", key="count"):
    """Animate a label's text as a number counting from ``start`` to ``end``."""
    animate(
        widget, duration,
        lambda t: set_opt(widget, "text", fmt.format(start + (end - start) * t)),
        ease=ease_out_cubic, key=key,
    )
