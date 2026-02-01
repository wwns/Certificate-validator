# Certificate Validator - Desktop Application

Aplikacja desktopowa do walidacji certyfikatów SSL/TLS i szyfrowania kluczy prywatnych.

## 🎯 Funkcje

### Walidacja Certyfikatów
- ✅ Walidacja certyfikatów serwera (server certificate)
- ✅ Walidacja kluczy prywatnych (private key)
- ✅ Walidacja certyfikatów pośrednich (intermediate CA)
- ✅ Walidacja certyfikatów głównych (root CA)
- ✅ Obsługa formatów: PEM, DER, CRT, CER
- ✅ Wsparcie dla Certum i innych CA
- ✅ Szczegółowe informacje: subject, issuer, daty ważności, numer seryjny

### Szyfrowanie Kluczy
- 🔐 Szyfrowanie kluczy prywatnych hasłem
- 🔐 Algorytmy: AES256, AES192, AES128, DES3
- 🔐 Automatyczna detekcja typu klucza (RSA/EC/DSA)
- 🔐 Sprawdzanie czy klucz jest już zaszyfrowany

### Embedded OpenSSL
- 🚀 **Automatyczne pobieranie** portable OpenSSL
- 🚀 **Lokalna instalacja** - nie wymaga uprawnień administratora
- 🚀 **Inteligentna detekcja** - najpierw lokalne, potem systemowe
- 🚀 **Jeden przycisk** - "Sprawdź OpenSSL" pobiera i instaluje

## 📋 Wymagania

