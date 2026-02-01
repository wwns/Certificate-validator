"""
Complete build script - tworzy EXE i Installer
"""
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Sprawdz czy wszystkie zaleznosci sa zainstalowane."""
    print("="*60)
    print("Sprawdzanie zaleznosci...")
    print("="*60)
    
    # Sprawdz PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller: OK")
    except ImportError:
        print("❌ PyInstaller nie jest zainstalowany!")
        print("\nInstaluj za pomoca: pip install pyinstaller")
        return False
    
    # Sprawdz NSIS (opcjonalnie)
    nsis_path = r"C:\Program Files (x86)\NSIS\makensis.exe"
    if os.path.exists(nsis_path):
        print("✅ NSIS: OK")
        return True, True  # PyInstaller i NSIS
    else:
        print("⚠️  NSIS nie znaleziony (opcjonalnie)")
        print("   Pobierz z: https://nsis.sourceforge.io/Download")
        print("   Installer bedzie pominiety, tylko EXE zostanie utworzony")
        return True, False  # Tylko PyInstaller

def build_all():
    """Buduj wszystko - EXE i Installer."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Certificate Validator - Complete Build System         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Sprawdz zaleznosci
    deps = check_dependencies()
    if not deps:
        return False
    
    has_pyinstaller, has_nsis = deps if isinstance(deps, tuple) else (deps, False)
    
    if not has_pyinstaller:
        print("\n❌ PyInstaller jest wymagany!")
        return False
    
    # Krok 1: Build EXE
    print("\n" + "="*60)
    print("KROK 1/2: Budowanie EXE...")
    print("="*60)
    
    try:
        result = subprocess.run([sys.executable, "build_exe.py"], check=True)
        print("\n✅ EXE zbudowany pomyslnie!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Blad podczas budowania EXE: {e}")
        return False
    
    # Krok 2: Build Installer (jesli NSIS dostepny)
    if has_nsis:
        print("\n" + "="*60)
        print("KROK 2/2: Budowanie Instalera...")
        print("="*60)
        
        nsis_path = r"C:\Program Files (x86)\NSIS\makensis.exe"
        installer_script = "installer.nsi"
        
        try:
            result = subprocess.run([nsis_path, installer_script], check=True, capture_output=True, text=True)
            print("\n✅ Installer zbudowany pomyslnie!")
            print(f"\n📦 Setup: dist\\CertificateValidator_Setup.exe")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Blad podczas budowania instalera: {e}")
            print(f"Output: {e.output}")
            return False
    else:
        print("\n⚠️  KROK 2/2: Pominieto (NSIS niedostepny)")
    
    # Podsumowanie
    print("\n" + "="*60)
    print("✅ BUILD ZAKOŃCZONY POMYŚLNIE!")
    print("="*60)
    
    dist_dir = Path("dist")
    print("\n📂 Pliki wyjsciowe w folderze: dist/")
    print()
    
    # Lista plikow
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                print(f"   📄 {item.name} ({size_mb:.2f} MB)")
            elif item.is_dir():
                print(f"   📁 {item.name}/")
    
    print("\n" + "="*60)
    print("GOTOWE DO DYSTRYBUCJI:")
    print("="*60)
    if has_nsis:
        print("1. CertificateValidator_Setup.exe - Installer dla uzytkownikow")
    print("2. CertificateValidator_Portable/  - Wersja portable (rozpakuj i uruchom)")
    print("3. CertificateValidator.exe        - Standalone EXE")
    
    return True

if __name__ == '__main__':
    success = build_all()
    
    if success:
        print("\n✅ Wszystko gotowe! Mozesz dystrybuowac pliki z folderu dist/")
        input("\nNacisnij ENTER aby zakonczyc...")
    else:
        print("\n❌ Build zakonczony z bledami!")
        input("\nNacisnij ENTER aby zakonczyc...")
        sys.exit(1)
