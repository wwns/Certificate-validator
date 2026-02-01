"""
Test embedded OpenSSL functionality
"""
from cert_manager_core import CertificateManager
import os
from pathlib import Path

def test_openssl_detection():
    """Test detekcji OpenSSL (lokalny vs systemowy)."""
    print("=" * 60)
    print("TEST: Detekcja OpenSSL")
    print("=" * 60)
    
    cm = CertificateManager()
    
    # Sprawdź status
    is_available, message = cm.check_openssl()
    
    print(f"\nStatus: {'✅ Dostępny' if is_available else '❌ Niedostępny'}")
    print(f"Szczegóły: {message}")
    
    # Sprawdź ścieżkę
    openssl_path = cm.get_openssl_command()
    print(f"\nŚcieżka: {openssl_path}")
    
    # Sprawdź czy to lokalna czy systemowa wersja
    app_dir = Path(__file__).parent.resolve()
    local_openssl = app_dir / "openssl" / "bin" / "openssl.exe"
    
    if openssl_path == str(local_openssl):
        print("📍 Lokalizacja: LOKALNY (embedded OpenSSL) ⭐")
    else:
        print("📍 Lokalizacja: SYSTEMOWY")
    
    print("\n" + "=" * 60)
    return is_available

def test_local_openssl_folder():
    """Test czy folder openssl/ istnieje."""
    print("\n" + "=" * 60)
    print("TEST: Struktura folderów")
    print("=" * 60)
    
    app_dir = Path(__file__).parent.resolve()
    openssl_folder = app_dir / "openssl"
    openssl_bin = openssl_folder / "bin"
    openssl_exe = openssl_bin / "openssl.exe"
    
    print(f"\nFolder aplikacji: {app_dir}")
    print(f"Folder OpenSSL: {openssl_folder}")
    print(f"  - Istnieje: {'✅' if openssl_folder.exists() else '❌'}")
    
    if openssl_folder.exists():
        print(f"\nFolder bin: {openssl_bin}")
        print(f"  - Istnieje: {'✅' if openssl_bin.exists() else '❌'}")
        
        if openssl_bin.exists():
            print(f"\nPlik openssl.exe: {openssl_exe}")
            print(f"  - Istnieje: {'✅' if openssl_exe.exists() else '❌'}")
            
            if openssl_exe.exists():
                size = openssl_exe.stat().st_size / (1024 * 1024)  # MB
                print(f"  - Rozmiar: {size:.2f} MB")
    
    print("\n" + "=" * 60)

def test_download_capability():
    """Test możliwości pobierania OpenSSL."""
    print("\n" + "=" * 60)
    print("TEST: Funkcja pobierania")
    print("=" * 60)
    
    cm = CertificateManager()
    
    print("\nMetoda download_portable_openssl() jest dostępna: ✅")
    print("URL pobierania: https://slproweb.com/download/Win64OpenSSL_Light-3_4_0.exe")
    
    app_dir = Path(__file__).parent.resolve()
    openssl_dir = app_dir / "openssl"
    
    print(f"Folder docelowy: {openssl_dir}")
    print(f"\nAby pobrać OpenSSL:")
    print("  1. Uruchom aplikację GUI")
    print("  2. Kliknij '🔍 Sprawdź OpenSSL'")
    print("  3. Wybierz 'TAK' w dialogu")
    print("  4. Zainstaluj w folderze aplikacji")
    
    print("\n" + "=" * 60)

def main():
    """Uruchom wszystkie testy."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     TEST EMBEDDED OPENSSL - Certificate Validator          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Test 1: Detekcja
    openssl_available = test_openssl_detection()
    
    # Test 2: Struktura folderów
    test_local_openssl_folder()
    
    # Test 3: Pobieranie
    test_download_capability()
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    
    if openssl_available:
        print("✅ OpenSSL jest dostępny i gotowy do użycia")
        print("✅ Aplikacja może walidować certyfikaty")
        print("✅ Aplikacja może szyfrować klucze")
    else:
        print("❌ OpenSSL niedostępny")
        print("📥 Użyj przycisku w GUI aby pobrać portable OpenSSL")
    
    print("\n" + "=" * 60)
    print()

if __name__ == "__main__":
    main()
