; สคริปต์สร้างตัวติดตั้ง Beauty Queen (Inno Setup)
; ต้องรัน build_exe.bat ก่อน เพื่อให้มีไฟล์ dist\BeautyQueen.exe

[Setup]
AppName=Beauty Queen
AppVersion=1.0
AppPublisher=Beauty Queen
; ติดตั้งในโฟลเดอร์ของผู้ใช้ (เขียนไฟล์ salon.db ได้โดยไม่ต้องขอสิทธิ์ผู้ดูแล)
PrivilegesRequired=lowest
DefaultDirName={autopf}\BeautyQueen
DefaultGroupName=Beauty Queen
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=BeautyQueen_Setup
SetupIconFile=crown.ico
UninstallDisplayIcon={app}\BeautyQueen.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut (สร้างไอคอนบนหน้าจอ)"; GroupDescription: "Shortcuts:"

[Files]
Source: "dist\BeautyQueen.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Beauty Queen"; Filename: "{app}\BeautyQueen.exe"
Name: "{autodesktop}\Beauty Queen"; Filename: "{app}\BeautyQueen.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\BeautyQueen.exe"; Description: "Open Beauty Queen now (เปิดแอปเลย)"; Flags: nowait postinstall skipifsilent
