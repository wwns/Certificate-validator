"""
Installer Builder for Certificate Validator
Tworzy instalator Windows z NSIS
"""
import os
import shutil
from pathlib import Path

def create_installer_script():
    """Tworzy skrypt NSIS dla instalatora."""
    
    nsis_script = r"""
; Certificate Validator Installer Script
; Requires NSIS (Nullsoft Scriptable Install System)

!include "MUI2.nsh"

; Podstawowe informacje
Name "Certificate Validator"
OutFile "CertificateValidator_Setup_v1.0.0.exe"
InstallDir "$PROGRAMFILES64\CertificateValidator"
InstallDirRegKey HKLM "Software\CertificateValidator" "Install_Dir"
RequestExecutionLevel admin

; Interfejs
!define MUI_ABORTWARNING
!define MUI_ICON "icons\paloalto.ico"
!define MUI_UNICON "icons\paloalto.ico"

; Strony
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Jezyki
!insertmacro MUI_LANGUAGE "English"

; Sekcje instalacji
Section "Certificate Validator (required)" SecMain
  SectionIn RO
  
  SetOutPath $INSTDIR
  
  ; Pliki aplikacji
  File "dist\CertificateValidator.exe"
  File "README.md"
  File "LICENSE.txt"
  
  ; Ikony
  SetOutPath "$INSTDIR\icons"
  File "icons\paloalto.ico"
  File "icons\paloalto.png"
  
  ; Rejestr
  WriteRegStr HKLM "Software\CertificateValidator" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator" "DisplayName" "Certificate Validator"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator" "NoRepair" 1
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator" "DisplayIcon" "$INSTDIR\icons\paloalto.ico"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator" "Publisher" "Certificate Validator"
  
  ; Uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Skroty
  CreateDirectory "$SMPROGRAMS\Certificate Validator"
  CreateShortcut "$SMPROGRAMS\Certificate Validator\Certificate Validator.lnk" "$INSTDIR\CertificateValidator.exe" "" "$INSTDIR\icons\paloalto.ico"
  CreateShortcut "$SMPROGRAMS\Certificate Validator\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortcut "$DESKTOP\Certificate Validator.lnk" "$INSTDIR\CertificateValidator.exe" "" "$INSTDIR\icons\paloalto.ico"
SectionEnd

Section "OpenSSL 3.x (recommended)" SecOpenSSL
  SetOutPath "$INSTDIR\openssl"
  
  ; Tutaj skopiuj OpenSSL jesli dostepny
  ; File /r "openssl\*.*"
  
  DetailPrint "OpenSSL folder created. Please install OpenSSL separately or use portable version."
SectionEnd

; Opisy sekcji
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Main application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecOpenSSL} "OpenSSL directory for certificate operations"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Deinstalacja
Section "Uninstall"
  ; Usun pliki
  Delete "$INSTDIR\CertificateValidator.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\icons\paloalto.ico"
  Delete "$INSTDIR\icons\paloalto.png"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Usun katalogi
  RMDir "$INSTDIR\icons"
  RMDir /r "$INSTDIR\openssl"
  RMDir "$INSTDIR"
  
  ; Usun skroty
  Delete "$SMPROGRAMS\Certificate Validator\*.*"
  Delete "$DESKTOP\Certificate Validator.lnk"
  RMDir "$SMPROGRAMS\Certificate Validator"
  
  ; Usun z rejestru
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CertificateValidator"
  DeleteRegKey HKLM "Software\CertificateValidator"
SectionEnd
"""
    
    output_path = Path("installer.nsi")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print(f"✅ Skrypt NSIS utworzony: {output_path}")
    return output_path

def build_installer():
    """Buduje instalator z NSIS."""
    print("\n" + "="*60)
    print("Certificate Validator - Installer Builder")
    print("="*60)
    
    # Sprawdz czy NSIS jest zainstalowany
    nsis_path = Path("C:/Program Files (x86)/NSIS/makensis.exe")
    if not nsis_path.exists():
        print("\n❌ NSIS nie jest zainstalowany!")
        print("Pobierz z: https://nsis.sourceforge.io/Download")
        return False
    
    # Utworz skrypt
    script_path = create_installer_script()
    
    # Zbuduj instalator
    print(f"\nBudowanie instalatora...")
    import subprocess
    result = subprocess.run(
        [str(nsis_path), str(script_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("\n✅ Instalator utworzony pomyslnie!")
        print(f"📦 Plik: CertificateValidator_Setup_v1.0.0.exe")
        return True
    else:
        print(f"\n❌ Blad budowania instalatora:")
        print(result.stderr)
        return False

if __name__ == '__main__':
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*15 + "Installer Builder" + " "*25 + "║")
    print("╚" + "="*58 + "╝\n")
    
    build_installer()
