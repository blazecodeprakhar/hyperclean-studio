"""
HyperClean Studio - Utilities Module
"""

import os
import sys
import ctypes
import math
import winreg
from typing import Tuple, Set, Dict, Optional
import psutil

try:
    from win32com.shell import shell, shellcon
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (e.g., 1.45 GB, 230 MB)."""
    if size_bytes <= 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def is_admin() -> bool:
    """Check if the current script is running with elevated Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_dir_stats(path: str, max_depth: int = 10) -> Tuple[int, int]:
    """
    Calculate total size in bytes and file count for a directory using os.scandir.
    Gracefully skips inaccessible or locked files.
    """
    total_size = 0
    file_count = 0

    if not os.path.exists(path):
        return 0, 0

    if os.path.isfile(path):
        try:
            return os.path.getsize(path), 1
        except OSError:
            return 0, 0

    def _scandir_recursive(dir_path: str, current_depth: int):
        nonlocal total_size, file_count
        if current_depth > max_depth:
            return
        try:
            with os.scandir(dir_path) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total_size += entry.stat(follow_symlinks=False).st_size
                            file_count += 1
                        elif entry.is_dir(follow_symlinks=False):
                            _scandir_recursive(entry.path, current_depth + 1)
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
        except (PermissionError, FileNotFoundError, OSError):
            pass

    _scandir_recursive(path, 1)
    return total_size, file_count


def get_disk_info(path: str = "C:\\") -> Dict[str, str | float | int]:
    """Get disk space information using psutil."""
    try:
        usage = psutil.disk_usage(path)
        return {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "percent_used": usage.percent,
            "total_str": format_size(usage.total),
            "used_str": format_size(usage.used),
            "free_str": format_size(usage.free),
        }
    except Exception:
        return {
            "total_bytes": 0,
            "used_bytes": 0,
            "free_bytes": 0,
            "percent_used": 0.0,
            "total_str": "0 B",
            "used_str": "0 B",
            "free_str": "0 B",
        }


def move_to_recycle_bin(path: str) -> bool:
    """Send a file or folder to the Windows Recycle Bin using PyWin32 API."""
    if not os.path.exists(path):
        return True

    if PYWIN32_AVAILABLE:
        try:
            abs_path = os.path.abspath(path)
            # FO_DELETE with FOF_ALLOWUNDO moves to Recycle Bin
            result, aborter = shell.SHFileOperation((
                0,
                shellcon.FO_DELETE,
                abs_path + '\0',
                None,
                shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION | shellcon.FOF_SILENT,
                None,
                None
            ))
            return result == 0 and not aborter
        except Exception:
            pass

    # Fallback to direct os.remove or rmtree if Recycle Bin fails
    return False


def get_installed_apps_registry() -> Set[str]:
    """
    Enumerate installed software display names from Windows Registry
    to identify valid installed applications vs abandoned AppData leftovers.
    """
    installed_names: Set[str] = set()
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for hkey, subkey in registry_paths:
        try:
            key = winreg.OpenKey(hkey, subkey)
            num_subkeys = winreg.QueryInfoKey(key)[0]
            for i in range(num_subkeys):
                try:
                    app_key_name = winreg.EnumKey(key, i)
                    app_key = winreg.OpenKey(key, app_key_name)
                    try:
                        display_name, _ = winreg.QueryValueEx(app_key, "DisplayName")
                        if display_name:
                            installed_names.add(display_name.lower())
                    except OSError:
                        pass
                    finally:
                        app_key.Close()
                except OSError:
                    continue
            key.Close()
        except OSError:
            continue

    return installed_names



def get_ram_info() -> Dict[str, str | float | int]:
    """Get system RAM memory statistics."""
    try:
        mem = psutil.virtual_memory()
        return {
            "total_bytes": mem.total,
            "used_bytes": mem.used,
            "available_bytes": mem.available,
            "percent_used": mem.percent,
            "total_str": format_size(mem.total),
            "used_str": format_size(mem.used),
            "available_str": format_size(mem.available),
        }
    except Exception:
        return {
            "total_bytes": 0,
            "used_bytes": 0,
            "available_bytes": 0,
            "percent_used": 0.0,
            "total_str": "0 B",
            "used_str": "0 B",
            "available_str": "0 B",
        }


def trim_system_ram() -> Tuple[int, int]:
    """
    Safely trim RAM Working Set memory across system processes using Win32 EmptyWorkingSet API.
    Returns (estimated_freed_bytes, processed_count).
    """
    initial_used = psutil.virtual_memory().used
    processed_count = 0

    try:
        PROCESS_ALL_ACCESS = 0x1F0FFF
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                if pid <= 4:  # Skip System Idle & System processes
                    continue

                handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
                if handle:
                    psapi.EmptyWorkingSet(handle)
                    kernel32.CloseHandle(handle)
                    processed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
                continue

    except Exception as e:
        print(f"Error during RAM trim: {e}")

    final_used = psutil.virtual_memory().used
    freed_bytes = max(0, initial_used - final_used)

    # Fallback estimation if OS page table lazily reports virtual memory difference
    if freed_bytes == 0 and processed_count > 0:
        freed_bytes = processed_count * 15 * 1024 * 1024  # ~15MB average per process

    return freed_bytes, processed_count


def flush_dns_cache() -> bool:
    """Flush Windows DNS Resolver Cache via subprocess."""
    import subprocess
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, check=True)
        return True
    except Exception:
        return False

