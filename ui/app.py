"""
HyperClean Studio - Main Application Window (v2.0 Performance & Gaming Suite)
Assembles header, stat metrics cards, interactive category file tree, Game & RAM booster tab, and large files reclaimer tab.
"""

import threading
import customtkinter as ctk
from typing import List, Optional
from ui.theme import Theme
from ui.widgets.header import HeaderFrame
from ui.widgets.stat_card import StatCard
from ui.widgets.category_tree import CategoryTreeWidget
from ui.widgets.boost_tab import GameBoostTab
from ui.widgets.clean_progress import CleanProgressModal

from core.scanner import SystemScanner
from core.cleaner import SystemCleaner
from core.models import ScanResult, CleanTarget, CleanProgressReport
from core.utils import format_size, get_disk_info


class HyperCleanApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("HyperClean Studio v2.0 - Performance & Gaming Suite")
        self.geometry("1140x780")
        self.minsize(1000, 700)
        self.configure(fg_color=Theme.BG_DARK)

        import os
        if os.path.exists("app_icon.ico"):
            try:
                self.iconbitmap("app_icon.ico")
            except Exception:
                pass


        self.scanner = SystemScanner()
        self.cleaner = SystemCleaner()
        self.last_scan_result: Optional[ScanResult] = None

        # Main Grid Layout
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Header Frame
        self.header = HeaderFrame(
            self,
            on_scan_click=self.on_scan_click,
            on_clean_click=self.on_clean_click,
            on_dry_run_click=self.on_dry_run_click,
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        # 2. Stat Cards Grid (3 Columns)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)
        self.stats_frame.grid_columnconfigure(2, weight=1)

        self.card_scanned = StatCard(
            self.stats_frame,
            title="Total Scanned Junk",
            initial_value="0 B",
            subtitle="0 total targets found",
            accent_color=Theme.PRIMARY,
        )
        self.card_scanned.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.card_selected = StatCard(
            self.stats_frame,
            title="Selected for Cleanup",
            initial_value="0 B",
            subtitle="0 targets selected",
            accent_color=Theme.SUCCESS,
        )
        self.card_selected.grid(row=0, column=1, sticky="ew", padx=5)

        disk = get_disk_info("C:\\")
        self.card_disk = StatCard(
            self.stats_frame,
            title="Drive C: Free Space",
            initial_value=disk["free_str"],
            subtitle=f"{disk['used_str']} currently used ({disk['percent_used']}%)",
            accent_color=Theme.PURPLE,
        )
        self.card_disk.grid(row=0, column=2, sticky="ew", padx=(5, 0))

        # 3. Tabbed Interface (Main Cleaner, Game & RAM Booster, Large Files Reclaimer)
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.CARD_BG,
            segmented_button_fg_color=Theme.BG_DARK,
            segmented_button_selected_color=Theme.PRIMARY,
            segmented_button_selected_hover_color=Theme.PRIMARY_HOVER,
            corner_radius=10,
        )
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.tab_cleaner = self.tabview.add("🧹 Junk & Cache Cleaner")
        self.tab_booster = self.tabview.add("🚀 Game & RAM Booster")

        # Configure Tab Layouts
        self.tab_cleaner.grid_rowconfigure(0, weight=1)
        self.tab_cleaner.grid_columnconfigure(0, weight=1)

        self.tab_booster.grid_rowconfigure(0, weight=1)
        self.tab_booster.grid_columnconfigure(0, weight=1)

        # Tab 1: Interactive Category Tree
        self.tree_widget = CategoryTreeWidget(self.tab_cleaner, on_selection_changed=self.update_selection_metrics)
        self.tree_widget.grid(row=0, column=0, sticky="nsew")

        # Tab 2: Game & RAM Booster
        self.boost_widget = GameBoostTab(self.tab_booster)
        self.boost_widget.grid(row=0, column=0, sticky="nsew")


        # Perform initial scan on launch
        self.after(500, self.on_scan_click)

    def on_scan_click(self):
        """Run system scan in background thread."""
        self.header.btn_scan.configure(state="disabled", text="⏳ Scanning...")

        def _worker():
            result = self.scanner.run_scan()
            self.after(0, lambda: self._on_scan_finished(result))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_scan_finished(self, result: ScanResult):
        self.last_scan_result = result
        self.header.btn_scan.configure(state="normal", text="🔍 Scan System")

        # Load results into tree view
        self.tree_widget.load_groups(result.groups)

        # Update Scanned Card
        self.card_scanned.update_metrics(
            value=format_size(result.total_size_bytes),
            subtitle=f"{result.total_targets} total targets found in {result.elapsed_seconds}s",
        )

        self.update_selection_metrics()

    def update_selection_metrics(self):
        """Reactive calculation of selected targets & storage space."""
        if not self.last_scan_result:
            return

        selected_bytes = self.last_scan_result.selected_size_bytes
        selected_count = self.last_scan_result.selected_targets

        self.card_selected.update_metrics(
            value=format_size(selected_bytes),
            subtitle=f"{selected_count} targets selected for purge",
        )

    def get_selected_targets(self) -> List[CleanTarget]:
        selected: List[CleanTarget] = []
        if not self.last_scan_result:
            return selected

        for group in self.last_scan_result.groups.values():
            for target in group.targets:
                if target.checked:
                    selected.append(target)
        return selected

    def on_clean_click(self):
        selected_targets = self.get_selected_targets()
        if not selected_targets:
            modal = CleanProgressModal(self, title="No Targets Selected")
            modal.lbl_status.configure(text="Please check at least one item or category to clean.")
            modal.btn_close.configure(state="normal", fg_color=Theme.PRIMARY)
            return

        from ui.widgets.confirm_modal import CleanConfirmationModal

        def _execute_actual_clean():
            self._run_clean_pipeline(dry_run=False)

        CleanConfirmationModal(self, targets=selected_targets, on_confirm=_execute_actual_clean)

    def on_dry_run_click(self):
        self._run_clean_pipeline(dry_run=True)

    def _run_clean_pipeline(self, dry_run: bool):
        selected_targets = self.get_selected_targets()
        if not selected_targets:
            modal = CleanProgressModal(self, title="No Targets Selected")
            modal.lbl_status.configure(text="Please check at least one item or category to clean.")
            modal.btn_close.configure(state="normal", fg_color=Theme.PRIMARY)
            return

        title = "🧪 Dry-Run Simulation" if dry_run else "🧹 System Cache Cleanup"
        modal = CleanProgressModal(self, title=title)

        def _clean_worker():
            def _progress_cb(report: CleanProgressReport):
                self.after(0, lambda: modal.update_progress(report))

            report = self.cleaner.clean_targets(
                targets=selected_targets,
                dry_run=dry_run,
                use_recycle_bin=False,
                progress_callback=_progress_cb,
            )

            # Post clean refresh
            if not dry_run:
                self.after(0, self._on_clean_complete_refresh)

        threading.Thread(target=_clean_worker, daemon=True).start()

    def _on_clean_complete_refresh(self):
        self.header.refresh_disk_info()
        disk = get_disk_info("C:\\")
        self.card_disk.update_metrics(
            value=disk["free_str"],
            subtitle=f"{disk['used_str']} currently used ({disk['percent_used']}%)",
        )
        self.on_scan_click()
