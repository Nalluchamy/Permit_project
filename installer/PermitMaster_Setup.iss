; ==============================================================================
; PermitMaster — Windows Inno Setup Compiler Script
; App Name: PermitMaster
; App Version: 1.0.0
; ==============================================================================

[Setup]
AppId={{8F4C5C0E-921A-4C2B-9831-29A887E8E101}
AppName=PermitMaster
AppVersion=1.0.0
AppPublisher=Tamil Nadu Mining Dispatch Systems
AppPublisherURL=https://cheery-sherbet-91f7c4.netlify.app/
AppSupportURL=https://cheery-sherbet-91f7c4.netlify.app/
AppUpdatesURL=https://cheery-sherbet-91f7c4.netlify.app/
DefaultDirName={autopf}\PermitMaster
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=..\installer_output
OutputBaseFilename=PermitMaster_v1.0.0_Setup
SetupIconFile=..\permit_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\PermitMaster.exe
UninstallDisplayName=PermitMaster TN Mining Dispatch System

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\PermitMaster.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\PermitMaster"; Filename: "{app}\PermitMaster.exe"; IconFilename: "{app}\PermitMaster.exe"
Name: "{autodesktop}\PermitMaster"; Filename: "{app}\PermitMaster.exe"; Tasks: desktopicon; IconFilename: "{app}\PermitMaster.exe"

[Run]
Filename: "{app}\PermitMaster.exe"; Description: "{cm:LaunchProgram,PermitMaster}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up binary files only. Preserves user data in %LOCALAPPDATA%\PermitMaster\
Type: filesandordirs; Name: "{app}"

[Code]
// Custom Inno Setup logic to ensure %LOCALAPPDATA%\PermitMaster\ directory is created safely
procedure InitializeWizard;
var
  AppDataDir: String;
begin
  AppDataDir := ExpandConstant('{userlocalappdata}\PermitMaster');
  if not DirExists(AppDataDir) then
  begin
    CreateDir(AppDataDir);
    CreateDir(AppDataDir + '\logs');
    CreateDir(AppDataDir + '\backups');
    CreateDir(AppDataDir + '\generated_pdfs');
  end;
end;
