"""
HyperClean Studio - Browser Cache Detector
Scans web browser cache, GPU cache, and compiled JS code caches across Chrome, Edge, Firefox, Brave, Opera, and Vivaldi.
"""

import os
import glob
from typing import List
from core.models import CleanTarget, CategoryType, SafetyLevel
from core.utils import get_dir_stats


def scan_browser_cache(local_app_data: str, app_data: str) -> List[CleanTarget]:
    targets: List[CleanTarget] = []

    browser_definitions = [
        # Chrome
        {
            "id": "browser_chrome",
            "name": "Google Chrome Cache",
            "paths": [
                os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default", "Cache"),
                os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default", "Code Cache"),
                os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default", "GPUCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Google Chrome web cache, script bytecode cache, and GPU shader cache.",
        },
        # Edge
        {
            "id": "browser_edge",
            "name": "Microsoft Edge Cache",
            "paths": [
                os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "Cache"),
                os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "Code Cache"),
                os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "GPUCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Microsoft Edge browser HTTP cache, script cache, and shader cache.",
        },
        # Firefox
        {
            "id": "browser_firefox",
            "name": "Mozilla Firefox Cache",
            "paths": glob.glob(os.path.join(local_app_data, "Mozilla", "Firefox", "Profiles", "*", "cache2")),
            "safety": SafetyLevel.SAFE,
            "desc": "Mozilla Firefox offline web cache and media cache files.",
        },
        # Brave
        {
            "id": "browser_brave",
            "name": "Brave Browser Cache",
            "paths": [
                os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data", "Default", "Cache"),
                os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data", "Default", "Code Cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Brave privacy browser disk cache and V8 JS code cache.",
        },
        # Opera
        {
            "id": "browser_opera",
            "name": "Opera Browser Cache",
            "paths": [
                os.path.join(local_app_data, "Opera Software", "Opera Stable", "Cache"),
                os.path.join(app_data, "Opera Software", "Opera Stable", "Cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Opera web browser cache and asset storage.",
        },
        # Vivaldi
        {
            "id": "browser_vivaldi",
            "name": "Vivaldi Browser Cache",
            "paths": [
                os.path.join(local_app_data, "Vivaldi", "User Data", "Default", "Cache"),
                os.path.join(local_app_data, "Vivaldi", "User Data", "Default", "Code Cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Vivaldi web browser cache data.",
        },
    ]

    for item in browser_definitions:
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
                            category=CategoryType.BROWSER_CACHE,
                            safety_level=item["safety"],
                            description=item["desc"],
                            is_directory=os.path.isdir(target_path),
                            item_count=file_count,
                        )
                    )

    return targets
