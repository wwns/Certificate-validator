"""
Build script for Certificate Validator executable
Tworzy standalone EXE za pomocą PyInstaller
"""
import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_exe():
    """Buduj plik EXE za pomocą PyInstaller."""
    print("="*60)
    print("Building Certificate Validator EXE")
    print("="*60)
    
    # Sciezki
    project_dir = Path(__file__).parent
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    # Wyczysc stare buildy
    if dist_dir.exists():
        print(f"\nCzyszczenie starego dist: {dist_dir}")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print(f"Czyszczenie starego build: {build_dir}")
        shutil.rmtree(build_dir)
    
    print("\n" + "="*60)
    print("Uruchamianie PyInstaller...")
    print("="*60)
    
    # Argumenty PyInstaller
    args = [
        'app.py',                           # Entry point
        '--name=CertificateValidator',      # Nazwa EXE
        '--onefile',                        # Jeden plik EXE
        '--windowed',                       # Bez konsoli (GUI)
        '--clean',                          # Wyczysc cache
        
        # Ikona (jesli istnieje)
        # '--icon=icon.ico',
        
        # Dodatkowe pliki
        '--add-data=cert_manager_core.py;.',
        '--add-data=palo_cert_manager_desktop.py;.',
        
        # Ukryte importy
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.filedialog',
        
        # Opcje
        '--noconfirm',                      # Nie pytaj o nadpisanie
    ]
    
    # Uruchom PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n" + "="*60)
    print("Build zakończony!")
    print("="*60)
    
    exe_path = dist_dir / "CertificateValidator.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ EXE utworzony: {exe_path}")
        print(f"📦 Rozmiar: {size_mb:.2f} MB")
        print(f"\n📂 Lokalizacja: {exe_path.absolute()}")
    else:
        print("\n❌ BŁĄD: EXE nie został utworzony!")
        return False
    
    return True

def create_portable_package():
    """Tworzy portable package z EXE i folderem OpenSSL."""
    print("\n" + "="*60)
    print("Tworzenie portable package...")
    print("="*60)
    
    project_dir = Path(__file__).parent
    dist_dir = project_dir / "dist"
    portable_dir = dist_dir / "CertificateValidator_Portable"
    
    # Utworz folder portable
    portable_dir.mkdir(exist_ok=True)
    
    # Skopiuj EXE
    exe_source = dist_dir / "CertificateValidator.exe"
    exe_dest = portable_dir / "CertificateValidator.exe"
    
    if exe_source.exists():
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Skopiowano EXE do: {portable_dir}")
    
    # Utworz pusty folder openssl (uzytkownik zainstaluje pozniej)
    openssl_dir = portable_dir / "openssl"
    openssl_dir.mkdir(exist_ok=True)
    
    # Utworz README
    readme_path = portable_dir / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("""Certificate Validator - Portable Edition

INSTALACJA:
1. Rozpakuj caly folder w dowolnej lokalizacji
2. Uruchom CertificateValidator.exe
3. Przy pierwszym uruchomieniu kliknij "Sprawdz OpenSSL"
4. Wybierz "TAK" aby pobrac portable OpenSSL
5. Zainstaluj OpenSSL w folderze "openssl" obok EXE

STRUKTURA FOLDEROW:
CertificateValidator_Portable/
├── CertificateValidator.exe    (Aplikacja)
├── openssl/                    (Folder na OpenSSL - instalacja automatyczna)
└── README.txt                  (Ten plik)

WYMAGANIA:
- Windows 10/11
- OpenSSL (pobierany automatycznie przez aplikacje)

KONTAKT:
W razie problemow sprawdz dokumentacje w folderze projektu.

Wersja: 1.0
Data: 2026-02-01
""")
    
    print(f"✅ Utworzono README: {readme_path}")
    print(f"\n📦 Portable package gotowy: {portable_dir}")
    print(f"\nMozesz skopiowac caly folder '{portable_dir.name}' i dystrybuowac!")
    
    return True

if __name__ == '__main__':
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       Certificate Validator - Build Script                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Build EXE
    if build_exe():
        # Utworz portable package
        create_portable_package()
        
        print("\n" + "="*60)
        print("✅ WSZYSTKO GOTOWE!")
        print("="*60)
        print("\nPliki sa w folderze: dist/")
        print("- CertificateValidator.exe - standalone EXE")
        print("- CertificateValidator_Portable/ - gotowy do dystrybucji")
    else:
        print("\n❌ Build zakonczony z bledami!")
        exit(1)
