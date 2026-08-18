"""
HyperClean Studio - Performance & Game Booster Engine
Executes RAM memory trimming, GPU shader cache purge, and network DNS flushing for maximum gaming speed.
"""

import os
from dataclasses import dataclass
from core.utils import trim_system_ram, flush_dns_cache, format_size, get_ram_info
from core.detectors.gpu_cache import scan_gpu_cache
from core.cleaner import SystemCleaner


@dataclass
class BoostResult:
    ram_freed_bytes: int = 0
    gpu_freed_bytes: int = 0
    processes_trimmed: int = 0
    dns_flushed: bool = False

    @property
    def total_freed_bytes(self) -> int:
        return self.ram_freed_bytes + self.gpu_freed_bytes

    @property
    def total_freed_str(self) -> str:
        return format_size(self.total_freed_bytes)


class SystemOptimizer:
    """Orchestrates Game Boost & RAM optimization pipelines."""

    def __init__(self):
        self.user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
        self.local_app_data = os.environ.get("LOCALAPPDATA", os.path.join(self.user_profile, "AppData", "Local"))
        self.app_data = os.environ.get("APPDATA", os.path.join(self.user_profile, "AppData", "Roaming"))

    def run_game_boost(self) -> BoostResult:
        """
        Executes safe Game Boost optimization:
        1. Trims Working Set memory across background processes.
        2. Clears GPU Shader Caches (NVIDIA, AMD, DirectX, Intel).
        3. Flushes DNS cache for reduced gaming network latency.
        """
        # 1. Trim RAM
        ram_freed, procs_trimmed = trim_system_ram()

        # 2. Clear GPU Shader Caches
        gpu_targets = scan_gpu_cache(self.local_app_data, self.app_data)
        gpu_freed = 0

        if gpu_targets:
            cleaner = SystemCleaner()
            report = cleaner.clean_targets(gpu_targets, dry_run=False)
            gpu_freed = report.freed_bytes

        # 3. Flush DNS
        dns_ok = flush_dns_cache()

        return BoostResult(
            ram_freed_bytes=ram_freed,
            gpu_freed_bytes=gpu_freed,
            processes_trimmed=procs_trimmed,
            dns_flushed=dns_ok,
        )
