#!/usr/bin/env python3
"""
Certificate Validator - Core Logic
Modul do walidacji certyfikatow
"""

import subprocess
import shutil
import os
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, Optional


class CertificateManager:
    """Menedzer certyfikatow"""
    
    def __init__(self):
        self._openssl_available = None
        self._openssl_path = None
        self._find_openssl()
        
    def _find_openssl(self):
        """Znajdz OpenSSL - priorytet systemowy, potem portable"""
        # Okresl folder aplikacji
        if getattr(sys, 'frozen', False):
            # Aplikacja skompilowana (PyInstaller)
            app_dir = Path(sys.executable).parent
            
            # Lista sciezek w kolejnosci priorytetu
            possible_paths = [
                # 1. Systemowa instalacja C:\Program Files
                Path('C:/Program Files/OpenSSL-Win64/bin/openssl.exe'),
                Path('C:/Program Files (x86)/OpenSSL-Win64/bin/openssl.exe'),
                
                # 2. Portable: openssl\OpenSSL-Win64\bin w root aplikacji
                app_dir / 'openssl' / 'OpenSSL-Win64' / 'bin' / 'openssl.exe',
            ]
        else:
            # Aplikacja uruchamiana ze zrodla - sprawdz lokalne i systemowe
            app_dir = Path(__file__).parent
            possible_paths = [
                # PRIORYTET: Standardowa systemowa instalacja
                Path('C:/Program Files/OpenSSL-Win64/bin/openssl.exe'),
                
                # Portable: folder openssl\OpenSSL-Win64\bin obok aplikacji
                app_dir / 'openssl' / 'OpenSSL-Win64' / 'bin' / 'openssl.exe',
                
                # Alternatywne lokalizacje
                Path('C:/Program Files (x86)/OpenSSL-Win64/bin/openssl.exe'),
                app_dir / 'openssl' / 'bin' / 'openssl.exe',
            ]
        
        for openssl_path in possible_paths:
            if openssl_path.exists():
                self._openssl_path = str(openssl_path)
                return
        
        # Sprawdz systemowy OpenSSL w PATH
        system_openssl = shutil.which('openssl')
        if system_openssl:
            self._openssl_path = system_openssl
            return
        
        self._openssl_path = None
    
    def get_openssl_command(self):
        """Zwroc sciezke do openssl lub 'openssl' jesli systemowy"""
        if self._openssl_path:
            return self._openssl_path
        return 'openssl'
        
    def check_openssl(self) -> tuple[bool, str]:
        """Sprawdz czy OpenSSL jest dostepny
        
        Returns:
            Krotka (czy_dostepny, komunikat)
        """
        if self._openssl_available is not None and self._openssl_path:
            return self._openssl_available, ""
        
        try:
            openssl_cmd = self.get_openssl_command()
            result = subprocess.run(
                [openssl_cmd, 'version'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self._openssl_available = True
                location = "Lokalny (wbudowany)" if 'openssl\\openssl.exe' in openssl_cmd else "Systemowy"
                return True, f"{result.stdout.strip()} [{location}]"
            else:
                self._openssl_available = False
                return False, "OpenSSL znaleziony ale nie dziala poprawnie"
        except Exception as e:
            self._openssl_available = False
            
            # Sugestia dla wersji portable
            if getattr(sys, 'frozen', False):
                app_dir = Path(sys.executable).parent
                suggested_path = app_dir / 'openssl' / 'OpenSSL-Win64' / 'bin' / 'openssl.exe'
                return False, f"OpenSSL niedostepny. Zainstaluj OpenSSL do:\n{suggested_path}\nlub C:\\Program Files\\OpenSSL-Win64\\bin\\openssl.exe"
            
            return False, f"OpenSSL niedostepny"
    
    def download_portable_openssl(self, dest_dir: str) -> tuple[bool, str]:
        """Pobierz portable wersje OpenSSL
        
        Args:
            dest_dir: Folder docelowy dla OpenSSL (pobieranie instalatora)
            
        Returns:
            Krotka (sukces, komunikat z pelna sciezka do instalatora)
        """
        try:
            # URL do portable OpenSSL (Light version wystarczy)
            # Aktualna stabilna wersja: 3.6.1 (Luty 2026)
            urls = [
                "https://slproweb.com/download/Win64OpenSSL_Light-3_6_1.exe",
                "https://slproweb.com/download/Win64OpenSSL_Light-3_5_5.exe",  # LTS fallback
                "https://slproweb.com/download/Win64OpenSSL_Light-3_4_4.exe",  # Poprzednia wersja
            ]
            
            dest_path = Path(dest_dir)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            installer_path = dest_path / "openssl_installer.exe"
            
            # Probuj kolejne URLe
            last_error = None
            for url in urls:
                try:
                    urllib.request.urlretrieve(url, installer_path)
                    # Zwroc sukces - GUI sam ustali docelowy folder
                    return True, str(installer_path)
                except urllib.error.HTTPError as e:
                    last_error = f"Blad HTTP {e.code} dla {url}"
                    continue
                except Exception as e:
                    last_error = str(e)
                    continue
            
            # Jesli zaden URL nie zadziala
            return False, f"Nie mozna pobrac OpenSSL z zaden z dostepnych zrodel.\nOstatni blad: {last_error}\n\nProsze pobrac recznie z:\nhttps://slproweb.com/products/Win32OpenSSL.html"
            
        except Exception as e:
            return False, f"Blad pobierania: {str(e)}"

    def validate_certificate(self, cert_path: str) -> Optional[Dict]:
        """Walidacja certyfikatu
        
        Args:
            cert_path: Sciezka do pliku certyfikatu
            
        Returns:
            Slownik z informacjami o certyfikacie lub None w przypadku bledu
        """
        # Sprawdz OpenSSL
        openssl_ok, openssl_msg = self.check_openssl()
        if not openssl_ok:
            return {
                'valid': False,
                'error': f'OpenSSL niedostepny: {openssl_msg}\n\nPobranie:\nhttps://slproweb.com/products/Win32OpenSSL.html\n\nPo instalacji dodaj do PATH i zrestartuj aplikacje.'
            }
        
        try:
            # Probuj najpierw jako PEM
            openssl_cmd = self.get_openssl_command()
            result = subprocess.run(
                [openssl_cmd, 'x509', '-in', cert_path, '-text', '-noout'],
                capture_output=True, text=True, timeout=10
            )
            
            # Jesli PEM nie dziala, probuj DER
            if result.returncode != 0:
                result = subprocess.run(
                    [openssl_cmd, 'x509', '-in', cert_path, '-inform', 'DER', '-text', '-noout'],
                    capture_output=True, text=True, timeout=10
                )
            
            if result.returncode != 0:
                # Zwroc blad z szczegolami
                return {
                    'valid': False,
                    'error': result.stderr if result.stderr else 'Nie mozna odczytac certyfikatu'
                }
            
            # Wyciagnij informacje z certyfikatu
            output = result.stdout
            subject = self._extract_field(output, 'Subject:')
            issuer = self._extract_field(output, 'Issuer:')
            valid_from = self._extract_field(output, 'Not Before:')
            valid_to = self._extract_field(output, 'Not After:')
            
            # Wyciagnij wiecej informacji
            serial = self._extract_field(output, 'Serial Number:')
            signature_algorithm = self._extract_field(output, 'Signature Algorithm:')
            
            return {
                'subject': subject,
                'issuer': issuer,
                'valid_from': valid_from,
                'valid_to': valid_to,
                'serial': serial,
                'signature_algorithm': signature_algorithm,
                'valid': True
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def _extract_field(self, text: str, field_name: str) -> str:
        """Wyciagnij pole z tekstu"""
        for line in text.split('\n'):
            if field_name in line:
                return line.replace(field_name, '').strip()
        return 'N/A'

    def validate_key(self, key_path: str) -> tuple[bool, str]:
        """Walidacja klucza prywatnego
        
        Args:
            key_path: Sciezka do pliku klucza
            
        Returns:
            Krotka (czy_prawidlowy, komunikat/typ_klucza)
        """
        # Sprawdz OpenSSL
        openssl_ok, openssl_msg = self.check_openssl()
        if not openssl_ok:
            return False, f'OpenSSL niedostepny: {openssl_msg}\n\nPobranie: https://slproweb.com/products/Win32OpenSSL.html'
        
        try:
            openssl_cmd = self.get_openssl_command()
            # Probuj RSA
            result = subprocess.run(
                [openssl_cmd, 'rsa', '-in', key_path, '-check', '-noout'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "RSA"
            
            # Probuj EC (Elliptic Curve)
            result = subprocess.run(
                [openssl_cmd, 'ec', '-in', key_path, '-check', '-noout'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "EC"
            
            # Probuj DSA
            result = subprocess.run(
                [openssl_cmd, 'dsa', '-in', key_path, '-check', '-noout'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "DSA"
            
            # Probuj jako zaszyfrowany klucz
            result = subprocess.run(
                [openssl_cmd, 'pkey', '-in', key_path, '-noout'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Zaszyfrowany (wymaga hasla)"
            
            return False, "Nieznany format klucza"
        except Exception as e:
            return False, str(e)

    def encrypt_private_key(self, key_path: str, output_path: str, password: str, cipher: str = 'aes256') -> tuple[bool, str]:
        """Zaszyfruj klucz prywatny haslem
        
        Args:
            key_path: Sciezka do klucza prywatnego
            output_path: Sciezka do pliku wyjsciowego
            password: Haslo do szyfrowania
            cipher: Algorytm szyfrowania (aes256, aes192, aes128, des3)
            
        Returns:
            Krotka (sukces, komunikat)
        """
        # Sprawdz OpenSSL
        openssl_ok, openssl_msg = self.check_openssl()
        if not openssl_ok:
            return False, f'OpenSSL niedostepny: {openssl_msg}\n\nPobranie: https://slproweb.com/products/Win32OpenSSL.html'
        
        try:
            openssl_cmd = self.get_openssl_command()
            # Najpierw sprawdz czy klucz jest prawidlowy
            is_valid, key_type = self.validate_key(key_path)
            if not is_valid:
                return False, f"Klucz prywatny jest nieprawidlowy: {key_type}"
            
            # Zaszyfruj klucz za pomoca OpenSSL
            result = subprocess.run(
                [openssl_cmd, 'rsa', '-in', key_path, f'-{cipher}', '-out', output_path, '-passout', f'pass:{password}'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return True, f"Klucz zaszyfrowany pomyslnie: {output_path}"
            else:
                return False, f"Blad szyfrowania: {result.stderr}"
                
        except Exception as e:
            return False, f"Wyjatek: {str(e)}"

    def check_key_encryption(self, key_path: str) -> tuple[bool, str]:
        """Sprawdz czy klucz jest zaszyfrowany
        
        Args:
            key_path: Sciezka do klucza prywatnego
            
        Returns:
            Krotka (czy_zaszyfrowany, typ_szyfrowania lub 'niezaszyfrowany')
        """
        try:
            with open(key_path, 'r') as f:
                content = f.read()
                
            # Sprawdz naglowki PEM
            if 'ENCRYPTED' in content:
                # Wyciagnij typ szyfrowania z naglowka
                for line in content.split('\n'):
                    if 'DEK-Info:' in line:
                        cipher_info = line.split('DEK-Info:')[1].strip().split(',')[0]
                        return True, cipher_info
                return True, "zaszyfrowany (typ nieznany)"
            else:
                return False, "niezaszyfrowany"
                
        except Exception as e:
            return False, f"Blad odczytu: {str(e)}"

    def create_palo_alto_pem(self, server_cert: str, private_key: str, 
                            intermediate_cert: str = None, root_cert: str = None,
                            output_path: str = None) -> tuple[bool, str]:
        """Tworzy pliki dla Palo Alto w odpowiednim formacie
        
        Format Palo Alto:
        - Certificate chain (.pem): Certyfikat serwera + CA posredni + Root CA
        - Private Key (osobny plik): Klucz prywatny
        
        Args:
            server_cert: Sciezka do certyfikatu serwera
            private_key: Sciezka do klucza prywatnego
            intermediate_cert: Sciezka do CA posredniego (opcjonalnie)
            root_cert: Sciezka do Root CA (opcjonalnie)
            output_path: Sciezka do pliku wyjsciowego (domyslnie: paloalto_certificate.pem)
            
        Returns:
            Krotka (sukces, komunikat)
        """
        try:
            if not output_path:
                output_path = "paloalto_certificate.pem"
            
            # Walidacja wymaganych plikow
            if not os.path.exists(server_cert):
                return False, f"Certyfikat serwera nie istnieje: {server_cert}"
            if not os.path.exists(private_key):
                return False, f"Klucz prywatny nie istnieje: {private_key}"
            
            # Walidacja certyfikatow
            cert_info = self.validate_certificate(server_cert)
            if not cert_info or not cert_info.get('valid'):
                return False, f"Certyfikat serwera jest nieprawidlowy"
            
            key_valid, key_msg = self.validate_key(private_key)
            if not key_valid:
                return False, f"Klucz prywatny jest nieprawidlowy: {key_msg}"
            
            # Buduj lancuch certyfikatow (BEZ klucza prywatnego)
            cert_chain = []
            
            # 1. Certyfikat serwera
            with open(server_cert, 'r', encoding='utf-8') as f:
                cert_data = f.read().strip()
                cert_chain.append(cert_data)
            
            # 2. CA posredni (jesli istnieje)
            if intermediate_cert and os.path.exists(intermediate_cert):
                int_cert_info = self.validate_certificate(intermediate_cert)
                if int_cert_info and int_cert_info.get('valid'):
                    with open(intermediate_cert, 'r', encoding='utf-8') as f:
                        int_data = f.read().strip()
                        cert_chain.append(int_data)
            
            # 3. Root CA (jesli istnieje)
            if root_cert and os.path.exists(root_cert):
                root_cert_info = self.validate_certificate(root_cert)
                if root_cert_info and root_cert_info.get('valid'):
                    with open(root_cert, 'r', encoding='utf-8') as f:
                        root_data = f.read().strip()
                        cert_chain.append(root_data)
            
            # Zapisz lancuch certyfikatow do pliku
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(cert_chain))
                f.write('\n')
            
            # Skopiuj klucz prywatny do osobnego pliku
            key_output_path = output_path.replace('.pem', '_key.pem')
            if key_output_path == output_path:
                key_output_path = output_path.replace('.pem', '') + '_key.pem'
            
            with open(private_key, 'r', encoding='utf-8') as f_in:
                with open(key_output_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
            
            # Policz dodane komponenty
            components = ["Certyfikat serwera"]
            if intermediate_cert and os.path.exists(intermediate_cert):
                components.append("CA posredni")
            if root_cert and os.path.exists(root_cert):
                components.append("Root CA")
            
            summary = f"Pliki dla Palo Alto utworzone pomyslnie!\n\n"
            summary += f"Certificate Chain: {output_path}\n"
            summary += f"Zawiera:\n"
            for i, comp in enumerate(components, 1):
                summary += f"  {i}. {comp}\n"
            summary += f"\nPrivate Key: {key_output_path}\n"
            summary += f"\nW Palo Alto zaimportuj:\n"
            summary += f"1. Certificate: {output_path}\n"
            summary += f"2. Private Key: {key_output_path}"
            
            return True, summary
            
        except Exception as e:
            return False, f"Blad tworzenia plikow: {str(e)}"
