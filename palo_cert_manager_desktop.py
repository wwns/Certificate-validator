#!/usr/bin/env python3
"""
Certificate Validator - Desktop Application
Aplikacja desktopowa do walidacji certyfikatow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
from PIL import Image, ImageTk
from cert_manager_core import CertificateManager


class CertValidatorApp:
    """Glowne okno aplikacji"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Certificate Validator")
        self.root.geometry("900x600")
        self.root.minsize(900, 600)  # Minimalny rozmiar okna
        
        # Ustaw ikone okna
        try:
            if getattr(sys, 'frozen', False):
                icon_path = Path(sys._MEIPASS) / 'icons' / 'paloalto.png'
            else:
                icon_path = Path(__file__).parent / 'icons' / 'paloalto.png'
            
            if icon_path.exists():
                icon_img = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon_img)
        except Exception as e:
            print(f"Ikona nie zaladowana: {e}")
        
        # Menedzer certyfikatow
        self.cert_manager = CertificateManager()
        
        # Zmienne dla pol
        self.server_cert_path = tk.StringVar()
        self.private_key_path = tk.StringVar()
        self.intermediate_cert_path = tk.StringVar()
        self.root_cert_path = tk.StringVar()
        
        # Zmienne dla szyfrowania
        self.key_to_encrypt_path = tk.StringVar()
        self.encrypted_key_output_path = tk.StringVar()
        self.encryption_password = tk.StringVar()
        self.encryption_cipher = tk.StringVar(value="aes256")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Utworz interfejs uzytkownika"""
        # Naglowek
        header = tk.Frame(self.root, bg="#004E89", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo Palo Alto
        try:
            if getattr(sys, 'frozen', False):
                logo_path = Path(sys._MEIPASS) / 'icons' / 'paloalto.png'
            else:
                logo_path = Path(__file__).parent / 'icons' / 'paloalto.png'
            
            if logo_path.exists():
                logo_img = Image.open(logo_path)
                # Zachowaj proporcje - maksymalna wysokość 50px
                logo_img.thumbnail((200, 50), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header, image=self.logo_photo, bg="#004E89")
                logo_label.pack(side="left", pady=15, padx=20)
        except Exception as e:
            print(f"Logo nie załadowane: {e}")
        
        title_label = tk.Label(
            header, 
            text="Certificate Validator",
            font=("Arial", 20, "bold"),
            bg="#004E89",
            fg="white"
        )
        title_label.pack(side="left", pady=20, padx=(0, 20))
        
        # Przycisk sprawdzania OpenSSL w naglowku
        check_openssl_btn = tk.Button(
            header,
            text="🔍 Sprawdz OpenSSL",
            command=self.manual_check_openssl,
            font=("Arial", 11),
            bg="#1A7FBF",
            fg="white",
            activebackground="#004E89",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        check_openssl_btn.pack(side="right", pady=20, padx=20)
        
        # Sprawdz OpenSSL przy starcie
        self.check_openssl_status()
        
        # Glowna ramka z dwoma kolumnami - wypelnia cale okno
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Konfiguracja kolumn - rowne proporcje
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)  # scrollbar
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_columnconfigure(3, weight=0)  # scrollbar
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Lewa kolumna z scrollbarem (bez sztywnej szerokosci)
        left_canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0, bd=0)
        left_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=left_canvas.yview)
        left_frame = ttk.Frame(left_canvas)
        
        def update_left_scrollregion(event=None):
            left_canvas.update_idletasks()
            # Ustaw scrollregion dokładnie na rozmiar frame
            bbox = left_canvas.bbox("all")
            if bbox:
                left_canvas.configure(scrollregion=(0, 0, bbox[2], bbox[3]))
        
        left_frame.bind("<Configure>", update_left_scrollregion)
        
        left_window = left_canvas.create_window((0, 0), window=left_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Responsywna szerokosc content
        def on_left_canvas_configure(event):
            left_canvas.itemconfig(left_window, width=event.width, height=event.height)
        left_canvas.bind('<Configure>', on_left_canvas_configure)
        
        # Mouse wheel scrolling
        def on_left_mousewheel(event):
            left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        left_canvas.bind_all("<MouseWheel>", on_left_mousewheel)
        
        left_canvas.grid(row=0, column=0, sticky="nsew")
        left_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Prawa kolumna z scrollbarem (bez sztywnej szerokosci)
        right_canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0, bd=0)
        right_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=right_canvas.yview)
        right_frame = ttk.Frame(right_canvas)
        
        def update_right_scrollregion(event=None):
            right_canvas.update_idletasks()
            # Ustaw scrollregion dokładnie na rozmiar frame
            bbox = right_canvas.bbox("all")
            if bbox:
                right_canvas.configure(scrollregion=(0, 0, bbox[2], bbox[3]))
        
        right_frame.bind("<Configure>", update_right_scrollregion)
        
        right_window = right_canvas.create_window((0, 0), window=right_frame, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        
        # Responsywna szerokosc content
        def on_right_canvas_configure(event):
            right_canvas.itemconfig(right_window, width=event.width, height=event.height)
        right_canvas.bind('<Configure>', on_right_canvas_configure)
        
        # Mouse wheel scrolling (tylko gdy mysz nad prawym canvas)
        def on_right_mousewheel(event):
            right_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        right_canvas.bind("<Enter>", lambda e: right_canvas.bind_all("<MouseWheel>", on_right_mousewheel))
        right_canvas.bind("<Leave>", lambda e: right_canvas.unbind_all("<MouseWheel>"))
        
        right_canvas.grid(row=0, column=2, sticky="nsew")
        right_scrollbar.grid(row=0, column=3, sticky="ns")
        
        # Sekcje - lewa strona
        self.create_certificates_section(left_frame)
        self.create_validation_section(left_frame)
        
        # Sekcje - prawa strona
        self.create_encryption_section(right_frame)
    
    def check_openssl_status(self):
        """Sprawdz status OpenSSL przy starcie"""
        openssl_ok, openssl_msg = self.cert_manager.check_openssl()
        
        if not openssl_ok:
            result = messagebox.askyesnocancel(
                "Brak OpenSSL",
                f"OpenSSL nie jest zainstalowany lub niedostepny!\n\n"
                f"Szczegoly: {openssl_msg}\n\n"
                f"Aplikacja wymaga OpenSSL do walidacji certyfikatow.\n\n"
                f"TAK - Pobierz portable OpenSSL (zalecane)\n"
                f"NIE - Otwórz stronę pobierania\n"
                f"ANULUJ - Kontynuuj bez OpenSSL",
                icon='warning'
            )
            if result is True:  # TAK - pobierz portable
                self.download_openssl()
            elif result is False:  # NIE - otwórz stronę
                self.open_openssl_download()
        else:
            print(f"✅ OpenSSL dostepny: {openssl_msg}")
    
    def manual_check_openssl(self):
        """Recznie sprawdz status OpenSSL (wywoływane przyciskiem)."""
        openssl_ok, openssl_msg = self.cert_manager.check_openssl()
        
        if openssl_ok:
            messagebox.showinfo(
                "OpenSSL Status",
                f"✓ OpenSSL jest dostępny i działa poprawnie!\n\n{openssl_msg}"
            )
        else:
            result = messagebox.askyesnocancel(
                "Brak OpenSSL",
                f"OpenSSL nie jest zainstalowany lub niedostepny!\n\n"
                f"Szczegoly: {openssl_msg}\n\n"
                f"TAK - Pobierz portable OpenSSL (zalecane)\n"
                f"NIE - Otwórz stronę pobierania\n"
                f"ANULUJ - Anuluj",
                icon='warning'
            )
            if result is True:
                self.download_openssl()
            elif result is False:
                self.open_openssl_download()
    
    
    def download_openssl(self):
        """Pobierz i zainstaluj portable OpenSSL do folderu aplikacji."""
        import os
        import sys
        from pathlib import Path
        
        # Okresl wlasciwy folder docelowy
        if getattr(sys, 'frozen', False):
            # Aplikacja skompilowana - folder obok .exe
            app_dir = Path(sys.executable).parent
            openssl_dir = app_dir / 'openssl'
            install_target = openssl_dir / 'OpenSSL-Win64'
        else:
            # Development - systemowa instalacja
            openssl_dir = Path.home() / 'Downloads'  # Temp do pobrania
            install_target = Path('C:/Program Files/OpenSSL-Win64')
        
        # Pokaz komunikat o rozpoczeciu
        self.root.update()
        progress_label = tk.Label(
            self.root, 
            text="⏳ Pobieranie OpenSSL...", 
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0'
        )
        progress_label.place(relx=0.5, rely=0.5, anchor='center')
        self.root.update()
        
        try:
            # Pobierz instalator
            success, message = self.cert_manager.download_portable_openssl(str(openssl_dir))
            
            progress_label.destroy()
            
            if success:
                # Pelna sciezka do openssl.exe
                openssl_exe_path = install_target / 'bin' / 'openssl.exe'
                
                # Komunikat z instrukcjami - rozny dla portable i systemowej
                if getattr(sys, 'frozen', False):
                    # Wersja portable - zalecany folder lokalny, mozliwy Program Files
                    installer_info = (
                        "OpenSSL zostal pobrany pomyslnie!\n\n"
                        "WAZNE INSTRUKCJE:\n\n"
                        f"ZALECANE: W instalatorze wybierz folder:\n   {install_target}\n\n"
                        "ALTERNATYWNIE mozesz zainstalowac w:\n   C:\\Program Files\\OpenSSL-Win64\n\n"
                        "2. Zaznacz opcje 'The OpenSSL binaries (/bin) directory'\n\n"
                        "3. Po instalacji NIE MUSISZ restartowac aplikacji\n\n"
                        "Czy uruchomic instalator teraz?"
                    )
                else:
                    # Wersja development - systemowa instalacja
                    installer_info = (
                        "OpenSSL zostal pobrany pomyslnie!\n\n"
                        "WAZNE INSTRUKCJE:\n\n"
                        f"1. W instalatorze wybierz folder:\n   {install_target}\n\n"
                        "2. Zaznacz opcje 'The OpenSSL binaries (/bin) directory'\n\n"
                        "3. Po instalacji NIE MUSISZ restartowac aplikacji\n\n"
                        "Czy uruchomic instalator teraz?"
                    )
                
                result = messagebox.askyesno("OpenSSL pobrany", installer_info, icon='info')
                
                if result:
                    import subprocess
                    installer_path = Path(message)  # message zawiera sciezke do instalatora
                    try:
                        # Uruchom instalator i czekaj na zakonczenie
                        process = subprocess.Popen([str(installer_path)])
                        
                        # Pokazujemy informacje o czekaniu
                        wait_msg = messagebox.showinfo(
                            "Instalator uruchomiony",
                            f"Po zakonczeniu instalacji OpenSSL bedzie w:\n{openssl_exe_path}\n\n"
                            "Kliknij OK po zakonczeniu instalacji.\n"
                            "Aplikacja automatycznie sprawdzi obecnosc OpenSSL."
                        )
                        
                        # Po zamknieciu komunikatu - odswież detekcje OpenSSL
                        self.cert_manager._find_openssl()
                        openssl_ok, openssl_msg = self.cert_manager.check_openssl()
                        
                        if openssl_ok:
                            messagebox.showinfo(
                                "Sukces!", 
                                f"OpenSSL zostal wykryty!\n\n{openssl_msg}\n\nMozesz teraz uzywac aplikacji."
                            )
                            # Odswież status w GUI
                            self.check_openssl_status()
                        else:
                            messagebox.showwarning(
                                "OpenSSL nie wykryty",
                                "OpenSSL nie zostal jeszcze wykryty.\n\n"
                                "Upewnij sie ze instalacja zakonczona prawidlowo\n"
                                "i kliknij 'Sprawdz OpenSSL' ponownie."
                            )
                    except Exception as e:
                        messagebox.showerror("Blad", f"Nie mozna uruchomic instalatora:\n{str(e)[:200]}")
            else:
                # Wyswietl tylko czesc komunikatu bez polskich znakow specjalnych
                error_msg = "Nie mozna pobrac OpenSSL.\n\nProsze pobrac recznie z:\nhttps://slproweb.com/products/Win32OpenSSL.html"
                messagebox.showerror("Blad pobierania", error_msg)
        except Exception as e:
            progress_label.destroy()
            messagebox.showerror("Blad", f"Nieoczekiwany blad:\n{e}")
    
    def open_openssl_download(self):
        """Otwiera strone pobierania OpenSSL i pokazuje instrukcje"""
        import webbrowser
        
        # Otwórz stronę pobierania
        webbrowser.open('https://slproweb.com/products/Win32OpenSSL.html')
        
        # Pokaż instrukcje instalacji
        messagebox.showinfo(
            "Instrukcja instalacji OpenSSL",
            "Krok 1: Pobierz instalator\n"
            "- Wybierz 'Win64 OpenSSL v3.x.x' (pelna wersja, NIE Light)\n\n"
            "Krok 2: Uruchom instalator\n"
            "- Zaakceptuj domyslna lokalizacje\n"
            "- WAZNE: Zaznacz opcje 'Add to PATH'\n\n"
            "Krok 3: Po instalacji\n"
            "- Zrestartuj te aplikacje\n"
            "- OpenSSL bedzie gotowy do uzycia\n\n"
            "Domyslna lokalizacja:\n"
            "C:\\Program Files\\OpenSSL-Win64\\bin"
        )
    
    def create_certificates_section(self, parent):
        """Sekcja certyfikatow"""
        cert_frame = ttk.LabelFrame(parent, text="1. Wybierz certyfikaty", padding=15)
        cert_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Certyfikat serwera
        ttk.Label(cert_frame, text="Certyfikat Serwera:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(cert_frame, textvariable=self.server_cert_path, width=35).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(cert_frame, text="...", width=3, command=lambda: self.select_file(self.server_cert_path)).grid(row=0, column=2, pady=5)
        
        # Klucz prywatny
        ttk.Label(cert_frame, text="Klucz Prywatny:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(cert_frame, textvariable=self.private_key_path, width=35).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(cert_frame, text="...", width=3, command=lambda: self.select_file(self.private_key_path)).grid(row=1, column=2, pady=5)
        
        # CA posredni
        ttk.Label(cert_frame, text="CA Posredni:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(cert_frame, textvariable=self.intermediate_cert_path, width=35).grid(row=2, column=1, pady=5, padx=5)
        ttk.Button(cert_frame, text="...", width=3, command=lambda: self.select_file(self.intermediate_cert_path)).grid(row=2, column=2, pady=5)
        
        # Root CA
        ttk.Label(cert_frame, text="Root CA:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(cert_frame, textvariable=self.root_cert_path, width=35).grid(row=3, column=1, pady=5, padx=5)
        ttk.Button(cert_frame, text="...", width=3, command=lambda: self.select_file(self.root_cert_path)).grid(row=3, column=2, pady=5)
    
    def create_validation_section(self, parent):
        """Sekcja walidacji"""
        val_frame = ttk.LabelFrame(parent, text="2. Walidacja certyfikatow", padding=15)
        val_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ramka na przyciski
        btn_frame = ttk.Frame(val_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Waliduj wybrane certyfikaty",
            command=self.validate_certificates
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Utworz .pem dla Palo Alto",
            command=self.create_paloalto_pem,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        # Wynik walidacji
        self.validation_result = scrolledtext.ScrolledText(val_frame, height=20, wrap=tk.WORD)
        self.validation_result.pack(pady=10, fill=tk.BOTH, expand=True)
    
    def create_encryption_section(self, parent):
        """Sekcja szyfrowania kluczy"""
        encrypt_main_frame = ttk.LabelFrame(parent, text="3. Szyfrowanie klucza", padding=15)
        encrypt_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Wybor klucza
        ttk.Label(encrypt_main_frame, text="Klucz do zaszyfrowania:").pack(anchor=tk.W, pady=(5,0))
        key_entry_frame = ttk.Frame(encrypt_main_frame)
        key_entry_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(key_entry_frame, textvariable=self.key_to_encrypt_path, width=35).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(key_entry_frame, text="...", width=3, command=lambda: self.select_file(self.key_to_encrypt_path)).pack(side=tk.LEFT)
        
        ttk.Button(encrypt_main_frame, text="Sprawdz status klucza", command=self.check_key_status).pack(pady=5)
        
        self.key_status_label = tk.Label(encrypt_main_frame, text="", font=("Arial", 9), fg="blue")
        self.key_status_label.pack(pady=5)
        
        # Separator
        ttk.Separator(encrypt_main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Haslo
        ttk.Label(encrypt_main_frame, text="Haslo szyfrowania:").pack(anchor=tk.W, pady=(5,0))
        ttk.Entry(encrypt_main_frame, textvariable=self.encryption_password, width=40, show="*").pack(fill=tk.X, pady=5)
        
        # Algorytm
        ttk.Label(encrypt_main_frame, text="Algorytm:").pack(anchor=tk.W, pady=(5,0))
        cipher_combo = ttk.Combobox(encrypt_main_frame, textvariable=self.encryption_cipher, width=38, state="readonly")
        cipher_combo['values'] = ('aes256', 'aes192', 'aes128', 'des3')
        cipher_combo.pack(fill=tk.X, pady=5)
        
        # Plik wyjsciowy
        ttk.Label(encrypt_main_frame, text="Plik wyjsciowy:").pack(anchor=tk.W, pady=(5,0))
        output_frame = ttk.Frame(encrypt_main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(output_frame, textvariable=self.encrypted_key_output_path, width=35).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(output_frame, text="...", width=3, command=self.select_output_file).pack(side=tk.LEFT)
        
        ttk.Button(
            encrypt_main_frame,
            text="Zaszyfruj i zapisz klucz",
            command=self.encrypt_key
        ).pack(pady=15)
        
        # Wynik
        ttk.Label(encrypt_main_frame, text="Wynik:").pack(anchor=tk.W, pady=(5,0))
        self.encryption_result = scrolledtext.ScrolledText(encrypt_main_frame, height=15, wrap=tk.WORD)
        self.encryption_result.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def select_file(self, var):
        """Wybierz plik"""
        filename = filedialog.askopenfilename(
            title="Wybierz plik",
            filetypes=[
                ("Certificate files", "*.pem *.crt *.cer *.key"),
                ("All files", "*.*")
            ]
        )
        if filename:
            var.set(filename)
    
    def validate_certificates(self):
        """Waliduj wybrane certyfikaty"""
        self.validation_result.delete(1.0, tk.END)
        self.validation_result.insert(tk.END, "Walidacja certyfikatow...\n\n")
        
        # Waliduj certyfikat serwera
        if self.server_cert_path.get():
            self.validation_result.insert(tk.END, "=== Certyfikat Serwera ===\n")
            cert_info = self.cert_manager.validate_certificate(self.server_cert_path.get())
            if cert_info and cert_info.get('valid'):
                self.validation_result.insert(tk.END, f"✅ Prawidlowy\n")
                self.validation_result.insert(tk.END, f"Subject: {cert_info.get('subject', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Issuer: {cert_info.get('issuer', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Valid From: {cert_info.get('valid_from', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Valid To: {cert_info.get('valid_to', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Serial: {cert_info.get('serial', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Signature Algorithm: {cert_info.get('signature_algorithm', 'N/A')}\n")
            else:
                self.validation_result.insert(tk.END, f"❌ Nieprawidlowy lub blad\n")
                if cert_info:
                    error_msg = cert_info.get('error', 'Nieznany blad')
                    self.validation_result.insert(tk.END, f"Szczegoly: {error_msg}\n")
            self.validation_result.insert(tk.END, "\n")
        
        # Waliduj klucz prywatny
        if self.private_key_path.get():
            self.validation_result.insert(tk.END, "=== Klucz Prywatny ===\n")
            is_valid, key_info = self.cert_manager.validate_key(self.private_key_path.get())
            if is_valid:
                self.validation_result.insert(tk.END, f"✅ Prawidlowy (Typ: {key_info})\n")
            else:
                self.validation_result.insert(tk.END, f"❌ Nieprawidlowy\n")
                self.validation_result.insert(tk.END, f"Szczegoly: {key_info}\n")
            self.validation_result.insert(tk.END, "\n")
        
        # Waliduj CA posredni
        if self.intermediate_cert_path.get():
            self.validation_result.insert(tk.END, "=== CA Posredni ===\n")
            cert_info = self.cert_manager.validate_certificate(self.intermediate_cert_path.get())
            if cert_info and cert_info.get('valid'):
                self.validation_result.insert(tk.END, f"✅ Prawidlowy\n")
                self.validation_result.insert(tk.END, f"Subject: {cert_info.get('subject', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Issuer: {cert_info.get('issuer', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Valid From: {cert_info.get('valid_from', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Valid To: {cert_info.get('valid_to', 'N/A')}\n")
            else:
                self.validation_result.insert(tk.END, f"❌ Nieprawidlowy lub blad\n")
                if cert_info:
                    error_msg = cert_info.get('error', 'Nieznany blad')
                    self.validation_result.insert(tk.END, f"Szczegoly: {error_msg}\n")
            self.validation_result.insert(tk.END, "\n")
        
        # Waliduj Root CA
        if self.root_cert_path.get():
            self.validation_result.insert(tk.END, "=== Root CA ===\n")
            cert_info = self.cert_manager.validate_certificate(self.root_cert_path.get())
            if cert_info and cert_info.get('valid'):
                self.validation_result.insert(tk.END, f"✅ Prawidlowy\n")
                self.validation_result.insert(tk.END, f"Subject: {cert_info.get('subject', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Issuer: {cert_info.get('issuer', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Valid From: {cert_info.get('valid_from', 'N/A')}\n")
                self.validation_result.insert(tk.END, f"Valid To: {cert_info.get('valid_to', 'N/A')}\n")
            else:
                self.validation_result.insert(tk.END, f"❌ Nieprawidlowy lub blad\n")
                if cert_info:
                    error_msg = cert_info.get('error', 'Nieznany blad')
                    self.validation_result.insert(tk.END, f"Szczegoly: {error_msg}\n")
            self.validation_result.insert(tk.END, "\n")
        
        self.validation_result.insert(tk.END, "Walidacja zakonczona.\n")
    
    def check_key_status(self):
        """Sprawdz czy klucz jest zaszyfrowany"""
        key_path = self.key_to_encrypt_path.get()
        
        if not key_path:
            messagebox.showwarning("Brak klucza", "Prosze wybrac klucz prywatny!")
            return
        
        is_encrypted, info = self.cert_manager.check_key_encryption(key_path)
        
        if is_encrypted:
            self.key_status_label.config(text=f"Status: ZASZYFROWANY ({info})", fg="green")
        else:
            self.key_status_label.config(text=f"Status: NIEZASZYFROWANY", fg="orange")
    
    def select_output_file(self):
        """Wybierz plik wyjsciowy dla zaszyfrowanego klucza"""
        filename = filedialog.asksaveasfilename(
            title="Zapisz zaszyfrowany klucz",
            defaultextension=".pem",
            filetypes=[
                ("PEM files", "*.pem"),
                ("Key files", "*.key"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.encrypted_key_output_path.set(filename)
    
    def encrypt_key(self):
        """Zaszyfruj klucz prywatny"""
        key_path = self.key_to_encrypt_path.get()
        output_path = self.encrypted_key_output_path.get()
        password = self.encryption_password.get()
        cipher = self.encryption_cipher.get()
        
        self.encryption_result.delete(1.0, tk.END)
        
        if not key_path:
            messagebox.showwarning("Brak klucza", "Prosze wybrac klucz prywatny!")
            return
        
        if not output_path:
            messagebox.showwarning("Brak sciezki", "Prosze wybrac sciezke do pliku wyjsciowego!")
            return
        
        if not password:
            messagebox.showwarning("Brak hasla", "Prosze podac haslo do szyfrowania!")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Slabe haslo", "Haslo powinno miec co najmniej 4 znaki!")
            return
        
        self.encryption_result.insert(tk.END, "Rozpoczynam szyfrowanie klucza...\n\n")
        
        # Sprawdz status przed szyfrowaniem
        is_encrypted, info = self.cert_manager.check_key_encryption(key_path)
        self.encryption_result.insert(tk.END, f"Status oryginalnego klucza: {info}\n\n")
        
        # Zaszyfruj klucz
        success, message = self.cert_manager.encrypt_private_key(key_path, output_path, password, cipher)
        
        if success:
            self.encryption_result.insert(tk.END, f"✅ {message}\n\n")
            self.encryption_result.insert(tk.END, f"Algorytm: {cipher.upper()}\n")
            self.encryption_result.insert(tk.END, f"Plik: {output_path}\n\n")
            self.encryption_result.insert(tk.END, "WAZNE: Zapisz haslo w bezpiecznym miejscu!\n")
            messagebox.showinfo("Sukces", "Klucz zaszyfrowany pomyslnie!")
        else:
            self.encryption_result.insert(tk.END, f"❌ {message}\n")
            messagebox.showerror("Blad", f"Nie udalo sie zaszyfrowac klucza:\n{message}")
    
    def create_paloalto_pem(self):
        """Utworz plik .pem dla Palo Alto"""
        # Sprawdz czy wszystkie wymagane pliki sa wybrane
        if not self.server_cert_path.get():
            messagebox.showwarning("Brak certyfikatu", "Prosze wybrac certyfikat serwera!")
            return
        
        if not self.private_key_path.get():
            messagebox.showwarning("Brak klucza", "Prosze wybrac klucz prywatny!")
            return
        
        # Wybierz miejsce zapisu
        output_path = filedialog.asksaveasfilename(
            title="Zapisz plik PEM dla Palo Alto",
            defaultextension=".pem",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")],
            initialfile="paloalto_bundle.pem"
        )
        
        if not output_path:
            return
        
        # Wyczysc wynik
        self.validation_result.delete(1.0, tk.END)
        self.validation_result.insert(tk.END, "Tworzenie pliku PEM dla Palo Alto...\n\n")
        self.root.update()
        
        # Utworz plik PEM
        success, message = self.cert_manager.create_palo_alto_pem(
            server_cert=self.server_cert_path.get(),
            private_key=self.private_key_path.get(),
            intermediate_cert=self.intermediate_cert_path.get() if self.intermediate_cert_path.get() else None,
            root_cert=self.root_cert_path.get() if self.root_cert_path.get() else None,
            output_path=output_path
        )
        
        if success:
            self.validation_result.insert(tk.END, f"✅ {message}\n")
            messagebox.showinfo("Sukces", f"Plik PEM utworzony pomyslnie!\n\n{output_path}")
        else:
            self.validation_result.insert(tk.END, f"❌ {message}\n")
            messagebox.showerror("Blad", message)



def main():
    """Uruchom aplikacje"""
    root = tk.Tk()
    app = CertValidatorApp(root)
    root.mainloop()

