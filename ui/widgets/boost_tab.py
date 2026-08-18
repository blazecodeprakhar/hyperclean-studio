"""
HyperClean Studio - Game & RAM Booster View Component
Live RAM telemetry gauge, GPU shader cache purge status, and One-Click Game Boost engine.
"""

import threading
import customtkinter as ctk
from ui.theme import Theme
from core.utils import get_ram_info, format_size
from core.optimizer import SystemOptimizer, BoostResult


class GameBoostTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.optimizer = SystemOptimizer()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left Column - Live Telemetry & Gauge
        self.left_box = ctk.CTkFrame(
            self,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        lbl_header = ctk.CTkLabel(
            self.left_box,
            text="🚀 GAME & SYSTEM RAM BOOSTER",
            font=Theme.FONT_SUBHEADER,
            text_color=Theme.TEXT_MAIN,
        )
        lbl_header.pack(anchor="w", padx=20, pady=(20, 5))

        lbl_desc = ctk.CTkLabel(
            self.left_box,
            text="Instantly trim background process RAM, flush GPU DirectX/NVIDIA/AMD shader caches, and reset network DNS for stutter-free gaming performance.",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
            wraplength=420,
            justify="left",
        )
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))

        # Live RAM Telemetry Box
        ram_info = get_ram_info()
        self.lbl_ram_title = ctk.CTkLabel(
            self.left_box,
            text=f"System RAM Memory: {ram_info['used_str']} Used ({ram_info['percent_used']}%)",
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_MAIN,
        )
        self.lbl_ram_title.pack(anchor="w", padx=20, pady=(10, 5))

        self.ram_progress = ctk.CTkProgressBar(
            self.left_box,
            width=400,
            height=14,
            progress_color=Theme.PRIMARY,
            fg_color=Theme.BORDER_COLOR,
        )
        self.ram_progress.set(ram_info["percent_used"] / 100.0)
        self.ram_progress.pack(anchor="w", padx=20, pady=(0, 15))

        # Stat pills
        stats_sub_frame = ctk.CTkFrame(self.left_box, fg_color="transparent")
        stats_sub_frame.pack(anchor="w", padx=20, pady=5)

        self.lbl_total_ram = ctk.CTkLabel(
            stats_sub_frame,
            text=f"Total: {ram_info['total_str']}",
            font=Theme.FONT_MUTED,
            text_color=Theme.TEXT_MUTED,
        )
        self.lbl_total_ram.pack(side="left", padx=(0, 15))

        self.lbl_avail_ram = ctk.CTkLabel(
            stats_sub_frame,
            text=f"Available: {ram_info['available_str']}",
            font=Theme.FONT_MUTED,
            text_color=Theme.SUCCESS,
        )
        self.lbl_avail_ram.pack(side="left")

        # One-Click Boost Button
        self.btn_boost = ctk.CTkButton(
            self.left_box,
            text="⚡ RUN ONE-CLICK GAME BOOST",
            font=Theme.FONT_SUBHEADER,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            height=46,
            corner_radius=10,
            command=self.on_boost_click,
        )
        self.btn_boost.pack(fill="x", padx=20, pady=25)

        # Right Column - Output Log & Report
        self.right_box = ctk.CTkFrame(
            self,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.right_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        lbl_log_header = ctk.CTkLabel(
            self.right_box,
            text="📋 Optimization Diagnostics Log",
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_MAIN,
        )
        lbl_log_header.pack(anchor="w", padx=15, pady=(15, 5))

        self.log_box = ctk.CTkTextbox(
            self.right_box,
            font=("Consolas", 10),
            fg_color=Theme.BG_DARK,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            text_color=Theme.TEXT_MAIN,
        )
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.log_box.insert("end", "System Optimizer Ready.\nClick 'Run One-Click Game Boost' to optimize RAM, GPU caches, and network latency.\n")

    def refresh_ram_gauge(self):
        ram_info = get_ram_info()
        self.lbl_ram_title.configure(
            text=f"System RAM Memory: {ram_info['used_str']} Used ({ram_info['percent_used']}%)"
        )
        self.ram_progress.set(ram_info["percent_used"] / 100.0)
        self.lbl_total_ram.configure(text=f"Total: {ram_info['total_str']}")
        self.lbl_avail_ram.configure(text=f"Available: {ram_info['available_str']}")

    def on_boost_click(self):
        self.btn_boost.configure(state="disabled", text="⏳ Optimizing Performance...")
        self.log_box.insert("end", "\n[BOOST] Starting Game Boost pipeline...\n")
        self.log_box.see("end")

        def _worker():
            res: BoostResult = self.optimizer.run_game_boost()
            self.after(0, lambda: self._on_boost_complete(res))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_boost_complete(self, res: BoostResult):
        self.btn_boost.configure(state="normal", text="⚡ RUN ONE-CLICK GAME BOOST")
        self.refresh_ram_gauge()

        self.log_box.insert("end", f"[RAM] Trimmed memory across {res.processes_trimmed} active background processes.\n")
        self.log_box.insert("end", f"[RAM] Reclaimed {format_size(res.ram_freed_bytes)} of physical RAM!\n")
        self.log_box.insert("end", f"[GPU] Cleared {format_size(res.gpu_freed_bytes)} of compiled GPU Shader Caches.\n")
        if res.dns_flushed:
            self.log_box.insert("end", "[NET] Flushed Windows DNS Resolver Cache successfully.\n")

        self.log_box.insert("end", f"=== BOOST COMPLETE ===\nTotal Space & Memory Reclaimed: {res.total_freed_str}\n\n")
        self.log_box.see("end")
