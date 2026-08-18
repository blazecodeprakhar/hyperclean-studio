"""
HyperClean Studio - System Junk Detector
Detects Windows system temp files, prefetch, crash dumps, Windows Update leftovers, and Recycle Bin.
"""

import os
from typing import List
from core.models import CleanTarget, CategoryType, SafetyLevel
from core.utils import get_dir_stats


def scan_system_junk(user_profile: str, temp_dir: str, local_app_data: str, system_root: str = "C:\\Windows") -> List[CleanTarget]:
    targets: List[CleanTarget] = []

    system_definitions = [
        {
            "id": "sys_user_temp",
            "name": "User Temporary Files",
            "paths": [temp_dir],
            "safety": SafetyLevel.SAFE,
            "desc": "Temporary files created by running applications. Safe to remove.",
        },
        {
            "id": "sys_windows_temp",
            "name": "Windows System Temp",
            "paths": [os.path.join(system_root, "Temp")],
            "safety": SafetyLevel.SAFE,
            "desc": "System-level temporary files created by Windows OS services.",
        },
        {
            "id": "sys_crash_dumps",
            "name": "Windows Crash Dumps & WER",
            "paths": [
                os.path.join(local_app_data, "CrashDumps"),
                os.path.join(local_app_data, "Microsoft", "Windows", "WER"),
                os.path.join(system_root, "minidump"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Memory dump files (.dmp) and error reporting diagnostics generated during app crashes.",
        },
        {
            "id": "sys_softwaredist",
            "name": "Windows Update Download Cache",
            "paths": [
                os.path.join(system_root, "SoftwareDistribution", "Download"),
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "Downloaded installation packages for Windows Updates already installed.",
        },
        {
            "id": "sys_prefetch",
            "name": "Windows Prefetch Cache",
            "paths": [
                os.path.join(system_root, "Prefetch"),
            ],
            "safety": SafetyLevel.CAUTION,
            "desc": "Prefetch data used to speed up application launch times. Cleaning can free space but apps may launch slightly slower initially.",
        },
        {
            "id": "sys_windows_logs",
            "name": "Windows System Logs & Setup Diagnostics",
            "paths": [
                os.path.join(system_root, "Logs"),
                os.path.join(system_root, "debug"),
                os.path.join(system_root, "Panther"),
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "Diagnostic logs and installation history reports.",
        },
        {
            "id": "sys_thumbcache",
            "name": "Windows Thumbnail & Icon Cache",
            "paths": [
                os.path.join(local_app_data, "Microsoft", "Windows", "Explorer"),
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "Cached image and document thumbnail database files (thumbcache_*.db).",
        },
        {
            "id": "sys_recycle_bin",
            "name": "Recycle Bin",
            "paths": [
                "C:\\$Recycle.Bin",
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "Deleted files stored in the Windows Recycle Bin waiting to be permanently purged.",
        },
    ]

    for item in system_definitions:
        for target_path in item["paths"]:
            if os.path.exists(target_path):
                size_bytes, file_count = get_dir_stats(target_path)
                if size_bytes > 0:
                    targets.append(
                        CleanTarget(
                            id=f"{item['id']}_{hash(target_path)}",
                            name=item["name"],
                            path=target_path,
                            size_bytes=size_bytes,
                            category=CategoryType.SYSTEM_JUNK,
                            safety_level=item["safety"],
                            description=item["desc"],
                            is_directory=os.path.isdir(target_path),
                            item_count=file_count,
                        )
                    )

    return targets
