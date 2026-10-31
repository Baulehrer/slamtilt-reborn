Unicode true
SetCompressor /SOLID lzma
!include "MUI2.nsh"
Name "Slamtilt - Reborn"
VIProductVersion "1.2.0.0"
VIAddVersionKey "ProductName" "Slamtilt - Reborn"
VIAddVersionKey "ProductVersion" "1.2"
VIAddVersionKey "FileVersion" "1.2.0.0"
VIAddVersionKey "FileDescription" "Slamtilt - Reborn Installer"
VIAddVersionKey "LegalCopyright" "Slamtilt - Reborn contributors"
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Programs\Slamtilt Reborn"
RequestExecutionLevel user
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section "Slamtilt - Reborn"
 SetOutPath "$INSTDIR"
 File /r "${STAGE}/*"
 WriteUninstaller "$INSTDIR\Uninstall.exe"
 CreateDirectory "$SMPROGRAMS\Slamtilt Reborn"
 CreateShortCut "$SMPROGRAMS\Slamtilt Reborn\Slamtilt Reborn.lnk" "$INSTDIR\bin\slamtilt.exe"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn" "DisplayName" "Slamtilt - Reborn"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn" "DisplayVersion" "1.2"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
 WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn" "NoModify" 1
 WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn" "NoRepair" 1
SectionEnd
Section "Uninstall"
 Delete "$SMPROGRAMS\Slamtilt Reborn\Slamtilt Reborn.lnk"
 RMDir "$SMPROGRAMS\Slamtilt Reborn"
 RMDir /r "$INSTDIR\bin"
 RMDir /r "$INSTDIR\share"
 RMDir /r "$INSTDIR\LICENSES"
 Delete "$INSTDIR\README.txt"
 Delete "$INSTDIR\windows-bundle.json"
 Delete "$INSTDIR\Uninstall.exe"
 RMDir "$INSTDIR"
 DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn"
SectionEnd
