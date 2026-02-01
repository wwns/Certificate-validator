# OpenSSL Installation for Portable Version

This folder is prepared for portable OpenSSL installation.

## Installation Steps

1. Download OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html
2. Choose: **Win64 OpenSSL v3.x.x Light**
3. Run the installer
4. **IMPORTANT**: When asked for installation location, choose THIS folder:
   - Click "Browse" in the installer
   - Navigate to this "openssl" folder
   - The installer will create: `openssl\OpenSSL-Win64\bin\openssl.exe`

## After Installation

The folder structure should look like this:
```
CertificateValidator_Portable/
├── CertificateValidator.exe
└── openssl/
    └── OpenSSL-Win64/
        ├── bin/
        │   └── openssl.exe  <-- This is what the app needs
        ├── lib/
        └── ...
```

## Alternative: System Installation

If you don't need a portable version, you can install OpenSSL system-wide:
- Install to default location: `C:\Program Files\OpenSSL-Win64\`
- The application will automatically detect it

## Verification

After installation, run CertificateValidator.exe
- If OpenSSL is detected, you'll see: ✅ OpenSSL available
- If not detected, click "🔍 Sprawdź OpenSSL" button for help
