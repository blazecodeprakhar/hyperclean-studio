"""
HyperClean Studio - Header Component
App banner, Admin privilege badge, live C: drive storage progress bar, and primary scan/clean controls.
"""

import webbrowser
import customtkinter as ctk
from ui.theme import Theme
from core.utils import is_admin, get_disk_info


class HeaderFrame(ctk.CTkFrame):
    def __init__(self, parent, on_scan_click, on_clean_click, on_dry_run_click):
        super().__init__(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )

        self.on_scan_click = on_scan_click
        self.on_clean_click = on_clean_click
        self.on_dry_run_click = on_dry_run_click

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left Column - Title & Admin Status
        self.left_box = ctk.CTkFrame(self, fg_color="transparent")
        self.left_box.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)

        title_frame = ctk.CTkFrame(self.left_box, fg_color="transparent")
        title_frame.pack(anchor="w")

        self.lbl_title = ctk.CTkLabel(
            title_frame,
            text="⚡ HyperClean Studio",
            font=Theme.FONT_HEADER,
            text_color=Theme.TEXT_MAIN,
        )
        self.lbl_title.pack(side="left")

        # Admin Badge
        admin_active = is_admin()
        badge_text = "ADMINISTRATOR" if admin_active else "USER MODE"
        badge_bg = Theme.SUCCESS if admin_active else Theme.WARNING

        self.badge = ctk.CTkLabel(
            title_frame,
            text=f" {badge_text} ",
            font=Theme.FONT_MUTED,
            text_color="#FFFFFF",
            fg_color=badge_bg,
            corner_radius=6,
        )
        self.badge.pack(side="left", padx=8)

        # Author / Watermark Badge (Clickable link to GitHub)
        self.btn_author = ctk.CTkButton(
            title_frame,
            text="by @blazecodeprakhar ↗",
            font=Theme.FONT_MUTED,
            text_color=Theme.PRIMARY,
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.CARD_HOVER,
            corner_radius=6,
            height=24,
            cursor="hand2",
            command=lambda: webbrowser.open_new_tab("https://github.com/blazecodeprakhar"),
        )
        self.btn_author.pack(side="left", padx=4)


        self.lbl_subtitle = ctk.CTkLabel(
            self.left_box,
            text="Master System & Developer Build Cache Reclaimer",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
        )
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # Drive Info Progress Bar
        disk_info = get_disk_info("C:\\")
        self.disk_info_lbl = ctk.CTkLabel(
            self.left_box,
            text=f"Drive C: {disk_info['free_str']} free of {disk_info['total_str']} ({disk_info['percent_used']}% used)",
            font=Theme.FONT_MUTED,
            text_color=Theme.TEXT_MUTED,
        )
        self.disk_info_lbl.pack(anchor="w", pady=(8, 2))

        self.disk_progress = ctk.CTkProgressBar(
            self.left_box,
            width=320,
            height=8,
            progress_color=Theme.PRIMARY,
            fg_color=Theme.BORDER_COLOR,
        )
        self.disk_progress.set(disk_info["percent_used"] / 100.0)
        self.disk_progress.pack(anchor="w")

        # Right Column - Action Buttons
        self.right_box = ctk.CTkFrame(self, fg_color="transparent")
        self.right_box.grid(row=0, column=1, sticky="ne", padx=20, pady=15)

        self.btn_scan = ctk.CTkButton(
            self.right_box,
            text="🔍 Scan System",
            font=Theme.FONT_TITLE,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            height=38,
            corner_radius=8,
            command=self.on_scan_click,
        )
        self.btn_scan.pack(side="left", padx=5)

        self.btn_dry_run = ctk.CTkButton(
            self.right_box,
            text="🧪 Dry Run",
            font=Theme.FONT_TITLE,
            fg_color=Theme.PURPLE,
            hover_color="#7C3AED",
            height=38,
            corner_radius=8,
            command=self.on_dry_run_click,
        )
        self.btn_dry_run.pack(side="left", padx=5)

        self.btn_clean = ctk.CTkButton(
            self.right_box,
            text="🧹 Clean Selected",
            font=Theme.FONT_TITLE,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            height=38,
            corner_radius=8,
            command=self.on_clean_click,
        )
        self.btn_clean.pack(side="left", padx=5)

    def refresh_disk_info(self):
        disk_info = get_disk_info("C:\\")
        self.disk_info_lbl.configure(
            text=f"Drive C: {disk_info['free_str']} free of {disk_info['total_str']} ({disk_info['percent_used']}% used)"
        )
        self.disk_progress.set(disk_info["percent_used"] / 100.0)
