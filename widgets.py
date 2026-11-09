import tkinter as tk

from theme import *


def make_crown(size=64):
    """วาดไอคอนมงกุฎสีชมพูด้วยโค้ด (ไม่ต้องมีไฟล์รูป)"""
    img = tk.PhotoImage(width=size, height=size)
    k = size / 64
    poly = [(8, 50), (8, 22), (20, 34), (32, 14), (44, 34), (56, 22), (56, 50)]

    def inside(x, y):
        c = False
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
        return c

    for py in range(size):
        for px in range(size):
            x, y = (px + .5) / k, (py + .5) / k
            if (x - 32) ** 2 + (y - 32) ** 2 > 31 ** 2:
                continue
            color = ACTIVE
            if inside(x, y):
                color = PINK
            if 8 <= x <= 56 and 50 <= y <= 57:
                color = DARK
            if any((x - gx) ** 2 + (y - gy) ** 2 <= 3.6 ** 2 for gx, gy in [(8, 22), (32, 14), (56, 22)]):
                color = WHITE
            img.put(color, (px, py))
    return img


# ---------------------------------------------------------------- WIDGET HELPERS
def pink_button(parent, text, command, bg=PINK, fg=WHITE, hover=DARK, **kw):
    b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                  activebackground=hover, activeforeground=WHITE, relief="flat",
                  bd=0, font=FONT_B, padx=kw.pop("padx", 14), pady=kw.pop("pady", 7),
                  cursor="hand2", **kw)
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def chip(parent, text, command, selected=False, disabled=False, width=8, height=2):
    """ปุ่มเลือก (วัน/เวลา) — ชมพูเข้มเมื่อถูกเลือก, เทาเมื่อเลือกไม่ได้"""
    if disabled:
        return tk.Button(parent, text=text, state="disabled", width=width, height=height,
                         bg=GREY, fg="#A89AA2", disabledforeground="#A89AA2",
                         relief="flat", bd=0, font=FONT)
    bg, fg = (PINK, WHITE) if selected else (SOFT, TEXT)
    b = tk.Button(parent, text=text, command=command, width=width, height=height, bg=bg,
                  fg=fg, activebackground=ACTIVE, activeforeground=DARK, relief="flat",
                  bd=0, font=FONT_B if selected else FONT, cursor="hand2",
                  highlightthickness=1, highlightbackground=BORDER)
    return b


def soft_entry(parent, var, width=26, show=None):
    return tk.Entry(parent, textvariable=var, width=width, font=FONT, relief="flat",
                    bg=SOFT, fg=TEXT, insertbackground=DARK, highlightthickness=1,
                    highlightbackground=BORDER, highlightcolor=PINK, show=show or "")


def F(key, label, kind="entry", opts=None, req=True, default=""):
    return dict(key=key, label=label, kind=kind, opts=opts, req=req, default=default)


class Card(tk.Canvas):
    """การ์ดสีขาวมุมโค้งมีเงานุ่มๆ ใส่เนื้อหาไว้ใน .inner"""

    def __init__(self, parent, width=None, height=None, fill=WHITE, outer=BG,
                 radius=22, pad=16):
        kw = {}
        if width:
            kw["width"] = width
        if height:
            kw["height"] = height
        super().__init__(parent, bg=outer, highlightthickness=0, **kw)
        self.fill, self.r, self.pad = fill, radius, pad
        self.inner = tk.Frame(self, bg=fill)
        self.win = self.create_window(pad, pad, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._draw)

    def _rr(self, x1, y1, x2, y2, fill, outline):
        r = self.r
        pts = [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
               x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
               x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r,
               x1, y1 + r, x1, y1]
        self.create_polygon(pts, smooth=True, fill=fill, outline=outline, tags="bg")

    def _draw(self, e):
        w, h = e.width, e.height
        self.delete("bg")
        self._rr(5, 6, w - 1, h - 1, SHADOW, "")
        self._rr(2, 2, w - 5, h - 5, self.fill, BORDER)
        self.tag_lower("bg")
        self.coords(self.win, self.pad, self.pad)
        self.itemconfigure(self.win, width=max(w - 2 * self.pad - 6, 1),
                           height=max(h - 2 * self.pad - 6, 1))


class LineChart(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=WHITE, highlightthickness=0)
        self.labels, self.values = [], []
        self.bind("<Configure>", lambda e: self.draw())

    def set_data(self, labels, values):
        self.labels, self.values = labels, values
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 80 or h < 80 or len(self.values) < 2:
            return
        L, R, T, B = 62, 24, 28, 32
        top = max(max(self.values), 1) * 1.15
        for i in range(5):
            y = T + (h - T - B) * i / 4
            self.create_line(L, y, w - R, y, fill="#FBE6EE")
            self.create_text(L - 8, y, text=f"{top * (1 - i / 4):,.0f}", anchor="e",
                             fill=MUTED, font=FONT_S)
        n = len(self.values)
        pts = []
        for i, v in enumerate(self.values):
            x = L + (w - L - R) * i / (n - 1)
            y = T + (h - T - B) * (1 - v / top)
            pts.append((x, y))
            self.create_text(x, h - B + 15, text=self.labels[i], fill=MUTED, font=FONT_S)
        flat = [c for p in pts for c in p]
        self.create_polygon([pts[0][0], h - B] + flat + [pts[-1][0], h - B],
                            fill="#FDEAF1", outline="")
        self.create_line(*flat, smooth=True, fill="#F2A0BE", width=3)
        for x, y in pts:
            self.create_oval(x - 5, y - 5, x + 5, y + 5, fill=WHITE, outline=PINK, width=2)
        x, y = pts[-1]
        self.create_text(x, y - 18, text=f"฿{self.values[-1]:,.0f}", fill=DARK, font=FONT_B)


def clear_children(w):
    for c in w.winfo_children():
        c.destroy()
