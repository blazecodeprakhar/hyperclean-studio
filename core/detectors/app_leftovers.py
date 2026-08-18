"""
HyperClean Studio - App Leftovers & Heavy Logs Detector
Scans desktop app caches (Spotify, Discord, Teams, Slack) and detects orphaned AppData folders from uninstalled applications using Registry matching.
"""

import os
from typing import List, Set
from core.models import CleanTarget, CategoryType, SafetyLevel
from core.utils import get_dir_stats, get_installed_apps_registry


def scan_app_leftovers(local_app_data: str, app_data: str) -> List[CleanTarget]:
    targets: List[CleanTarget] = []

    # 1. Known App Caches
    known_app_caches = [
        {
            "id": "app_spotify",
            "name": "Spotify Offline Cache & Data",
            "paths": [
                os.path.join(local_app_data, "Spotify", "Storage"),
                os.path.join(local_app_data, "Spotify", "Data"),
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "Cached songs and audio streams from Spotify.",
        },
        {
            "id": "app_discord",
            "name": "Discord Media & GPU Cache",
            "paths": [
                os.path.join(app_data, "discord", "Cache"),
                os.path.join(app_data, "discord", "Code Cache"),
                os.path.join(app_data, "discord", "GPUCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Discord app media cache and Electron runtime cache.",
        },
        {
            "id": "app_slack",
            "name": "Slack App Cache",
            "paths": [
                os.path.join(app_data, "Slack", "Cache"),
                os.path.join(app_data, "Slack", "Service Worker", "CacheStorage"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Slack webview assets and image cache.",
        },
        {
            "id": "app_teams",
            "name": "Microsoft Teams Cache",
            "paths": [
                os.path.join(app_data, "Microsoft", "Teams", "Cache"),
                os.path.join(app_data, "Microsoft", "Teams", "tmp"),
                os.path.join(local_app_data, "Packages", "MSTeams_8wekyb3d8bbwe", "LocalCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Microsoft Teams call logs, avatar cache, and temporary data.",
        },
        {
            "id": "app_zoom",
            "name": "Zoom Meeting Logs & Temp",
            "paths": [
                os.path.join(app_data, "Zoom", "data"),
                os.path.join(app_data, "Zoom", "logs"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Zoom video conferencing log files and cache.",
        },
    ]

    for item in known_app_caches:
        for target_path in item["paths"]:
            if os.path.exists(target_path):
                size_bytes, file_count = get_dir_stats(target_path)
                if size_bytes > 0:
                    targets.append(
                        CleanTarget(
                            id=f"{item['id']}_{hash(target_path)}",
                            name=f"{item['name']} ({os.path.basename(target_path)})",
                            path=target_path,
                            size_bytes=size_bytes,
                            category=CategoryType.APP_LEFTOVERS,
                            safety_level=item["safety"],
                            description=item["desc"],
                            is_directory=os.path.isdir(target_path),
                            item_count=file_count,
                        )
                    )

    # 2. Intelligent Registry-backed AppData Leftover Detection
    try:
        installed_apps = get_installed_apps_registry()
        # System & core vendors to ignore during orphan search
        whitelist_vendors = {
            "microsoft", "windows", "google", "python", "pip", "npm", "yarn",
            "git", "node", "intel", "nvidia", "realtek", "amd", "adobe", "packages", "temp"
        }

        for base_dir in [local_app_data, app_data]:
            if not os.path.exists(base_dir):
                continue
            try:
                for folder_name in os.listdir(base_dir):
                    folder_path = os.path.join(base_dir, folder_name)
                    if not os.path.isdir(folder_path):
                        continue

                    lower_name = folder_name.lower()
                    if lower_name in whitelist_vendors or any(w in lower_name for w in whitelist_vendors):
                        continue

                    # Check if folder name corresponds to any installed software name in registry
                    matched = any(lower_name in app_name for app_name in installed_apps)
                    if not matched:
                        size_bytes, file_count = get_dir_stats(folder_path, max_depth=3)
                        # Only report orphaned folders >= 5 MB to prevent false alarms on minor configs
                        if size_bytes > 5 * 1024 * 1024:
                            targets.append(
                                CleanTarget(
                                    id=f"app_orphan_{hash(folder_path)}",
                                    name=f"Orphaned AppData: {folder_name}",
                                    path=folder_path,
                                    size_bytes=size_bytes,
                                    category=CategoryType.APP_LEFTOVERS,
                                    safety_level=SafetyLevel.CAUTION,
                                    description=f"Orphaned AppData directory from uninstalled application '{folder_name}'. No matching installed app found in Windows Registry.",
                                    is_directory=True,
                                    item_count=file_count,
                                    checked=False,  # Unchecked by default for caution
                                )
                            )
            except OSError:
                continue
    except Exception:
        pass

    return targets
