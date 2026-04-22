# 🧹 TempFileCleaner

A Windows utility that cleans temporary files, caches, and junk to free up disk space.

## What it cleans

| Category | Locations |
|---|---|
| **Temp Files** | `%TEMP%`, `Windows\Temp`, `Windows\Prefetch` |
| **Caches** | Thumbnail cache, Font cache, DirectX Shader cache |
| **Logs** | Windows logs, Error reports, Delivery Optimization cache |
| **Browser Caches** | Chrome, Edge, Firefox, Opera GX |
| **Other** | Recent documents, Windows Installer cache, Recycle Bin |

## Usage

### Quick Start / Scripts (double-click)
If you just want to run the tool without touching the command line, use these included batch scripts:

- 🚀 **`run_cleaner.bat`**: The main launcher. It automatically requests Administrator privileges (essential for deep-cleaning Windows folders like Prefetch and Windows Temp) and launches the interactive menu.
- 🔍 **`run_dryrun.bat`**: Scan-only mode. It simulates a clean, showing you exactly how much space you *would* free, but guarantees absolutely nothing is deleted.
- 📦 **`build.bat`**: Packaging tool. Double-click this to automatically install `pyinstaller` and bundle the Python script into a single, standalone **`.exe`** file inside the `dist/` folder. This `.exe` can be shared with anyone and works without Python installed!

### Command Line
```powershell
# Preview what would be cleaned
python cleaner.py --dry-run

# Run cleanup (will ask for confirmation)
python cleaner.py

# Run cleanup without confirmation prompt
python cleaner.py --yes

# Skip browser caches
python cleaner.py --skip-browsers

# Skip recycle bin
python cleaner.py --skip-recycle-bin

# Combine flags
python cleaner.py --yes --skip-browsers
```

### Flags
| Flag | Short | Description |
|---|---|---|
| `--dry-run` | `-d` | Scan only — shows reclaimable space without deleting |
| `--yes` | `-y` | Skip confirmation prompt |
| `--skip-browsers` | `-sb` | Don't touch browser caches |
| `--skip-recycle-bin` | `-sr` | Don't empty the Recycle Bin |

## Build as EXE

To compile into a standalone `.exe` (no Python needed to run it):

```powershell
# Double-click build.bat, or run manually:
pip install pyinstaller
python -m PyInstaller --onefile --console --name TempFileCleaner --uac-admin --clean cleaner.py
```

The exe will be at `dist/TempFileCleaner.exe`. It auto-requests admin privileges and works without Python installed.

## Requirements
- Python 3.10+
- Windows 10/11
- **Run as Administrator** for full cleanup (user-level cleanup works without admin)

## ⚠️ Notes
- Files currently in use by other programs will be skipped automatically
- Browser caches will regenerate over time — this is normal
- Running as admin unlocks: `Windows\Temp`, `Prefetch`, `Font Cache`, `Windows Logs`, and `Delivery Optimization`
