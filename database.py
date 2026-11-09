import sqlite3
from datetime import date, timedelta

from theme import STATUS, to_min, clean_phone


class DB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()
        self.seed()

    def create_tables(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            phone TEXT NOT NULL, note TEXT);
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            price REAL NOT NULL CHECK (price >= 0),
            duration INTEGER NOT NULL CHECK (duration > 0));
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            phone TEXT NOT NULL, specialty TEXT);
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
            service_id  INTEGER NOT NULL REFERENCES services(id)  ON DELETE RESTRICT,
            staff_id    INTEGER NOT NULL REFERENCES staff(id)     ON DELETE RESTRICT,
            date TEXT NOT NULL, time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'รอดำเนินการ');
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
        """)
        self.conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('pin','1234')")
        self.conn.commit()

    def seed(self):
        if self.q("SELECT COUNT(*) AS n FROM services")[0]["n"] > 0:
            return
        services = [("ตัดผมหญิง", 300, 45), ("สระไดร์", 200, 40),
                    ("ทำสีผม", 1500, 120), ("ทำเล็บเจล", 500, 60),
                    ("ต่อขนตา", 700, 75), ("ทรีตเมนต์ผม", 800, 60),
                    ("นวดหน้า", 900, 60)]
        staff = [("คุณมิ้นท์", "081-111-1111", "ทำผม"),
                 ("คุณพีช", "082-222-2222", "ทำเล็บ"),
                 ("คุณโรส", "083-333-3333", "ต่อขนตา/สปาหน้า")]
        customers = [("น้องแพรว", "089-000-0001", "แพ้น้ำหอม"),
                     ("คุณใบเตย", "089-000-0002", ""),
                     ("คุณมะลิ", "089-000-0003", "ลูกค้าประจำ")]
        self.conn.executemany("INSERT INTO services(name,price,duration) VALUES(?,?,?)", services)
        self.conn.executemany("INSERT INTO staff(name,phone,specialty) VALUES(?,?,?)", staff)
        self.conn.executemany("INSERT INTO customers(name,phone,note) VALUES(?,?,?)", customers)
        today = date.today()
        past = [170, 150, 140, 120, 110, 95, 80, 70, 55, 45, 35, 28, 20, 12, 6, 3]
        for i, d in enumerate(past):
            self.conn.execute(
                "INSERT INTO appointments(customer_id,service_id,staff_id,date,time,status) "
                "VALUES(?,?,?,?,?,?)",
                (1 + i % 3, 1 + (i * 2) % 7, 1 + i % 3,
                 (today - timedelta(days=d)).isoformat(), f"{10 + i % 7}:00", "เสร็จสิ้น"))
        upcoming = [(0, "16:00", 1, 1, 1), (1, "13:30", 2, 4, 2),
                    (2, "11:00", 3, 5, 3), (4, "15:00", 1, 3, 1)]
        for days, t, c, s, st in upcoming:
            self.conn.execute(
                "INSERT INTO appointments(customer_id,service_id,staff_id,date,time,status) "
                "VALUES(?,?,?,?,?,?)",
                (c, s, st, (today + timedelta(days=days)).isoformat(), t, STATUS[0]))
        self.conn.commit()

    def q(self, sql, params=()):
        return self.conn.execute(sql, params).fetchall()

    def x(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    # ---- ระบบตรวจคิวว่าง (เช็กเวลาซ้อนทับตามระยะเวลาของบริการ)
    def busy(self, staff_id, day, start, dur, exclude_id=None):
        rows = self.q(
            "SELECT a.time, s.duration FROM appointments a JOIN services s ON s.id=a.service_id "
            "WHERE a.staff_id=? AND a.date=? AND a.status!='ยกเลิก' AND a.id!=?",
            (staff_id, day, exclude_id or -1))
        for r in rows:
            st = to_min(r["time"])
            if start < st + r["duration"] and st < start + dur:
                return True
        return False

    def free_staff(self, day, start, dur, staff_id=None):
        ids = [r["id"] for r in self.q("SELECT id FROM staff ORDER BY id")]
        if staff_id is not None:
            ids = [staff_id]
        return [i for i in ids if not self.busy(i, day, start, dur)]

    def create_booking(self, name, phone, service_id, staff_id, day, time):
        key = clean_phone(phone)
        found = [r for r in self.q("SELECT id, phone FROM customers")
                 if clean_phone(r["phone"]) == key]
        if found:
            cid = found[0]["id"]
        else:
            cid = self.x("INSERT INTO customers(name,phone,note) VALUES(?,?,?)",
                         (name, phone, "จองผ่านหน้าร้านออนไลน์")).lastrowid
        return self.x(
            "INSERT INTO appointments(customer_id,service_id,staff_id,date,time,status) "
            "VALUES(?,?,?,?,?,?)", (cid, service_id, staff_id, day, time, STATUS[0])).lastrowid
