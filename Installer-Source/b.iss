; ===================================================================
;  Inno Setup Script for ZamanSanj Application
; ===================================================================

#define MyAppName "ZamanSanj"
#define MyAppVersion "1.0"
#define MyAppPublisher "Davoudi"
#define MyAppExeName "main.exe"

[Setup]
AppId={{E04977C6-A88A-42F6-90D7-7A24453113BB} ; یک شناسه منحصر به فرد برای برنامه شما
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=setup-zamansanj
SetupIconFile=clock.ico
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
; فایل اجرایی اصلی برنامه شما
Source: "{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; فایل فونت که باید به صورت خودکار نصب شود
Source: "Vazirmatn-Regular.ttf"; DestDir: "{autofonts}"; FontInstall: "Vazirmatn Regular"; Flags: onlyifdoesntexist uninsneveruninstall

; فایل آیکون برای استفاده در شورتکات‌ها و بخش حذف برنامه
Source: "clock.ico"; DestDir: "{app}";

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\clock.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\*"