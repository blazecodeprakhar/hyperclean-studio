"""
HyperClean Studio - Core Multi-Threaded Scanner Orchestrator
"""

import os
import time
import concurrent.futures
from typing import Dict, List, Callable, Optional
from core.models import ScanResult, CategoryGroup, CategoryType, CleanTarget
from core.detectors.dev_caches import scan_dev_caches
from core.detectors.system_junk import scan_system_junk
from core.detectors.browser_cache import scan_browser_cache
from core.detectors.app_leftovers import scan_app_leftovers
from core.detectors.malware_temp import scan_suspicious_temp
from core.detectors.gpu_cache import scan_gpu_cache


class SystemScanner:
    """Orchestrates parallel scanning across all target category detectors."""

    def __init__(self):
        self.user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
        self.local_app_data = os.environ.get("LOCALAPPDATA", os.path.join(self.user_profile, "AppData", "Local"))
        self.app_data = os.environ.get("APPDATA", os.path.join(self.user_profile, "AppData", "Roaming"))
        self.temp_dir = os.environ.get("TEMP", os.path.join(self.local_app_data, "Temp"))
        self.system_root = os.environ.get("SystemRoot", "C:\\Windows")

    def run_scan(self, progress_callback: Optional[Callable[[str, float], None]] = None) -> ScanResult:
        """
        Executes parallel scan across detectors and aggregates results.
        progress_callback(status_message: str, percentage: float)
        """
        start_time = time.time()
        groups: Dict[CategoryType, CategoryGroup] = {
            cat: CategoryGroup(category=cat, targets=[]) for cat in CategoryType
        }

        if progress_callback:
            progress_callback("Initializing system detectors...", 0.05)

        detectors = [
            ("Scanning Developer & Build Caches...", 0.15, lambda: scan_dev_caches(self.user_profile, self.local_app_data, self.app_data)),
            ("Scanning System Junk & Prefetch...", 0.35, lambda: scan_system_junk(self.user_profile, self.temp_dir, self.local_app_data, self.system_root)),
            ("Scanning Web Browser Caches...", 0.55, lambda: scan_browser_cache(self.local_app_data, self.app_data)),
            ("Scanning Application Leftovers...", 0.75, lambda: scan_app_leftovers(self.local_app_data, self.app_data)),
            ("Scanning GPU Shader Caches...", 0.85, lambda: scan_gpu_cache(self.local_app_data, self.app_data)),
            ("Scanning Suspicious Temp Executables...", 0.95, lambda: scan_suspicious_temp(self.temp_dir)),
        ]


        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_info = {
                executor.submit(func): (label, pct) for label, pct, func in detectors
            }

            for future in concurrent.futures.as_completed(future_to_info):
                label, pct = future_to_info[future]
                if progress_callback:
                    progress_callback(label, pct)
                try:
                    targets: List[CleanTarget] = future.result()
                    for target in targets:
                        groups[target.category].targets.append(target)
                except Exception as e:
                    print(f"Error in detector ({label}): {e}")

        # Remove empty category groups
        active_groups = {cat: grp for cat, grp in groups.items() if grp.total_count > 0}

        elapsed = round(time.time() - start_time, 2)
        if progress_callback:
            progress_callback("Scan completed!", 1.0)

        return ScanResult(groups=active_groups, elapsed_seconds=elapsed)
