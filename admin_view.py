import tkinter as tk

from theme import *
from widgets import pink_button, F
from crud_page import CrudPage
from dashboard import Dashboard


class AdminView(tk.Frame):
    def __init__(self, parent, db, on_logout, on_pin, logo):
        super().__init__(parent, bg=BG)
        self.db = db
        top = tk.Frame(self, bg=SIDEBAR, height=66)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        if logo:
            tk.Label(top, image=logo, bg=SIDEBAR).pack(side="left", padx=(18, 10), pady=10)
        else:
            tk.Label(top, text="👑", font=("Segoe UI Emoji", 20), bg=SIDEBAR
                     ).pack(side="left", padx=(18, 10))
        self.page_title = tk.Label(top, text="", font=("Tahoma", 15, "bold"), bg=SIDEBAR, fg=DARK)
        self.page_title.pack(side="left")
        tk.Label(top, text="Beauty Queen", font=BRAND, bg=SIDEBAR, fg=PINK
                 ).place(relx=0.5, rely=0.5, anchor="center")
        pink_button(top, "🏪 ออกไปหน้าร้านลูกค้า", on_logout, bg=WHITE, fg=DARK, hover=ACTIVE
                    ).pack(side="right", padx=20)
        tk.Label(top, text="💁 โหมดเจ้าของร้าน", font=FONT_B, bg=SIDEBAR, fg=TEXT
                 ).pack(side="right")
        tk.Frame(self, bg=BORDER, height=1).pack(side="top", fill="x")

        main = tk.Frame(self, bg=BG)
        main.pack(side="top", fill="both", expand=True)
        side = tk.Frame(main, bg=SIDEBAR, width=215)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        self.container = tk.Frame(main, bg=BG)
        self.container.pack(side="left", fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.pages, self.nav = {}, {}

        d = db
        self.pages["home"] = Dashboard(self.container, d, self.show)
        self.pages["customers"] = CrudPage(
            self.container, d, "ข้อมูลลูกค้า", "👩", "customers",
            [F("name", "ชื่อลูกค้า"), F("phone", "เบอร์โทร"), F("note", "หมายเหตุ", req=False)],
            "SELECT id, name AS ชื่อ, phone AS เบอร์, note AS หมายเหตุ FROM customers",
            [("ชื่อ", 160), ("เบอร์", 130), ("หมายเหตุ", 180)],
            ["ชื่อ", "เบอร์", "หมายเหตุ"], "ORDER BY id DESC")
        self.pages["services"] = CrudPage(
            self.container, d, "บริการและราคา", "💅", "services",
            [F("name", "ชื่อบริการ"), F("price", "ราคา (บาท)", "number"),
             F("duration", "เวลา (นาที)", "number")],
            "SELECT id, name AS บริการ, price AS ราคา, duration AS นาที FROM services",
            [("บริการ", 200), ("ราคา", 100), ("นาที", 100)],
            ["บริการ", "ราคา"], "ORDER BY id")
        self.pages["staff"] = CrudPage(
            self.container, d, "พนักงาน / ช่าง", "💇", "staff",
            [F("name", "ชื่อพนักงาน"), F("phone", "เบอร์โทร"), F("specialty", "ความถนัด", req=False)],
            "SELECT id, name AS ชื่อ, phone AS เบอร์, specialty AS ความถนัด FROM staff",
            [("ชื่อ", 150), ("เบอร์", 130), ("ความถนัด", 180)],
            ["ชื่อ", "ความถนัด"], "ORDER BY id")
        self.pages["appointments"] = CrudPage(
            self.container, d, "นัดหมาย", "📅", "appointments",
            [F("customer_id", "ลูกค้า", "combo",
               lambda: [(r["id"], r["name"]) for r in d.q("SELECT id,name FROM customers ORDER BY name")]),
             F("service_id", "บริการ", "combo",
               lambda: [(r["id"], r["name"]) for r in d.q("SELECT id,name FROM services ORDER BY name")]),
             F("staff_id", "ช่าง", "combo",
               lambda: [(r["id"], r["name"]) for r in d.q("SELECT id,name FROM staff ORDER BY name")]),
             F("date", "วันที่ (ปปปป-ดด-วว)", "date"),
             F("time", "เวลา (ชช:นน)", "time", default="10:00"),
             F("status", "สถานะ", "combo", lambda: [(s, s) for s in STATUS], default=STATUS[0])],
            "SELECT a.id, a.date AS วันที่, a.time AS เวลา, c.name AS ลูกค้า, "
            "s.name AS บริการ, st.name AS ช่าง, s.price AS ราคา, a.status AS สถานะ "
            "FROM appointments a JOIN customers c ON c.id=a.customer_id "
            "JOIN services s ON s.id=a.service_id JOIN staff st ON st.id=a.staff_id",
            [("วันที่", 95), ("เวลา", 60), ("ลูกค้า", 110), ("บริการ", 110),
             ("ช่าง", 90), ("ราคา", 70), ("สถานะ", 100)],
            ["วันที่", "ลูกค้า", "บริการ", "ช่าง", "สถานะ"],
            "ORDER BY วันที่ DESC, เวลา DESC", check=self.check_booking)

        self.titles = {"home": "หน้าหลัก", "appointments": "นัดหมาย", "customers": "ลูกค้า",
                       "services": "บริการและราคา", "staff": "พนักงาน"}
        menu = [("home", "🏠   หน้าหลัก"), ("appointments", "📅   นัดหมาย"),
                ("customers", "👩   ลูกค้า"), ("services", "💅   บริการ"), ("staff", "💇   พนักงาน")]
        tk.Frame(side, bg=SIDEBAR, height=14).pack()
        for key, text in menu:
            self.pages[key].grid(row=0, column=0, sticky="nsew")
            b = tk.Button(side, text=text, anchor="w", font=("Tahoma", 12, "bold"),
                          bg=SIDEBAR, fg=TEXT, relief="flat", bd=0, padx=22, pady=11,
                          activebackground=ACTIVE, activeforeground=DARK, cursor="hand2",
                          command=lambda k=key: self.show(k))
            b.pack(fill="x", padx=12, pady=3)
            self.nav[key] = b
        pink_button(side, "🔑 เปลี่ยนรหัส PIN", on_pin, bg=ACTIVE, fg=DARK, hover="#F3AFCB"
                    ).pack(side="bottom", fill="x", padx=14, pady=(0, 16))
        self.show("home")

    def check_booking(self, v, selected_id):
        """ห้ามจองช่างคนเดิมในช่วงเวลาที่ซ้อนกัน (คิดตามระยะเวลาของบริการ)"""
        if v["status"] == "ยกเลิก":
            return None
        dur = self.db.q("SELECT duration FROM services WHERE id=?", (v["service_id"],))[0]["duration"]
        if self.db.busy(v["staff_id"], v["date"], to_min(v["time"]), dur, selected_id):
            return "ช่างคนนี้มีคิวซ้อนกับช่วงเวลาดังกล่าวแล้วค่ะ"
        return None

    def show(self, key):
        for k, b in self.nav.items():
            b.config(bg=ACTIVE if k == key else SIDEBAR, fg=DARK if k == key else TEXT)
        self.page_title.config(text=self.titles[key])
        self.pages[key].refresh()
        self.pages[key].tkraise()

