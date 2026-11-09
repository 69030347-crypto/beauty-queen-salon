import tkinter as tk
from datetime import date
from tkinter import messagebox

from theme import *
from widgets import Card, pink_button, soft_entry, clear_children


class MyBookingsPage(tk.Frame):
    """ลูกค้าเช็ก/ยกเลิกการจองด้วยเบอร์โทร"""

    def __init__(self, parent, db, go):
        super().__init__(parent, bg=BG)
        self.db, self.go = db, go
        self.phone = tk.StringVar()
        card = Card(self)
        card.pack(fill="both", expand=True, padx=30, pady=22)
        box = card.inner
        tk.Label(box, text="🔍 เช็กการจองของฉัน", font=("Tahoma", 14, "bold"), bg=WHITE,
                 fg=DARK).pack(anchor="w")
        bar = tk.Frame(box, bg=WHITE)
        bar.pack(fill="x", pady=10)
        tk.Label(bar, text="เบอร์โทรที่ใช้จอง", font=FONT, bg=WHITE, fg=TEXT).pack(side="left")
        e = soft_entry(bar, self.phone, 24)
        e.pack(side="left", padx=10, ipady=4)
        e.bind("<Return>", lambda _: self.search())
        pink_button(bar, "ค้นหา", self.search).pack(side="left")
        self.result = tk.Frame(box, bg=WHITE)
        self.result.pack(fill="both", expand=True)

    def refresh(self):
        clear_children(self.result)

    def search(self):
        key = clean_phone(self.phone.get())
        clear_children(self.result)
        if len(key) < 9:
            return messagebox.showwarning("เบอร์ไม่ถูกต้อง", "กรุณากรอกเบอร์โทรให้ถูกต้องนะคะ")
        rows = [r for r in self.db.q(
            "SELECT a.id, a.date, a.time, a.status, s.name AS sn, s.price, st.name AS stn, c.phone "
            "FROM appointments a JOIN customers c ON c.id=a.customer_id "
            "JOIN services s ON s.id=a.service_id JOIN staff st ON st.id=a.staff_id "
            "ORDER BY a.date DESC, a.time DESC") if clean_phone(r["phone"]) == key][:8]
        if not rows:
            return tk.Label(self.result, text="ไม่พบการจองจากเบอร์นี้ค่ะ 🌷", font=FONT,
                            bg=WHITE, fg=MUTED).pack(pady=20)
        today = date.today().isoformat()
        for r in rows:
            row = tk.Frame(self.result, bg=SOFT, padx=12, pady=8)
            row.pack(fill="x", pady=3)
            row.columnconfigure(0, weight=1)
            tk.Label(row, text=f"#{r['id']}  {r['sn']}  (฿{r['price']:,.0f})", font=FONT_B,
                     bg=SOFT, fg=TEXT).grid(row=0, column=0, sticky="w")
            tk.Label(row, text=f"{th_date(r['date'])}  {r['time']} น.  •  ช่าง {r['stn']}",
                     font=FONT_S, bg=SOFT, fg=MUTED).grid(row=1, column=0, sticky="w")
            bgc, fgc = STATUS_COLORS[r["status"]]
            tk.Label(row, text=r["status"], font=FONT_S, bg=bgc, fg=fgc, padx=10, pady=3
                     ).grid(row=0, column=1, padx=10)
            if r["status"] == STATUS[0] and r["date"] >= today:
                pink_button(row, "ยกเลิกคิว", lambda i=r["id"]: self.cancel(i),
                            bg="#F29AB5", hover="#D9708F", pady=3
                            ).grid(row=0, column=2, rowspan=2)

    def cancel(self, bid):
        if messagebox.askyesno("ยืนยัน", f"ต้องการยกเลิกการจอง #{bid} ใช่ไหมคะ?"):
            self.db.x("UPDATE appointments SET status='ยกเลิก' WHERE id=?", (bid,))
            self.search()
