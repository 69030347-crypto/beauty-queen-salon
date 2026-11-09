import tkinter as tk
from datetime import datetime, date, timedelta
from tkinter import ttk, messagebox

from theme import *
from widgets import Card, pink_button, chip, soft_entry, clear_children


class BookingPage(tk.Frame):
    """จองคิว 4 ขั้นตอน: บริการ → วัน/เวลา → ข้อมูลลูกค้า → ยืนยัน"""
    STEPS = ["เลือกบริการ", "เลือกวัน-เวลา", "ข้อมูลของคุณ", "ยืนยันการจอง"]

    def __init__(self, parent, db, go):
        super().__init__(parent, bg=BG)
        self.db, self.go = db, go
        self.name, self.phone, self.staff_choice = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.head = tk.Frame(self, bg=BG)
        self.head.pack(fill="x", padx=30, pady=(18, 6))
        self.card = Card(self)
        self.card.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self.body = self.card.inner
        self.reset()

    def reset(self):
        self.step, self.service, self.day, self.time = 0, None, None, None
        self.staff_map, self.done = {}, None
        self.name.set("")
        self.phone.set("")
        self.staff_choice.set("")

    def refresh(self):
        if self.done:
            self.reset()
        self.render()

    def render(self):
        clear_children(self.head)
        clear_children(self.body)
        if self.done:
            return self.show_success()
        for i, t in enumerate(self.STEPS):
            if i == self.step:
                bg, fg = PINK, WHITE
            elif i < self.step:
                bg, fg = ACTIVE, DARK
            else:
                bg, fg = SOFT, MUTED
            tk.Label(self.head, text=f"{i + 1}  {t}", font=FONT_B, bg=bg, fg=fg,
                     padx=16, pady=7).pack(side="left", padx=(0, 8))
        [self.step_service, self.step_datetime, self.step_info, self.step_confirm][self.step]()

    def title(self, text, sub=""):
        tk.Label(self.body, text=text, font=("Tahoma", 14, "bold"), bg=WHITE, fg=DARK
                 ).pack(anchor="w")
        if sub:
            tk.Label(self.body, text=sub, font=FONT, bg=WHITE, fg=MUTED).pack(anchor="w", pady=(2, 0))
        tk.Frame(self.body, bg=WHITE, height=8).pack()

    def nav(self, back=True, next_text="ถัดไป ➜", next_cmd=None):
        bar = tk.Frame(self.body, bg=WHITE)
        bar.pack(side="bottom", fill="x", pady=(10, 0))
        if back:
            pink_button(bar, "⬅ ย้อนกลับ", self.back, bg=ACTIVE, fg=DARK, hover="#F3AFCB"
                        ).pack(side="left")
        if next_cmd:
            pink_button(bar, next_text, next_cmd, padx=22).pack(side="right")

    def back(self):
        self.step -= 1
        self.render()

    # ---- ขั้นที่ 1
    def step_service(self):
        self.title("💅 คุณอยากทำอะไรดีคะ?", "แตะที่บริการที่ต้องการได้เลย")
        grid = tk.Frame(self.body, bg=WHITE)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1, 2), weight=1, uniform="s")
        for i, r in enumerate(self.db.q("SELECT * FROM services ORDER BY id")):
            b = tk.Button(grid, text=f"{r['name']}\n฿{r['price']:,.0f}  •  {r['duration']} นาที",
                          font=FONT_B, bg=SOFT, fg=TEXT, activebackground=ACTIVE,
                          activeforeground=DARK, relief="flat", bd=0, height=3, cursor="hand2",
                          highlightthickness=1, highlightbackground=BORDER,
                          command=lambda row=r: self.pick_service(row))
            b.grid(row=i // 3, column=i % 3, sticky="ew", padx=6, pady=6)

    def pick_service(self, row):
        if self.service is None or self.service["id"] != row["id"]:
            self.time = None
        self.service = row
        self.step = 1
        self.render()

    # ---- ขั้นที่ 2
    def slots(self):
        dur = self.service["duration"]
        now = datetime.now()
        now_min = now.hour * 60 + now.minute if self.day == date.today().isoformat() else -1
        out = []
        for t in range(OPEN_MIN, CLOSE_MIN - dur + 1, STEP_MIN):
            ok = t > now_min and bool(self.db.free_staff(self.day, t, dur))
            out.append((t, ok))
        return out

    def step_datetime(self):
        s = self.service
        self.title("📅 เลือกวันและเวลา", f"บริการ: {s['name']}  ({s['duration']} นาที)")
        days = tk.Frame(self.body, bg=WHITE)
        days.pack(anchor="w")
        for i in range(BOOK_DAYS):
            d = date.today() + timedelta(days=i)
            iso = d.isoformat()
            chip(days, f"{WEEK[d.weekday()]}\n{d.day} {TH_MONTHS[d.month - 1]}",
                 lambda v=iso: self.pick_day(v), selected=(self.day == iso), width=7
                 ).grid(row=i // 7, column=i % 7, padx=3, pady=3)
        if self.day:
            tk.Label(self.body, text=f"⏰ เวลาว่างของวัน {th_date(self.day)}", font=FONT_B,
                     bg=WHITE, fg=TEXT).pack(anchor="w", pady=(12, 4))
            sl = tk.Frame(self.body, bg=WHITE)
            sl.pack(anchor="w")
            slots = self.slots()
            if not any(ok for _, ok in slots):
                tk.Label(sl, text="วันนี้คิวเต็มแล้วค่ะ ลองเลือกวันอื่นนะคะ 🌷", font=FONT,
                         bg=WHITE, fg=MUTED).pack()
            for i, (t, ok) in enumerate(slots):
                chip(sl, fmt_min(t), lambda v=fmt_min(t): self.pick_time(v),
                     selected=(self.time == fmt_min(t)), disabled=not ok, width=7, height=1
                     ).grid(row=i // 9, column=i % 9, padx=3, pady=3)
        else:
            tk.Label(self.body, text="👆 เลือกวันก่อน แล้วจะแสดงเวลาที่ว่างให้ค่ะ", font=FONT,
                     bg=WHITE, fg=MUTED).pack(anchor="w", pady=14)
        self.nav(next_cmd=self.go_info)

    def pick_day(self, iso):
        self.day, self.time = iso, None
        self.render()

    def pick_time(self, t):
        self.time = t
        self.render()

    def go_info(self):
        if not self.time:
            return messagebox.showinfo("เลือกเวลา", "กรุณาเลือกวันและเวลาก่อนนะคะ 💗")
        self.step = 2
        self.render()

    # ---- ขั้นที่ 3
    def step_info(self):
        self.title("👩 ข้อมูลของคุณ", "เพื่อให้ร้านติดต่อยืนยันคิวได้ค่ะ")
        form = tk.Frame(self.body, bg=WHITE)
        form.pack(anchor="w")
        tk.Label(form, text="ชื่อ", font=FONT, bg=WHITE, fg=TEXT).grid(row=0, column=0, sticky="w", pady=8)
        soft_entry(form, self.name, 30).grid(row=0, column=1, padx=12, ipady=4)
        tk.Label(form, text="เบอร์โทร", font=FONT, bg=WHITE, fg=TEXT).grid(row=1, column=0, sticky="w", pady=8)
        soft_entry(form, self.phone, 30).grid(row=1, column=1, padx=12, ipady=4)
        tk.Label(form, text="เลือกช่าง", font=FONT, bg=WHITE, fg=TEXT).grid(row=2, column=0, sticky="w", pady=8)
        dur = self.service["duration"]
        free = self.db.free_staff(self.day, to_min(self.time), dur)
        names = {r["id"]: r["name"] + (f" ({r['specialty']})" if r["specialty"] else "")
                 for r in self.db.q("SELECT * FROM staff")}
        auto = "ไม่ระบุ (ให้ร้านจัดช่างให้)"
        self.staff_map = {auto: None, **{names[i]: i for i in free}}
        if self.staff_choice.get() not in self.staff_map:
            self.staff_choice.set(auto)
        ttk.Combobox(form, textvariable=self.staff_choice, values=list(self.staff_map),
                     state="readonly", width=28, font=FONT).grid(row=2, column=1, padx=12, ipady=3)
        self.nav(next_text="ตรวจสอบการจอง ➜", next_cmd=self.go_confirm)

    def go_confirm(self):
        if not self.name.get().strip():
            return messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อด้วยนะคะ")
        if len(clean_phone(self.phone.get())) < 9:
            return messagebox.showwarning("เบอร์ไม่ถูกต้อง", "กรุณากรอกเบอร์โทรให้ถูกต้องนะคะ")
        self.step = 3
        self.render()

    # ---- ขั้นที่ 4
    def step_confirm(self):
        s = self.service
        self.title("✅ ตรวจสอบรายละเอียดก่อนยืนยัน")
        box = tk.Frame(self.body, bg=SOFT, padx=24, pady=16)
        box.pack(anchor="w", fill="x")
        end = fmt_min(to_min(self.time) + s["duration"])
        for k, v in [("💅 บริการ", s["name"]),
                     ("📅 วันที่", th_date(self.day)),
                     ("⏰ เวลา", f"{self.time} - {end} น."),
                     ("💇 ช่าง", self.staff_choice.get()),
                     ("👩 ชื่อ", self.name.get().strip()),
                     ("📞 เบอร์โทร", self.phone.get().strip()),
                     ("💰 ราคา", f"฿{s['price']:,.0f}")]:
            r = tk.Frame(box, bg=SOFT)
            r.pack(fill="x", pady=3)
            tk.Label(r, text=k, width=14, anchor="w", font=FONT_B, bg=SOFT, fg=DARK).pack(side="left")
            tk.Label(r, text=v, font=FONT, bg=SOFT, fg=TEXT).pack(side="left")
        self.nav(next_text="💖 ยืนยันการจอง", next_cmd=self.confirm)

    def confirm(self):
        s = self.service
        staff_id = self.staff_map.get(self.staff_choice.get())
        free = self.db.free_staff(self.day, to_min(self.time), s["duration"], staff_id)
        if not free:
            messagebox.showwarning("ขออภัยค่ะ", "คิวช่วงเวลานี้เพิ่งถูกจองไปแล้ว กรุณาเลือกเวลาใหม่นะคะ 🌷")
            self.time, self.step = None, 1
            return self.render()
        bid = self.db.create_booking(self.name.get().strip(), self.phone.get().strip(),
                                     s["id"], free[0], self.day, self.time)
        self.done = bid
        self.render()

    def show_success(self):
        s = self.service
        tk.Label(self.body, text="🎉", font=("Segoe UI Emoji", 44), bg=WHITE).pack(pady=(20, 0))
        tk.Label(self.body, text="จองคิวสำเร็จแล้วค่ะ!", font=FONT_T, bg=WHITE, fg=DARK).pack()
        tk.Label(self.body, text=f"หมายเลขการจอง #{self.done}\n\n"
                                 f"{s['name']}\n{th_date(self.day)}  เวลา {self.time} น.\n\n"
                                 "ไว้พบกันนะคะ 💗\n(เช็ก/ยกเลิกคิวได้ที่เมนู \"เช็กการจอง\" ด้วยเบอร์โทรของคุณ)",
                 font=FONT, bg=WHITE, fg=TEXT, justify="center").pack(pady=10)
        bar = tk.Frame(self.body, bg=WHITE)
        bar.pack(pady=6)
        pink_button(bar, "🏠 กลับหน้าร้าน", lambda: self.go("home"), bg=ACTIVE, fg=DARK,
                    hover="#F3AFCB").pack(side="left", padx=6)
        pink_button(bar, "➕ จองเพิ่ม", self.again).pack(side="left", padx=6)

    def again(self):
        self.reset()
        self.render()
