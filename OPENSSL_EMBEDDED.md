# Embedded OpenSSL - Instrukcja

## Jak działa embedded OpenSSL

Aplikacja **Certificate Validator** ma wbudowaną możliwość automatycznego pobierania i używania portable wersji OpenSSL, która jest instalowana lokalnie w folderze aplikacji zamiast w systemie.

### Zalety embedded OpenSSL

1. ✅ **Nie wymaga uprawnień administratora** - instalacja w folderze aplikacji
2. ✅ **Nie modyfikuje PATH systemowego** - działa niezależnie od systemu
3. ✅ **Automatyczna detekcja** - aplikacja sama znajduje lokalny OpenSSL
4. ✅ **Łatwa instalacja** - jeden przycisk w aplikacji

### Architektura

```
Send to Palo Cert/
├── palo_cert_manager_desktop.py    # GUI aplikacji
├── cert_manager_core.py             # Logika walidacji
└── openssl/                         # Folder na portable OpenSSL
    ├── openssl.exe                  # Główny plik wykonywalny
    ├── libcrypto-3-x64.dll         # Biblioteki
    └── libssl-3-x64.dll
```

### Kolejność wyszukiwania OpenSSL

Aplikacja szuka OpenSSL w następującej kolejności:

1. **Lokalny folder aplikacji**: `<aplikacja>/openssl/bin/openssl.exe` ⭐ PRIORYTET
2. **Systemowy PATH**: standardowa instalacja w `C:\Program Files\OpenSSL-Win64\bin\openssl.exe`

### Jak używać

#### Opcja 1: Automatyczne pobieranie (zalecane)

1. Uruchom aplikację
2. Jeśli OpenSSL nie jest zainstalowany, pojawi się dialog
3. Kliknij **TAK** aby pobrać portable OpenSSL
4. Aplikacja pobierze instalator (Win64OpenSSL_Light-3_4_0.exe)
5. Uruchom instalator i wybierz folder: `<aplikacja>/openssl`
6. Po instalacji kliknij **"🔍 Sprawdź OpenSSL"** w aplikacji
7. Gotowe! Aplikacja automatycznie wykryje lokalny OpenSSL

#### Opcja 2: Ręczna instalacja

1. Pobierz portable OpenSSL z: https://slproweb.com/products/Win32OpenSSL.html
2. Wybierz wersję **Win64 OpenSSL v3.x.x** (Light wystarczy)
3. Uruchom instalator
4. Wybierz lokalizację: `<ścieżka_do_aplikacji>/openssl`
5. Zaznacz opcję **"The OpenSSL binaries (/bin) directory"**
6. Zakończ instalację
7. Zrestartuj aplikację lub kliknij **"🔍 Sprawdź OpenSSL"**

### Implementacja techniczna

#### cert_manager_core.py

```python
def _find_openssl(self):
    """Szuka OpenSSL: najpierw lokalnie, potem w systemie."""
    # 1. Sprawdz folder aplikacji
    app_dir = Path(__file__).parent.resolve()
    local_openssl = app_dir / "openssl" / "bin" / "openssl.exe"
    
    if local_openssl.exists():
        return str(local_openssl)
    
    # 2. Sprawdz systemowy PATH
    system_openssl = shutil.which("openssl")
    return system_openssl

def get_openssl_command(self) -> str:
    """Zwraca ścieżkę do OpenSSL."""
    if self._openssl_path:
        return self._openssl_path
    return "openssl"  # Fallback
```

#### Wywołania OpenSSL

Wszystkie wywołania OpenSSL używają `get_openssl_command()`:

```python
openssl_cmd = self.get_openssl_command()
subprocess.run([openssl_cmd, 'x509', '-in', cert_path, ...])
```

### Status w aplikacji

W prawym górnym rogu aplikacji znajduje się przycisk **"🔍 Sprawdź OpenSSL"**, który pokazuje:

- ✅ **Status**: Czy OpenSSL jest dostępny
- 📍 **Lokalizacja**: Local (aplikacja) lub System
- 🔢 **Wersja**: OpenSSL 3.x.x

### Rozwiązywanie problemów

#### Problem: "OpenSSL niedostępny"

**Rozwiązanie:**
1. Kliknij **"🔍 Sprawdź OpenSSL"** w aplikacji
2. Wybierz **TAK** aby pobrać portable OpenSSL
3. Zainstaluj w folderze aplikacji
4. Sprawdź ponownie

#### Problem: "Nie można znaleźć openssl.exe"

**Rozwiązanie:**
1. Sprawdź czy folder `openssl/bin/` istnieje w katalogu aplikacji
2. Sprawdź czy plik `openssl.exe` jest w `openssl/bin/openssl.exe`
3. Jeśli nie - zainstaluj ponownie używając przycisku w aplikacji

#### Problem: "Missing DLL files"

**Rozwiązanie:**
1. Pobierz pełną wersję OpenSSL (nie Light)
2. Lub zainstaluj Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Dystrybucja aplikacji

Jeśli chcesz rozpowszechniać aplikację z embedded OpenSSL:

1. Zainstaluj OpenSSL lokalnie w `openssl/`
2. Skopiuj całą strukturę folderów:
   ```
   Send to Palo Cert/
   ├── palo_cert_manager_desktop.py
   ├── cert_manager_core.py
   └── openssl/
       └── bin/
           ├── openssl.exe
           ├── libcrypto-3-x64.dll
           └── libssl-3-x64.dll
   ```
3. Użytkownik NIE musi instalować OpenSSL w systemie

### PyInstaller (EXE)

Jeśli kompilujesz do EXE za pomocą PyInstaller:

```bash
pyinstaller --onefile --windowed --add-data "openssl;openssl" palo_cert_manager_desktop.py
```

Dodaj do spec file:

```python
datas=[
    ('openssl/bin/openssl.exe', 'openssl/bin'),
    ('openssl/bin/*.dll', 'openssl/bin'),
]
```

### Testowanie

Test lokalnego OpenSSL:

```python
from cert_manager_core import CertificateManager

cm = CertificateManager()
print(cm.get_openssl_command())  # Pokaże ścieżkę
is_ok, msg = cm.check_openssl()
print(f"Status: {msg}")
```

### Licencja OpenSSL

OpenSSL jest dostępny na licencji Apache 2.0. Więcej: https://www.openssl.org/source/license.html

---

**Wersja**: 1.0  
**Data**: 2025-01-31  
**Autor**: Certificate Validator Team
