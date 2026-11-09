@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === กำลังติดตั้งเครื่องมือ (ต้องต่ออินเทอร์เน็ต) ===
python -m pip install pyinstaller
echo === กำลังสร้างโปรแกรม BeautyQueen.exe รอสักครู่ ===
python -m PyInstaller --onefile --windowed --name BeautyQueen --icon crown.ico salon_app.py
echo.
echo เสร็จแล้ว! เปิดโฟลเดอร์ dist จะเจอไฟล์ BeautyQueen.exe
pause
