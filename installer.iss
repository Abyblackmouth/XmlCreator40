[Setup]
AppName=XmlCreator40
AppVersion=1.0
DefaultDirName={pf}\XmlCreator40
DefaultGroupName=XmlCreator40
OutputDir=output
OutputBaseFilename=XmlCreator40_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=static\favicon.ico

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "static\*"; DestDir: "{app}\static"; Flags: recursesubdirs
Source: "templates\*"; DestDir: "{app}\templates"; Flags: recursesubdirs
Source: "resources\*"; DestDir: "{app}\resources"; Flags: recursesubdirs

[Icons]
Name: "{group}\XmlCreator40"; Filename: "{app}\main.exe"; IconFilename: "{app}\static\favicon.ico"
Name: "{commondesktop}\XmlCreator40"; Filename: "{app}\main.exe"; IconFilename: "{app}\static\favicon.ico"