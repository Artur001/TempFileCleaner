"""
╔══════════════════════════════════════════════════╗
║          TempFileCleaner v1.0                    ║
║   Windows Temp & Junk File Cleanup Utility       ║
╚══════════════════════════════════════════════════╝

Cleans temporary files, caches, and junk from common
Windows locations to free up disk space.

Run as Administrator for full cleaning capability.
"""

import os
import sys
import shutil
import ctypes
import time
import argparse
from pathlib import Path
from datetime import datetime


# ─── ANSI Colors ────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_RED  = "\033[41m"
    BG_GREEN = "\033[42m"


def is_admin() -> bool:
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def format_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    if size_bytes < 0:
        size_bytes = 0
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def get_dir_size(path: str, check_locked: bool = False, filter_fn=None) -> int:
    """Get total size of a directory in bytes, optionally skipping locked files."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                if filter_fn and dirpath == path and not filter_fn(f):
                    continue
                fp = os.path.join(dirpath, f)
                try:
                    size = os.path.getsize(fp)
                    if check_locked:
                        try:
                            # If it can't be opened for appending, it's likely locked
                            with open(fp, 'ab'): pass
                        except (PermissionError, IOError):
                            continue
                    total += size
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total


def clean_directory(path: str, delete_root: bool = False) -> tuple[int, int, int]:
    """
    Remove all files and subdirectories inside a directory.
    Returns (files_deleted, files_failed, bytes_freed).
    """
    files_deleted = 0
    files_failed = 0
    bytes_freed = 0

    if not os.path.exists(path):
        return 0, 0, 0

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                size = os.path.getsize(item_path)
                os.unlink(item_path)
                files_deleted += 1
                bytes_freed += size
            elif os.path.isdir(item_path):
                size = get_dir_size(item_path, check_locked=True)
                shutil.rmtree(item_path, ignore_errors=False)
                files_deleted += 1
                bytes_freed += size
        except (PermissionError, OSError):
            files_failed += 1

    if delete_root:
        try:
            os.rmdir(path)
        except (PermissionError, OSError):
            pass

    return files_deleted, files_failed, bytes_freed


def print_banner():
    """Print the startup banner."""
    os.system("")  # Enable ANSI on Windows
    print()
    print(f"{C.CYAN}{C.BOLD}  ╔══════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}  ║   🧹  TempFileCleaner v1.0                      ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}  ║   Windows Junk & Temp File Cleanup               ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}  ╚══════════════════════════════════════════════════╝{C.RESET}")
    print()

    if is_admin():
        print(f"  {C.GREEN}{C.BOLD}✓ Running as Administrator{C.RESET} — full cleanup available")
    else:
        print(f"  {C.YELLOW}{C.BOLD}⚠ Not running as Administrator{C.RESET} — some locations may be skipped")
        print(f"  {C.DIM}  Right-click → 'Run as administrator' for full cleanup{C.RESET}")
    print()


def print_section(title: str):
    """Print a section header."""
    print(f"  {C.BLUE}{C.BOLD}{'─' * 50}{C.RESET}")
    print(f"  {C.BLUE}{C.BOLD}  {title}{C.RESET}")
    print(f"  {C.BLUE}{C.BOLD}{'─' * 50}{C.RESET}")


def print_result(name: str, deleted: int, failed: int, freed: int):
    """Print the result of a cleaning operation."""
    if deleted > 0 or freed > 0:
        icon = f"{C.GREEN}✓{C.RESET}"
        size_str = f"{C.GREEN}{format_size(freed)}{C.RESET}"
    elif failed > 0:
        icon = f"{C.YELLOW}~{C.RESET}"
        size_str = f"{C.YELLOW}skipped (in use){C.RESET}"
    else:
        icon = f"{C.DIM}○{C.RESET}"
        size_str = f"{C.DIM}already clean{C.RESET}"

    print(f"    {icon} {name:<35} {size_str}  {C.DIM}({deleted} removed, {failed} skipped){C.RESET}")


# ─── Cleaning Targets ──────────────────────────────────

def get_cleaning_targets() -> list[dict]:
    """Get all cleaning targets with paths and descriptions."""
    user_temp = os.environ.get("TEMP", os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Temp"))
    user_profile = os.environ.get("USERPROFILE", "")
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    windir = os.environ.get("WINDIR", r"C:\Windows")

    targets = [
        # ── User Temp Files ──
        {
            "name": "User Temp (%TEMP%)",
            "path": user_temp,
            "category": "Temporary Files",
            "admin": False,
        },
        {
            "name": "Windows Temp",
            "path": os.path.join(windir, "Temp"),
            "category": "Temporary Files",
            "admin": True,
        },
        {
            "name": "Windows Prefetch",
            "path": os.path.join(windir, "Prefetch"),
            "category": "Temporary Files",
            "admin": True,
        },

        # ── Caches ──
        {
            "name": "Thumbnail Cache",
            "path": os.path.join(local_appdata, "Microsoft", "Windows", "Explorer"),
            "category": "Caches",
            "admin": False,
            "filter": lambda f: f.startswith("thumbcache_") or f.startswith("iconcache_"),
        },
        {
            "name": "Font Cache",
            "path": os.path.join(windir, "ServiceProfiles", "LocalService", "AppData", "Local", "FontCache"),
            "category": "Caches",
            "admin": True,
        },

        # ── Logs ──
        {
            "name": "Windows Log Files",
            "path": os.path.join(windir, "Logs"),
            "category": "Log Files",
            "admin": True,
        },
        {
            "name": "Windows Error Reports",
            "path": os.path.join(local_appdata, "Microsoft", "Windows", "WER"),
            "category": "Log Files",
            "admin": False,
        },
        {
            "name": "Delivery Optimization Cache",
            "path": os.path.join(windir, "SoftwareDistribution", "Download"),
            "category": "Log Files",
            "admin": True,
        },

        # ── Browser Caches ──
        {
            "name": "Chrome Cache",
            "path": os.path.join(local_appdata, "Google", "Chrome", "User Data", "Default", "Cache"),
            "category": "Browser Caches",
            "admin": False,
        },
        {
            "name": "Edge Cache",
            "path": os.path.join(local_appdata, "Microsoft", "Edge", "User Data", "Default", "Cache"),
            "category": "Browser Caches",
            "admin": False,
        },
        {
            "name": "Firefox Cache",
            "path": os.path.join(local_appdata, "Mozilla", "Firefox", "Profiles"),
            "category": "Browser Caches",
            "admin": False,
            "subfolder": "cache2",
        },
        {
            "name": "Opera GX Cache",
            "path": os.path.join(local_appdata, "Opera Software", "Opera GX Stable", "Cache"),
            "category": "Browser Caches",
            "admin": False,
        },

        # ── Recent / History ──
        {
            "name": "Recent Documents",
            "path": os.path.join(user_profile, "AppData", "Roaming", "Microsoft", "Windows", "Recent"),
            "category": "Recent & History",
            "admin": False,
        },

        # ── Misc ──
        {
            "name": "DirectX Shader Cache",
            "path": os.path.join(local_appdata, "D3DSCache"),
            "category": "Miscellaneous",
            "admin": False,
        },
        {
            "name": "Windows Installer Cache",
            "path": os.path.join(windir, "Installer", "$PatchCache$"),
            "category": "Miscellaneous",
            "admin": True,
        },
    ]

    return targets


def clean_filtered(path: str, filter_fn) -> tuple[int, int, int]:
    """Clean only files matching a filter function."""
    files_deleted = 0
    files_failed = 0
    bytes_freed = 0

    if not os.path.exists(path):
        return 0, 0, 0

    for item in os.listdir(path):
        if filter_fn(item):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    os.unlink(item_path)
                    files_deleted += 1
                    bytes_freed += size
            except (PermissionError, OSError):
                files_failed += 1

    return files_deleted, files_failed, bytes_freed


def clean_firefox_cache(profiles_path: str) -> tuple[int, int, int]:
    """Clean Firefox cache from all profiles."""
    total_del, total_fail, total_freed = 0, 0, 0

    if not os.path.exists(profiles_path):
        return 0, 0, 0

    for profile in os.listdir(profiles_path):
        cache_path = os.path.join(profiles_path, profile, "cache2")
        if os.path.isdir(cache_path):
            d, f, b = clean_directory(cache_path)
            total_del += d
            total_fail += f
            total_freed += b

    return total_del, total_fail, total_freed


def scan_targets(targets: list[dict]) -> dict[str, int]:
    """Scan all targets and return sizes by category."""
    sizes = {}
    for t in targets:
        path = t["path"]
        if os.path.exists(path):
            if t.get("subfolder") == "cache2":
                size = 0
                for profile in os.listdir(path):
                    cache_path = os.path.join(path, profile, "cache2")
                    if os.path.isdir(cache_path):
                        size += get_dir_size(cache_path, check_locked=True)
            else:
                size = get_dir_size(path, check_locked=True, filter_fn=t.get("filter"))
            cat = t["category"]
            sizes[cat] = sizes.get(cat, 0) + size
    return sizes


def run_cleanup(targets: list[dict], dry_run: bool = False, skip_browsers: bool = False) -> tuple[int, int]:
    """Run the cleanup process. Returns (total_freed, total_deleted)."""
    total_freed = 0
    total_deleted = 0
    total_failed = 0
    current_category = None
    admin = is_admin()

    for target in targets:
        cat = target["category"]

        # Skip browser caches if requested
        if skip_browsers and cat == "Browser Caches":
            continue

        # Skip admin-only targets if not admin
        if target.get("admin") and not admin:
            if cat != current_category:
                current_category = cat
                print_section(cat)
            print(f"    {C.DIM}○ {target['name']:<35} requires admin{C.RESET}")
            continue

        if cat != current_category:
            current_category = cat
            print_section(cat)

        path = target["path"]

        if not os.path.exists(path):
            print(f"    {C.DIM}○ {target['name']:<35} not found{C.RESET}")
            continue

        if dry_run:
            if target.get("subfolder") == "cache2":
                size = 0
                for profile in os.listdir(path):
                    cache_path = os.path.join(path, profile, "cache2")
                    if os.path.isdir(cache_path):
                        size += get_dir_size(cache_path, check_locked=True)
            else:
                size = get_dir_size(path, check_locked=True, filter_fn=target.get("filter"))
                
            print(f"    {C.CYAN}? {target['name']:<35} {format_size(size)} reclaimable{C.RESET}")
            total_freed += size
            continue

        # Actual cleaning
        if "filter" in target:
            deleted, failed, freed = clean_filtered(path, target["filter"])
        elif target.get("subfolder") == "cache2":
            deleted, failed, freed = clean_firefox_cache(path)
        else:
            deleted, failed, freed = clean_directory(path)

        print_result(target["name"], deleted, failed, freed)
        total_freed += freed
        total_deleted += deleted
        total_failed += failed

    return total_freed, total_deleted


def empty_recycle_bin(dry_run: bool = False) -> int:
    """Empty the Windows Recycle Bin. Returns bytes freed."""
    print_section("Recycle Bin")

    try:
        # Get recycle bin size before emptying
        from ctypes import wintypes
        SHQueryRecycleBin = ctypes.windll.shell32.SHQueryRecycleBinW

        class SHQUERYRBINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("i64Size", ctypes.c_longlong),
                ("i64NumItems", ctypes.c_longlong),
            ]

        info = SHQUERYRBINFO()
        info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
        result = SHQueryRecycleBin(None, ctypes.byref(info))

        if result != 0 or info.i64NumItems == 0:
            print(f"    {C.DIM}○ {'Recycle Bin':<35} already empty{C.RESET}")
            return 0

        size = info.i64Size

        if dry_run:
            print(f"    {C.CYAN}? {'Recycle Bin':<35} {format_size(size)} reclaimable ({info.i64NumItems} items){C.RESET}")
            return size

        # Empty the recycle bin (no confirmation, no progress, no sound)
        SHERB_NOCONFIRMATION = 0x00000001
        SHERB_NOPROGRESSUI = 0x00000002
        SHERB_NOSOUND = 0x00000004
        flags = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND

        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        print(f"    {C.GREEN}✓ {'Recycle Bin':<35} {C.GREEN}{format_size(size)}{C.RESET}  {C.DIM}({info.i64NumItems} items removed){C.RESET}")
        return size

    except Exception as e:
        print(f"    {C.YELLOW}~ {'Recycle Bin':<35} could not access ({e}){C.RESET}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="TempFileCleaner — Windows Temp & Junk File Cleanup Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="Scan only — show what would be cleaned without deleting.")
    parser.add_argument("--skip-browsers", "-sb", action="store_true",
                        help="Skip browser cache cleaning.")
    parser.add_argument("--skip-recycle-bin", "-sr", action="store_true",
                        help="Skip emptying the Recycle Bin.")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip confirmation prompt.")

    args = parser.parse_args()

    while True:
        print_banner()

        targets = get_cleaning_targets()
        skip_recycle_bin_iteration = args.skip_recycle_bin

        # Interactive Category Selection
        if not args.yes:
            print(f"  {C.CYAN}Scanning system for reclaimable space...{C.RESET}", end="\r")
            sizes = scan_targets(targets)
            
            # Add recycle bin size
            bin_size = 0
            if not args.skip_recycle_bin:
                try:
                    from ctypes import wintypes
                    SHQueryRecycleBin = ctypes.windll.shell32.SHQueryRecycleBinW
                    class SHQUERYRBINFO(ctypes.Structure):
                        _fields_ = [("cbSize", ctypes.c_ulong),("i64Size", ctypes.c_longlong),("i64NumItems", ctypes.c_longlong)]
                    info = SHQUERYRBINFO()
                    info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
                    if SHQueryRecycleBin(None, ctypes.byref(info)) == 0:
                        bin_size = info.i64Size
                except:
                    pass
            sizes["Recycle Bin"] = bin_size

            categories = list(dict.fromkeys(t["category"] for t in targets))
            categories.append("Recycle Bin")

            print(f"  {C.CYAN}{C.BOLD}Select categories to clean:                 {C.RESET}")
            for i, cat in enumerate(categories, 1):
                size_str = format_size(sizes.get(cat, 0))
                print(f"    {C.BOLD}{i}.{C.RESET} {cat:<25} {C.YELLOW}({size_str}){C.RESET}")
                
            total_size = sum(sizes.values())
            print(f"    {C.BOLD}A.{C.RESET} {'All of the above':<25} {C.GREEN}({format_size(total_size)} total){C.RESET}")
            print(f"    {C.BOLD}Q.{C.RESET} Quit")
            print()

            try:
                choice = input(f"  {C.BOLD}  Enter choices (e.g. 1 3 4 or A for All): {C.RESET}").strip().lower()
            except KeyboardInterrupt:
                print(f"\n\n  {C.RED}Exiting.{C.RESET}\n")
                sys.exit(0)

            if choice == 'q' or choice == 'quit':
                print(f"\n  {C.CYAN}Goodbye!{C.RESET}\n")
                sys.exit(0)

            selected_categories = []
            if choice == 'a' or choice == 'all':
                selected_categories = categories
            else:
                parts = choice.replace(",", " ").split()
                for p in parts:
                    if p.isdigit():
                        idx = int(p) - 1
                        if 0 <= idx < len(categories):
                            selected_categories.append(categories[idx])

            if not selected_categories:
                print(f"\n  {C.RED}No valid categories selected. Please try again.{C.RESET}\n")
                time.sleep(1.5)
                os.system("cls" if os.name == "nt" else "clear")
                continue

            # Filter targets based on selection
            targets = [t for t in targets if t["category"] in selected_categories]
            if "Recycle Bin" not in selected_categories:
                skip_recycle_bin_iteration = True
            else:
                skip_recycle_bin_iteration = False

        if args.dry_run:
            print(f"\n  {C.CYAN}{C.BOLD}  MODE: DRY RUN (scan only, nothing will be deleted){C.RESET}\n")
        elif not args.yes:
            print(f"\n  {C.CYAN}{C.BOLD}The following targets will be cleaned:{C.RESET}")
            for t in targets:
                path_display = t["path"]
                if len(path_display) > 60:
                    path_display = "..." + path_display[-57:]
                print(f"    {C.YELLOW}-{C.RESET} {C.BOLD}{t['name']:<28}{C.RESET} {C.DIM}{path_display}{C.RESET}")
            
            if not skip_recycle_bin_iteration:
                 print(f"    {C.YELLOW}-{C.RESET} {C.BOLD}{'Recycle Bin':<28}{C.RESET} {C.DIM}Windows Recycle Bin{C.RESET}")
            
            print(f"\n  {C.YELLOW}⚠  This will permanently delete the files in these locations.{C.RESET}")
            try:
                ans = input(f"  {C.BOLD}  Proceed? (y/N): {C.RESET}").strip().lower()
            except KeyboardInterrupt:
                 sys.exit(0)
            if ans not in ("y", "yes"):
                 print(f"\n  {C.RED}Cancelled this selection.{C.RESET}\n")
                 time.sleep(1)
                 os.system("cls" if os.name == "nt" else "clear")
                 continue
            print()

        start_time = time.time()

        # Run cleanup
        total_freed, total_deleted = run_cleanup(targets, dry_run=args.dry_run, skip_browsers=args.skip_browsers)

        # Recycle bin
        if not skip_recycle_bin_iteration:
            bin_freed = empty_recycle_bin(dry_run=args.dry_run)
            total_freed += bin_freed

        elapsed = time.time() - start_time

        # Summary
        print()
        print(f"  {C.GREEN}{C.BOLD}{'═' * 50}{C.RESET}")
        if args.dry_run:
            print(f"  {C.GREEN}{C.BOLD}  SCAN COMPLETE{C.RESET}")
            print(f"  {C.GREEN}{C.BOLD}  Total reclaimable:  {format_size(total_freed)}{C.RESET}")
        else:
            print(f"  {C.GREEN}{C.BOLD}  ✓ CLEANUP COMPLETE{C.RESET}")
            print(f"  {C.GREEN}{C.BOLD}  Total freed:  {format_size(total_freed)}{C.RESET}")
            print(f"  {C.DIM}    Items processed: {total_deleted}{C.RESET}")
        print(f"  {C.DIM}    Time elapsed:    {elapsed:.1f}s{C.RESET}")
        print(f"  {C.GREEN}{C.BOLD}{'═' * 50}{C.RESET}")
        print()

        # If running purely via command line arguments with no interaction, exit after one run
        if args.yes:
             break
        
        print(f"  {C.CYAN}Press Enter to return to the main menu, or 'Q' to quit.{C.RESET}")
        try:
            cont = input().strip().lower()
            if cont == 'q' or cont == 'quit':
                break
            os.system("cls" if os.name == "nt" else "clear")
        except KeyboardInterrupt:
            break



if __name__ == "__main__":
    main()
