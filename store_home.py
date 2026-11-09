import tkinter as tk

from theme import *
from widgets import Card, pink_button, clear_children


class StoreHome(tk.Frame):
    """หน้าแรกของร้าน: ต้อนรับ + รายการบริการและราคา"""

    def __init__(self, parent, db, go):
        super().__init__(parent, bg=BG)
        self.db, self.go = db, go
        hero = Card(self, height=190, fill="#FFEFF4")
        hero.pack(fill="x", padx=30, pady=(22, 10))
        h = hero.inner
        tk.Label(h, text="👑 ยินดีต้อนรับสู่ Beauty Queen", font=FONT_T, bg="#FFEFF4",
                 fg=DARK).pack(anchor="w", pady=(6, 2))
        tk.Label(h, text="ร้านเสริมสวยที่ดูแลคุณให้สวยปังทุกวัน 💗\n"
                         "เปิดทุกวัน 10:00 - 19:00 น.  •  จองคิวออนไลน์ได้ง่ายๆ ใน 4 ขั้นตอน",
                 font=FONT, bg="#FFEFF4", fg=TEXT, justify="left").pack(anchor="w")
        pink_button(h, "📅  จองคิวเลย", lambda: self.go("book"), pady=10, padx=26
                    ).pack(anchor="w", pady=(12, 0))

        self.menu = Card(self)
        self.menu.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def refresh(self):
        box = self.menu.inner
        clear_children(box)
        tk.Label(box, text="💅 บริการและราคา", font=FONT_B, bg=WHITE, fg=PINK
                 ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        box.columnconfigure((0, 1), weight=1, uniform="c")
        for i, r in enumerate(self.db.q("SELECT * FROM services ORDER BY id")):
            row = tk.Frame(box, bg=SOFT, padx=14, pady=10)
            row.grid(row=1 + i // 2, column=i % 2, sticky="ew", padx=6, pady=5)
            row.columnconfigure(0, weight=1)
            tk.Label(row, text=r["name"], font=FONT_B, bg=SOFT, fg=TEXT
                     ).grid(row=0, column=0, sticky="w")
            tk.Label(row, text=f"ใช้เวลาประมาณ {r['duration']} นาที", font=FONT_S, bg=SOFT,
                     fg=MUTED).grid(row=1, column=0, sticky="w")
            tk.Label(row, text=f"฿{r['price']:,.0f}", font=("Tahoma", 14, "bold"), bg=SOFT,
                     fg=DARK).grid(row=0, column=1, rowspan=2, sticky="e")
