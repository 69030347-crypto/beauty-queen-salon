import os
import sys
from datetime import date


# ---------------------------------------------------------------- THEME
BG = "#FDF0F5"
SIDEBAR = "#FCE4EE"
ACTIVE = "#F8C8DC"
PINK = "#E8739A"
DARK = "#B94A74"
SOFT = "#FFF5F8"
BORDER = "#F9D9E6"
SHADOW = "#F7E1EA"
WHITE = "#FFFFFF"
TEXT = "#6B3A50"
MUTED = "#B58BA0"
GREEN = "#38A169"
GREY = "#EDE7EB"

FONT = ("Tahoma", 11)
FONT_B = ("Tahoma", 11, "bold")
FONT_S = ("Tahoma", 9)
FONT_T = ("Tahoma", 18, "bold")
FONT_BIG = ("Tahoma", 24, "bold")
EMOJI = ("Segoe UI Emoji", 26)
BRAND = ("Segoe Script", 22, "bold")

STATUS = ["รอดำเนินการ", "เสร็จสิ้น", "ยกเลิก"]
STATUS_COLORS = {
    "รอดำเนินการ": ("#FFF1D6", "#B7791F"),
    "เสร็จสิ้น": ("#DDF3E4", "#2F855A"),
    "ยกเลิก": ("#EDE7EB", "#8A7480"),
}
TH_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
             "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
WEEK = ["จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส.", "อา."]

OPEN_MIN, CLOSE_MIN, STEP_MIN, BOOK_DAYS = 10 * 60, 19 * 60, 30, 14  # เปิด 10:00-19:00

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "salon.db")

# ไอคอนแอป: ถ้ามีข้อความ base64 รูปมงกุฎเดิมของคุณ ให้วางไว้ในเครื่องหมายคำพูดด้านล่างนี้
# (ถ้าปล่อยว่างไว้ แอปจะใช้อีโมจิ 👑 แทน ใช้งานได้ปกติ)
ICON_B64 = ""


def to_min(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def fmt_min(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def th_date(iso):
    d = date.fromisoformat(iso)
    return f"{WEEK[d.weekday()]} {d.day} {TH_MONTHS[d.month - 1]} {d.year + 543}"


def clean_phone(p):
    return "".join(ch for ch in p if ch.isdigit())
