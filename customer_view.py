import tkinter as tk

from theme import *
from widgets import pink_button
from store_home import StoreHome
from booking_page import BookingPage
from my_bookings import MyBookingsPage


class CustomerView(tk.Frame):
    def __init__(self, parent, db, on_admin, logo):
        super().__init__(parent, bg=BG)
        top = tk.Frame(self, bg=SIDEBAR, height=66)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        if logo:
            tk.Label(top, image=logo, bg=SIDEBAR).pack(side="left", padx=(18, 10), pady=10)
        else:
            tk.Label(top, text="👑", font=("Segoe UI Emoji", 20), bg=SIDEBAR
                     ).pack(side="left", padx=(18, 10))
        tk.Label(top, text="Beauty Queen", font=BRAND, bg=SIDEBAR, fg=PINK).pack(side="left")
        pink_button(top, "🔐 เจ้าของร้าน", on_admin, bg=WHITE, fg=DARK, hover=ACTIVE
                    ).pack(side="right", padx=20)
        self.nav = {}
        for key, text in [("check", "🔍 เช็กการจอง"), ("book", "📅 จองคิว"), ("home", "🏠 หน้าร้าน")]:
            b = tk.Button(top, text=text, font=("Tahoma", 12, "bold"), bg=SIDEBAR, fg=TEXT,
                          relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
                          activebackground=ACTIVE, activeforeground=DARK,
                          command=lambda k=key: self.show(k))
            b.pack(side="right", padx=3)
            self.nav[key] = b
        tk.Frame(self, bg=BORDER, height=1).pack(side="top", fill="x")
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.pages = {"home": StoreHome(self.container, db, self.show),
                      "book": BookingPage(self.container, db, self.show),
                      "check": MyBookingsPage(self.container, db, self.show)}
        for p in self.pages.values():
            p.grid(row=0, column=0, sticky="nsew")
        self.show("home")

    def show(self, key):
        for k, b in self.nav.items():
            b.config(bg=ACTIVE if k == key else SIDEBAR, fg=DARK if k == key else TEXT)
        self.pages[key].refresh()
        self.pages[key].tkraise()
