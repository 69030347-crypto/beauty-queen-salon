import sqlite3
import tkinter as tk
from datetime import datetime, date
from tkinter import ttk, messagebox

from theme import *
from widgets import Card, pink_button, soft_entry


class CrudPage(tk.Frame):
    def __init__(self, parent, db, title, icon, table, fields, list_sql,
                 headings, search_cols, order_sql="", check=None):
        super().__init__(parent, bg=BG)
        self.db, self.table, self.fields = db, table, fields
        self.list_sql, self.order_sql = list_sql, order_sql
        self.search_cols, self.check = search_cols, check
        self.selected_id = None
        self.vars, self.widgets, self.maps = {}, {}, {}

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=25, pady=20)
        card = Card(body, width=340)
        card.pack(side="left", fill="y", padx=(0, 15))
        form = card.inner
        tk.Label(form, text=f"{icon} {title}", font=FONT_B, bg=WHITE, fg=PINK
                 ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        for i, f in enumerate(fields, start=1):
            tk.Label(form, text=f["label"], font=FONT, bg=WHITE, fg=TEXT
                     ).grid(row=i, column=0, sticky="w", pady=6, padx=(0, 10))
            var = tk.StringVar()
            self.vars[f["key"]] = var
            if f["kind"] == "combo":
                w = ttk.Combobox(form, textvariable=var, state="readonly", width=23, font=FONT)
            else:
                w = soft_entry(form, var)
            w.grid(row=i, column=1, pady=6, ipady=3)
            self.widgets[f["key"]] = w

        btns = tk.Frame(form, bg=WHITE)
        btns.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(18, 0))
        pink_button(btns, "➕ เพิ่ม", self.add).grid(row=0, column=0, padx=4, pady=4)
        pink_button(btns, "💾 แก้ไข", self.save_edit, bg="#C79BE0", hover="#A878C4"
                    ).grid(row=0, column=1, padx=4, pady=4)
        pink_button(btns, "🗑️ ลบ", self.delete_row, bg="#F29AB5", hover="#D9708F"
                    ).grid(row=1, column=0, padx=4, pady=4)
        pink_button(btns, "🧹 ล้างฟอร์ม", self.clear, bg="#F5B8CC", fg=DARK, hover="#F0A2BC"
                    ).grid(row=1, column=1, padx=4, pady=4)

        right = Card(body)
        right.pack(side="left", fill="both", expand=True)
        box = right.inner
        sbar = tk.Frame(box, bg=WHITE)
        sbar.pack(fill="x", pady=(0, 10))
        tk.Label(sbar, text="🔍 ค้นหา", font=FONT_B, bg=WHITE, fg=DARK).pack(side="left")
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self.load_table())
        soft_entry(sbar, self.search).pack(side="left", padx=10, ipady=4, fill="x", expand=True)

        cols = ["id"] + [h[0] for h in headings]
        tree_frame = tk.Frame(box, bg=WHITE)
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                 displaycolumns=cols[1:], selectmode="browse")
        for text, width in headings:
            self.tree.heading(text, text=text)
            self.tree.column(text, width=width, anchor="center")
        self.tree.tag_configure("odd", background="#FFF6F9")
        sc = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.clear()

    def refresh(self):
        for f in self.fields:
            if f["kind"] == "combo":
                pairs = f["opts"]()
                self.maps[f["key"]] = {label: val for val, label in pairs}
                self.widgets[f["key"]]["values"] = [label for _, label in pairs]
        self.load_table()

    def load_table(self):
        self.tree.delete(*self.tree.get_children())
        sql, params = f"SELECT * FROM ({self.list_sql})", []
        kw = self.search.get().strip()
        if kw:
            sql += " WHERE " + " OR ".join(f"{c} LIKE ?" for c in self.search_cols)
            params = [f"%{kw}%"] * len(self.search_cols)
        sql += " " + self.order_sql
        for i, row in enumerate(self.db.q(sql, params)):
            self.tree.insert("", "end", values=tuple(row), tags=("odd",) if i % 2 else ())

    def on_select(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_id = self.tree.item(sel[0])["values"][0]
        row = self.db.q(f"SELECT * FROM {self.table} WHERE id=?", (self.selected_id,))[0]
        for f in self.fields:
            val = row[f["key"]]
            if f["kind"] == "combo":
                rev = {v: l for l, v in self.maps[f["key"]].items()}
                val = rev.get(val, "")
            self.vars[f["key"]].set("" if val is None else val)

    def clear(self):
        self.selected_id = None
        for f in self.fields:
            d = f["default"]
            if f["kind"] == "date" and not d:
                d = date.today().isoformat()
            self.vars[f["key"]].set(d() if callable(d) else d)
        if hasattr(self, "tree"):
            self.tree.selection_remove(self.tree.selection())

    def get_values(self):
        values = {}
        for f in self.fields:
            v = self.vars[f["key"]].get().strip()
            if not v and f["req"]:
                messagebox.showwarning("ข้อมูลไม่ครบ", f"กรุณากรอก \"{f['label']}\" ค่ะ")
                return None
            try:
                if f["kind"] == "combo":
                    v = self.maps[f["key"]].get(v)
                elif f["kind"] == "number":
                    n = float(v)
                    v = int(n) if n.is_integer() else n
                elif f["kind"] == "date":
                    datetime.strptime(v, "%Y-%m-%d")
                elif f["kind"] == "time":
                    v = datetime.strptime(v, "%H:%M").strftime("%H:%M")
            except ValueError:
                hint = {"number": "ตัวเลข", "date": "วันที่ รูปแบบ ปปปป-ดด-วว",
                        "time": "เวลา รูปแบบ ชช:นน"}.get(f["kind"], "ถูกต้อง")
                messagebox.showwarning("รูปแบบไม่ถูกต้อง", f"\"{f['label']}\" ต้องเป็น{hint}ค่ะ")
                return None
            values[f["key"]] = v
        if self.check:
            err = self.check(values, self.selected_id)
            if err:
                messagebox.showwarning("ไม่สามารถบันทึกได้", err)
                return None
        return values

    def add(self):
        v = self.get_values()
        if v is None:
            return
        self.db.x(f"INSERT INTO {self.table}({','.join(v)}) VALUES({','.join('?' * len(v))})",
                  list(v.values()))
        self.clear()
        self.load_table()
        messagebox.showinfo("สำเร็จ", "เพิ่มข้อมูลเรียบร้อยแล้วค่ะ 💖")

    def save_edit(self):  # (เดิมชื่อ update ซึ่งไปชนกับเมธอด update() ของ Tkinter จึงเปลี่ยนชื่อ)
        if self.selected_id is None:
            messagebox.showinfo("เลือกข้อมูล", "กรุณาเลือกแถวที่ต้องการแก้ไขก่อนนะคะ")
            return
        v = self.get_values()
        if v is None:
            return
        sets = ",".join(f"{k}=?" for k in v)
        self.db.x(f"UPDATE {self.table} SET {sets} WHERE id=?",
                  list(v.values()) + [self.selected_id])
        self.clear()
        self.load_table()
        messagebox.showinfo("สำเร็จ", "แก้ไขข้อมูลเรียบร้อยแล้วค่ะ ✨")

    def delete_row(self):
        if self.selected_id is None:
            messagebox.showinfo("เลือกข้อมูล", "กรุณาเลือกแถวที่ต้องการลบก่อนนะคะ")
            return
        if not messagebox.askyesno("ยืนยัน", "ต้องการลบข้อมูลนี้ใช่ไหมคะ?"):
            return
        try:
            self.db.x(f"DELETE FROM {self.table} WHERE id=?", (self.selected_id,))
        except sqlite3.IntegrityError:
            messagebox.showerror("ลบไม่ได้", "ข้อมูลนี้ถูกใช้อยู่ในรายการนัดหมาย จึงลบไม่ได้ค่ะ")
            return
        self.clear()
        self.load_table()

