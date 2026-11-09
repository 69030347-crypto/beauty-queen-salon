import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from theme import *
from widgets import make_crown
from database import DB
from customer_view import CustomerView
from admin_view import AdminView


# ================================================================ MAIN APP
class SalonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💖 Beauty Queen - ร้านเสริมสวย")
        self.geometry("1200x740")
        self.minsize(1050, 680)
        self.configure(bg=BG)
        self.set_icon()
        self.db = DB(DB_PATH)
        self.setup_style()
        self.logo = None
        if ICON_B64:
            try:
                self.logo = tk.PhotoImage(data=ICON_B64).subsample(3)
            except tk.TclError:
                self.logo = None
        if self.logo is None:
            self.logo = make_crown(44)
        self.customer = CustomerView(self, self.db, self.admin_login, self.logo)
        self.admin = None
        self.customer.pack(fill="both", expand=True)

    def admin_login(self):
        pin = simpledialog.askstring("เข้าสู่ระบบเจ้าของร้าน 🔐",
                                     "กรุณาใส่รหัส PIN ของเจ้าของร้านค่ะ\n(รหัสเริ่มต้น: 1234)",
                                     show="*", parent=self)
        if pin is None:
            return
        real = self.db.q("SELECT value FROM settings WHERE key='pin'")[0]["value"]
        if pin != real:
            messagebox.showerror("รหัสไม่ถูกต้อง", "รหัส PIN ไม่ถูกต้องค่ะ")
            return
        if self.admin is None:
            self.admin = AdminView(self, self.db, self.go_store, self.change_pin, self.logo)
        else:
            self.admin.show("home")
        self.customer.pack_forget()
        self.admin.pack(fill="both", expand=True)

    def go_store(self):
        self.admin.pack_forget()
        self.customer.pack(fill="both", expand=True)
        self.customer.show("home")

    def change_pin(self):
        new = simpledialog.askstring("เปลี่ยนรหัส PIN", "ตั้งรหัส PIN ใหม่ (ตัวเลข 4 หลักขึ้นไป)",
                                     show="*", parent=self)
        if new is None:
            return
        if not new.isdigit() or len(new) < 4:
            messagebox.showwarning("รหัสไม่ถูกต้อง", "รหัส PIN ต้องเป็นตัวเลขอย่างน้อย 4 หลักค่ะ")
            return
        self.db.x("UPDATE settings SET value=? WHERE key='pin'", (new,))
        messagebox.showinfo("สำเร็จ", "เปลี่ยนรหัส PIN เรียบร้อยแล้วค่ะ 💖")

    def setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                    foreground=TEXT, rowheight=32, font=FONT, borderwidth=0)
        s.configure("Treeview.Heading", background="#F9D5E3", foreground=DARK,
                    font=FONT_B, relief="flat", padding=7)
        s.map("Treeview.Heading", background=[("active", ACTIVE)])
        s.map("Treeview", background=[("selected", ACTIVE)], foreground=[("selected", DARK)])
        s.configure("TCombobox", fieldbackground=SOFT, background=ACTIVE,
                    foreground=TEXT, arrowcolor=DARK, bordercolor=BORDER)
        s.configure("Vertical.TScrollbar", background=ACTIVE, troughcolor=SOFT,
                    arrowcolor=DARK, bordercolor=SOFT)

    def set_icon(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("beautyqueen.salon.app")
        except Exception:
            pass
        img = None
        if ICON_B64:
            try:
                img = tk.PhotoImage(data=ICON_B64)
            except tk.TclError:
                img = None
        if img is None:
            img = make_crown(64)
        self.iconphoto(True, img)
        self._icon = img


if __name__ == "__main__":
    SalonApp().mainloop()