- **Python**: 3.7+
- **System**: Windows 10/11
- **OpenSSL**: Automatycznie pobierany przez aplikację (lub ręcznie z https://slproweb.com)

## 🚀 Instalacja

### Opcja 1: Uruchomienie z Python

```bash
# Sklonuj repozytorium lub pobierz pliki
cd "Send to Palo Cert"

# Uruchom aplikację
python palo_cert_manager_desktop.py

# Lub użyj start.bat (Windows)
start.bat
```

### Opcja 2: Kompilacja do EXE

```bash
# Zainstaluj PyInstaller
pip install pyinstaller

# Skompiluj
pyinstaller --onefile --windowed --name "CertValidator" palo_cert_manager_desktop.py
```

## 📖 Jak używać

### 1. Pierwszy start - OpenSSL

Przy pierwszym uruchomieniu aplikacja sprawdzi czy OpenSSL jest dostępny:

- ❌ **Jeśli NIE**: Pojawi się dialog z opcjami
  - **TAK** - Pobierz portable OpenSSL (zalecane, automatyczne)
  - **NIE** - Otwórz stronę pobierania (ręczna instalacja)
  - **ANULUJ** - Kontynuuj bez OpenSSL (niektóre funkcje niedostępne)

- ✅ **Jeśli TAK**: Aplikacja jest gotowa do użycia

**Przycisk "🔍 Sprawdź OpenSSL"** w prawym górnym rogu pozwala:
- Sprawdzić status OpenSSL (dostępny/niedostępny)
- Zobaczyć wersję i lokalizację (Local/System)
- Pobrać i zainstalować portable OpenSSL

### 2. Walidacja Certyfikatów

**Lewa kolumna interfejsu:**

1. Kliknij **"Wybierz plik"** przy każdym typie certyfikatu:
   - 🌐 **Server Certificate** (wymagany)
   - 🔑 **Private Key** (opcjonalny)
   - 📄 **Intermediate CA** (opcjonalny)
   - 🏛️ **Root CA** (opcjonalny)

2. Kliknij **"Waliduj Certyfikaty"**

3. Wyniki pojawią się poniżej z ikonami:
   - ✅ Certyfikat prawidłowy
   - ❌ Certyfikat nieprawidłowy
   - 📝 Szczegóły: subject, issuer, daty, serial number

### 3. Szyfrowanie Klucza

**Prawa kolumna interfejsu:**

1. Wybierz **klucz prywatny** do zaszyfrowania

2. Wybierz **lokalizację zapisu** zaszyfrowanego klucza

3. Wybierz **algorytm szyfrowania**:
   - **AES256** (zalecane, najbezpieczniejsze)
   - AES192
   - AES128
   - DES3

4. Wpisz **hasło** (min. 8 znaków)

5. Kliknij **"Zaszyfruj Klucz"**

6. Zaszyfrowany klucz zostanie zapisany w wybranej lokalizacji

## 🏗️ Struktura Projektu

```
Send to Palo Cert/
├── palo_cert_manager_desktop.py  # GUI aplikacji (tkinter)
├── cert_manager_core.py          # Logika walidacji i szyfrowania
├── start.bat                     # Launcher Windows
├── requirements.txt              # Zależności Python (pusta - brak zależności!)
├── openssl/                      # Folder na portable OpenSSL
│   └── bin/
│       ├── openssl.exe           # Główny plik OpenSSL
│       └── *.dll                 # Biblioteki
├── README.md                     # Ten plik
└── OPENSSL_EMBEDDED.md           # Szczegółowa dokumentacja OpenSSL
```

## 🔧 Embedded OpenSSL - Jak działa?

Aplikacja ma wbudowaną inteligentną detekcję OpenSSL:

### Kolejność wyszukiwania:

1. **Lokalny folder** `<aplikacja>/openssl/bin/openssl.exe` ⭐ **PRIORYTET**
2. **Systemowy PATH** `C:\Program Files\OpenSSL-Win64\bin\openssl.exe`

### Implementacja:

```python
def _find_openssl(self):
    # 1. Sprawdź lokalny folder aplikacji
    local_openssl = Path(__file__).parent / "openssl" / "bin" / "openssl.exe"
    if local_openssl.exists():
        return str(local_openssl)
    
    # 2. Sprawdź systemowy PATH
    return shutil.which("openssl")
```

### Automatyczne pobieranie:

Funkcja `download_portable_openssl()` w `cert_manager_core.py`:
- Pobiera instalator z https://slproweb.com
- Zapisuje w folderze `openssl/`
- Uruchamia instalator z instrukcjami
- Aplikacja automatycznie wykrywa po instalacji

**Więcej szczegółów**: Zobacz [OPENSSL_EMBEDDED.md](OPENSSL_EMBEDDED.md)

## 🐛 Rozwiązywanie Problemów

### Problem: "OpenSSL niedostępny"

**Rozwiązanie:**
1. Kliknij **"🔍 Sprawdź OpenSSL"** w prawym górnym rogu
2. Wybierz **TAK** w dialogu
3. Zainstaluj w folderze aplikacji (domyślna ścieżka)
4. Sprawdź ponownie po instalacji

### Problem: "Unable to load certificate"

**Przyczyny:**
- Uszkodzony plik certyfikatu
- Nieobsługiwany format

**Rozwiązanie:**
- Sprawdź czy plik to PEM lub DER
- Otwórz plik w notatniku - PEM zaczyna się od `-----BEGIN CERTIFICATE-----`
- Spróbuj przekonwertować: `openssl x509 -in cert.der -inform DER -out cert.pem`

### Problem: "Unable to load private key"

**Przyczyny:**
- Klucz jest już zaszyfrowany (wymaga hasła)
- Nieprawidłowy format

**Rozwiązanie:**
- Sprawdź czy klucz zawiera `-----BEGIN ENCRYPTED PRIVATE KEY-----`
- Jeśli tak - najpierw odszyfruj hasłem
- Aplikacja wykrywa zaszyfrowane klucze i pokazuje komunikat

### Problem: Błąd przy szyfrowaniu

**Przyczyny:**
- Za krótkie hasło (min. 8 znaków)
- Klucz już zaszyfrowany

**Rozwiązanie:**
- Użyj hasła min. 8 znaków
- Sprawdź czy klucz nie jest już zaszyfrowany

## 📝 Formaty Plików

### Obsługiwane formaty certyfikatów:
- `.pem` - PEM (Base64 encoded)
- `.crt` - Certificate (zazwyczaj PEM)
- `.cer` - Certificate (może być PEM lub DER)
- `.der` - DER (Binary)

### Obsługiwane formaty kluczy:
- `.key` - Private key (PEM lub DER)
- `.pem` - PEM encoded key

### Typy kluczy:
- **RSA** - RSA private key
- **EC** - Elliptic Curve private key
- **DSA** - DSA private key

## 🔐 Bezpieczeństwo

### Hasła do kluczy:
- **Wymagania**: Minimum 8 znaków
- **Zalecenia**: 12+ znaków, duże/małe litery, cyfry, znaki specjalne
- **Algorytm**: AES256 (najsilniejsze szyfrowanie)

### Przechowywanie:
- Zaszyfrowane klucze można bezpiecznie przechowywać
- Hasło NIE jest zapisywane w aplikacji
- Aplikacja NIE wysyła danych przez sieć

## 🚧 Zmiany względem wersji webowej

### Usunięte funkcje:
- ❌ Połączenie SSH z Palo Alto
- ❌ Przesyłanie certyfikatów na urządzenie
- ❌ Flask web server
- ❌ Zależności: Flask, Werkzeug, paramiko

### Nowe funkcje:
- ✅ Embedded OpenSSL (automatyczne pobieranie)
- ✅ Interfejs tkinter (native desktop)
- ✅ Dwukolumnowy layout (certyfikaty | szyfrowanie)
- ✅ Przycisk "Sprawdź OpenSSL" w GUI
- ✅ Brak zależności zewnętrznych (pusta requirements.txt)

## 📄 Licencja

Ten projekt jest open source.

OpenSSL jest dostępny na licencji Apache 2.0: https://www.openssl.org/source/license.html

## 📧 Kontakt

W razie problemów lub pytań:
- Sprawdź [OPENSSL_EMBEDDED.md](OPENSSL_EMBEDDED.md) dla szczegółów o OpenSSL
- Użyj przycisku "🔍 Sprawdź OpenSSL" w aplikacji

---

**Wersja**: 2.0 (Desktop Edition with Embedded OpenSSL)  
**Data**: 2025-01-31
