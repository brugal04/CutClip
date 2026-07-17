#define MyAppName "CutClip"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Bryant Brugal"
#define MyAppURL ""
#define MyAppExeName "CutClip.exe"
#define MyAppDescription "Instant Replay Manager compatible con OBS Studio"

[Setup]
AppId={{8A9E40C0-43FD-44AB-9E21-6A41CC1D8F03}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppComments=Aplicacion independiente compatible con OBS Studio. No afiliada, patrocinada ni respaldada por OBS Studio.
VersionInfoVersion=1.0.1.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2026 Bryant Brugal
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=CutClip_Setup_v1.0.1
SetupIconFile=..\assets\cutclip.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no
AllowNoIcons=yes
ShowLanguageDialog=no
LicenseFile=LICENSE.txt
InfoBeforeFile=INFO_BEFORE.txt
InfoAfterFile=INFO_AFTER.txt

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked
Name: "startup"; Description: "Iniciar CutClip automaticamente con Windows"; GroupDescription: "Inicio automatico:"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\tools\ffmpeg\ffmpeg.exe"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion
Source: "..\tools\ffmpeg\FFMPEG_*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion skipifsourcedoesntexist
Source: "..\docs\GUIA_INSTALACION_Y_CONFIGURACION_v1.0.1.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\CHANGELOG_v1.0.1.md"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--silent"; WorkingDir: "{app}"; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
