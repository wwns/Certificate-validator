# Palo Cert

Desktopowa aplikacja dla Windows do sprawdzania certyfikatów TLS i kluczy
prywatnych oraz przygotowywania plików PEM dla urządzeń Palo Alto.

## Funkcje

- Walidacja certyfikatów serwera, certyfikatów CA i kluczy prywatnych.
- Odczyt informacji o certyfikacie, m.in. wystawcy i okresu ważności.
- Tworzenie pliku PEM zawierającego certyfikat i klucz, opcjonalnie z
  certyfikatami pośrednimi i głównym.
- Szyfrowanie kluczy prywatnych z użyciem OpenSSL.
- Wykrywanie OpenSSL zainstalowanego w systemie lub w folderze aplikacji.

## Wymagania

- Windows 10 lub 11.
- Python 3.9 lub nowszy, z Tkinter.
- OpenSSL. Aplikacja potrafi sprawdzić jego dostępność i przeprowadzić
  użytkownika przez instalację wersji portable.

## Uruchomienie ze źródeł

W PowerShell, z katalogu repozytorium:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Można też uruchomić `start.bat` w systemie Windows.

## Budowanie pliku EXE

Zainstaluj PyInstaller, a następnie uruchom skrypt budujący:

```powershell
python -m pip install pyinstaller
python build_exe.py
```

Pliki wynikowe są zapisywane w `dist\`. Do zbudowania instalatora Windows
potrzebny jest dodatkowo NSIS.

## Test diagnostyczny

Skrypt `test_embedded_openssl.py` wyświetla informacje o wykryciu OpenSSL
i strukturze katalogów:

```powershell
python test_embedded_openssl.py
```

## Bezpieczeństwo

Certyfikaty i klucze są przetwarzane lokalnie przez OpenSSL. Nie umieszczaj
w repozytorium prywatnych kluczy ani haseł. Pobrany instalator OpenSSL wymaga
dostępu do sieci.

## Licencja

Projekt jest udostępniany na licencji GNU GPL v3.0 — szczegóły w pliku
[LICENSE](LICENSE). OpenSSL jest objęty własną licencją; informacje znajdują
się na stronie [OpenSSL](https://www.openssl.org/source/license.html).

## Autor i współtwórca

[wwns](https://github.com/wwns)
