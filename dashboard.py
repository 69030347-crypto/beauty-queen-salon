import tkinter as tk
from datetime import datetime, date

from theme import *
from widgets import Card, LineChart, pink_button, clear_children


class Dashboard(tk.Frame):
    def __init__(self, parent, db, go):
        super().__init__(parent, bg=BG)
        self.db, self.go = db, go
        self.greet = tk.Label(self, text="", font=("Tahoma", 15, "bold"), bg=BG, fg=DARK)
        self.greet.pack(anchor="w", padx=28, pady=(16, 6))
        grid = tk.Frame(self, bg=BG)
        grid.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        for c in range(4):
            grid.columnconfigure(c, weight=1, uniform="col")
        grid.rowconfigure(1, weight=1)

        self.stat = {}
        for c, (key, title, emoji) in enumerate([
                ("revenue", "รายได้เดือนนี้", "💰"), ("customers", "ลูกค้าทั้งหมด", "👩"),
                ("today", "นัดหมายวันนี้", "📅"), ("top", "บริการยอดนิยม", "🌟")]):
            card = Card(grid, height=112)
            card.grid(row=0, column=c, sticky="nsew", padx=6, pady=6)
            inner = card.inner
            inner.columnconfigure(0, weight=1)
            left = tk.Frame(inner, bg=WHITE)
            left.grid(row=0, column=0, sticky="w")
            tk.Label(left, text=title, font=FONT, bg=WHITE, fg=TEXT).pack(anchor="w")
            val = tk.Label(left, text="-", font=FONT_BIG, bg=WHITE, fg=TEXT)
            val.pack(anchor="w")
            sub = tk.Label(left, text="", font=FONT_S, bg=WHITE, fg=GREEN)
            sub.pack(anchor="w")
            tk.Label(inner, text=emoji, font=EMOJI, bg=WHITE).grid(row=0, column=1, sticky="e")
            self.stat[key] = (val, sub)

        up = Card(grid, height=250)
        up.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        tk.Label(up.inner, text="💗 นัดหมายที่จะถึง", font=FONT_B, bg=WHITE, fg=TEXT
                 ).pack(anchor="w", pady=(0, 8))
        self.up_list = tk.Frame(up.inner, bg=WHITE)
        self.up_list.pack(fill="both", expand=True)

        ch = Card(grid, height=250)
        ch.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=6, pady=6)
        tk.Label(ch.inner, text="📈 รายได้ย้อนหลัง 6 เดือน", font=FONT_B, bg=WHITE, fg=TEXT
                 ).pack(anchor="w")
        self.chart = LineChart(ch.inner)
        self.chart.pack(fill="both", expand=True)

        fun = Card(grid, height=165)
        fun.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        tk.Label(fun.inner, text="🎀 สรุปสถานะนัดหมาย", font=FONT_B, bg=WHITE, fg=TEXT
                 ).pack(anchor="w", pady=(0, 8))
        tiles = tk.Frame(fun.inner, bg=WHITE)
        tiles.pack(fill="x")
        self.tiles = {}
        for i, (key, emoji, label) in enumerate([
                ("all", "📋", "ทั้งหมด"), ("wait", "⏳", "รอดำเนินการ"),
                ("done", "✅", "เสร็จสิ้น"), ("cancel", "💔", "ยกเลิก")]):
            tiles.columnconfigure(i, weight=1)
            t = tk.Frame(tiles, bg=SOFT, padx=6, pady=8)
            t.grid(row=0, column=i, padx=4, sticky="nsew")
            n = tk.Label(t, text="0", font=("Tahoma", 16, "bold"), bg=SOFT, fg=DARK)
            n.pack()
            tk.Label(t, text=f"{emoji} {label}", font=FONT_S, bg=SOFT, fg=TEXT).pack()
            self.tiles[key] = n

        right = tk.Frame(grid, bg=BG)
        right.grid(row=2, column=2, columnspan=2, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure((0, 1), weight=1)
        qa = Card(right, height=95)
        qa.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6, 3))
        qa.inner.columnconfigure((0, 1, 2), weight=1)
        for i, (text, key) in enumerate([("➕ เพิ่มนัดหมาย", "appointments"),
                                         ("👩 เพิ่มลูกค้า", "customers"),
                                         ("💅 เพิ่มบริการ", "services")]):
            pink_button(qa.inner, text, lambda k=key: self.go(k), bg=ACTIVE, fg=DARK,
                        hover="#F3AFCB").grid(row=0, column=i, padx=4, pady=8, sticky="ew")
        qt = Card(right, height=75, fill="#FFEFF4")
        qt.grid(row=1, column=0, sticky="nsew", padx=6, pady=(3, 6))
        tk.Label(qt.inner, text="✨ ทุกยิ้มของลูกค้า คือกำลังใจของเรา", font=FONT_B,
                 bg="#FFEFF4", fg=DARK).pack(anchor="w")
        tk.Label(qt.inner, text="วันนี้ก็สวยและปังในแบบของตัวเองนะคะ 💗", font=FONT_S,
                 bg="#FFEFF4", fg=TEXT).pack(anchor="w")

    def month_key(self, offset):
        t = date.today()
        y, m = t.year, t.month - offset
        while m <= 0:
            m += 12
            y -= 1
        return y, m

    def refresh(self):
        today = date.today()
        h = datetime.now().hour
        hello = "สวัสดีตอนเช้า" if h < 12 else "สวัสดีตอนบ่าย" if h < 17 else "สวัสดีตอนเย็น"
        self.greet.config(text=f"{hello} 💗  ร้านของคุณกำลังเบ่งบานนะคะ!")
        rows = self.db.q(
            "SELECT substr(a.date,1,7) AS m, SUM(s.price) AS r FROM appointments a "
            "JOIN services s ON s.id=a.service_id WHERE a.status='เสร็จสิ้น' GROUP BY m")
        by_month = {r["m"]: r["r"] for r in rows}
        keys = [self.month_key(i) for i in range(5, -1, -1)]
        values = [by_month.get(f"{y}-{m:02d}", 0) for y, m in keys]
        self.chart.set_data([TH_MONTHS[m - 1] for _, m in keys], values)

        cur, prev = values[-1], values[-2]
        val, sub = self.stat["revenue"]
        val.config(text=f"฿{cur:,.0f}")
        if prev > 0:
            pct = (cur - prev) / prev * 100
            sub.config(text=f"{'▲' if pct >= 0 else '▼'} {abs(pct):.0f}% จากเดือนก่อน",
                       fg=GREEN if pct >= 0 else "#D9534F")
        else:
            sub.config(text="เริ่มนับรายได้เดือนนี้ 🌸", fg=MUTED)

        n_cus = self.db.q("SELECT COUNT(*) AS n FROM customers")[0]["n"]
        self.stat["customers"][0].config(text=str(n_cus))
        self.stat["customers"][1].config(text="ลูกค้าในระบบ", fg=MUTED)
        n_today = self.db.q(
            "SELECT COUNT(*) AS n FROM appointments WHERE date=? AND status!='ยกเลิก'",
            (today.isoformat(),))[0]["n"]
        self.stat["today"][0].config(text=str(n_today))
        self.stat["today"][1].config(text="คิวของวันนี้", fg=MUTED)
        top = self.db.q(
            "SELECT s.name, COUNT(*) AS c FROM appointments a "
            "JOIN services s ON s.id=a.service_id WHERE a.status!='ยกเลิก' "
            "GROUP BY s.id ORDER BY c DESC LIMIT 1")
        self.stat["top"][0].config(text=top[0]["name"] if top else "-", font=("Tahoma", 17, "bold"))
        self.stat["top"][1].config(text=f"ใช้บริการ {top[0]['c']} ครั้ง" if top else "", fg=MUTED)

        cnt = {r["status"]: r["n"] for r in self.db.q(
            "SELECT status, COUNT(*) AS n FROM appointments GROUP BY status")}
        self.tiles["all"].config(text=str(sum(cnt.values())))
        self.tiles["wait"].config(text=str(cnt.get(STATUS[0], 0)))
        self.tiles["done"].config(text=str(cnt.get(STATUS[1], 0)))
        self.tiles["cancel"].config(text=str(cnt.get(STATUS[2], 0)))

        clear_children(self.up_list)
        ups = self.db.q(
            "SELECT c.name AS cn, s.name AS sn, a.date, a.time, a.status FROM appointments a "
            "JOIN customers c ON c.id=a.customer_id JOIN services s ON s.id=a.service_id "
            "WHERE a.date>=? AND a.status='รอดำเนินการ' ORDER BY a.date, a.time LIMIT 4",
            (today.isoformat(),))
        if not ups:
            tk.Label(self.up_list, text="ยังไม่มีนัดหมายที่จะถึง 🌷", font=FONT, bg=WHITE,
                     fg=MUTED).pack(pady=20)
        flowers = ["🌸", "🌷", "🌼", "💮"]
        for i, r in enumerate(ups):
            row = tk.Frame(self.up_list, bg=SOFT, padx=10, pady=6)
            row.pack(fill="x", pady=3)
            row.columnconfigure(1, weight=1)
            av = tk.Canvas(row, width=38, height=38, bg=SOFT, highlightthickness=0)
            av.create_oval(2, 2, 36, 36, fill=ACTIVE, outline="")
            av.create_text(19, 19, text=flowers[i % 4], font=("Segoe UI Emoji", 13))
            av.grid(row=0, column=0, rowspan=2, padx=(0, 10))
            tk.Label(row, text=r["cn"], font=FONT_B, bg=SOFT, fg=TEXT).grid(row=0, column=1, sticky="w")
            tk.Label(row, text=r["sn"], font=FONT_S, bg=SOFT, fg=MUTED).grid(row=1, column=1, sticky="w")
            d = r["date"]
            tk.Label(row, text=f"{d[8:10]}/{d[5:7]}  {r['time']} น.", font=FONT_S,
                     bg=SOFT, fg=TEXT).grid(row=0, column=2, sticky="e")
            bgc, fgc = STATUS_COLORS[r["status"]]
            tk.Label(row, text=r["status"], font=FONT_S, bg=bgc, fg=fgc, padx=8
                     ).grid(row=1, column=2, sticky="e")

