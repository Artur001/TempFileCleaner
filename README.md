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

### Quick Start (double-click)
- **`run_cleaner.bat`** — Full cleanup (auto-requests admin)
- **`run_dryrun.bat`** — Preview only (shows what *would* be cleaned)

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
