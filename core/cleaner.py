"""
HyperClean Studio - Safe Deletion Engine
Handles dry-run simulation, permanent deletion, Recycle Bin routing, and file-lock recovery.
"""

import os
import shutil
import stat
from typing import List, Callable, Optional
from core.models import CleanTarget, CleanProgressReport
from core.utils import move_to_recycle_bin, format_size


class SystemCleaner:
    """Safely executes deletion or dry-run simulation for selected targets."""

    @staticmethod
    def _force_remove_readonly(func, path, exc_info):
        """Error handler for shutil.rmtree to remove read-only attributes on file lock."""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    def clean_targets(
        self,
        targets: List[CleanTarget],
        dry_run: bool = False,
        use_recycle_bin: bool = False,
        progress_callback: Optional[Callable[[CleanProgressReport], None]] = None,
    ) -> CleanProgressReport:
        """
        Executes cleanup for the selected targets.
        Supports Dry-Run mode to simulate deletion without modifying disk.
        """
        report = CleanProgressReport(total_items=len(targets))

        for idx, target in enumerate(targets):
            report.completed_items = idx + 1
            report.current_item = f"{target.name} ({target.formatted_size})"

            if dry_run:
                # Simulate deletion
                report.freed_bytes += target.size_bytes
                if progress_callback:
                    progress_callback(report)
                continue

            # Real Deletion
            try:
                if not os.path.exists(target.path):
                    report.freed_bytes += target.size_bytes
                    continue

                if use_recycle_bin and target.safety_level != target.safety_level.SAFE:
                    success = move_to_recycle_bin(target.path)
                    if success:
                        report.freed_bytes += target.size_bytes
                        if progress_callback:
                            progress_callback(report)
                        continue

                # Direct File / Folder purge
                if target.is_directory or os.path.isdir(target.path):
                    shutil.rmtree(target.path, onerror=self._force_remove_readonly)
                else:
                    try:
                        os.chmod(target.path, stat.S_IWRITE)
                        os.remove(target.path)
                    except OSError:
                        pass

                # Verify deletion or space recovery
                if not os.path.exists(target.path):
                    report.freed_bytes += target.size_bytes
                else:
                    report.skipped.append(f"Locked file in use: {target.name}")

            except Exception as e:
                report.errors.append(f"Failed to clean '{target.name}': {str(e)}")

            if progress_callback:
                progress_callback(report)

        report.finished = True
        return report
