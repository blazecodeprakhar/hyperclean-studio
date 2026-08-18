"""
HyperClean Studio - Stat Card Component
Displays live metric counters with icon titles, values, and subtitles.
"""

import customtkinter as ctk
from ui.theme import Theme


class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title: str, initial_value: str = "0 B", subtitle: str = "0 files selected", accent_color: str = Theme.PRIMARY):
        super().__init__(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=10,
        )

        self.grid_columnconfigure(0, weight=1)

        # Title Label
        self.lbl_title = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        self.lbl_title.pack(anchor="w", padx=15, pady=(12, 2))

        # Main Value Display
        self.lbl_value = ctk.CTkLabel(
            self,
            text=initial_value,
            font=Theme.FONT_STAT_NUM,
            text_color=accent_color,
            anchor="w",
        )
        self.lbl_value.pack(anchor="w", padx=15, pady=0)

        # Subtitle / Counter
        self.lbl_sub = ctk.CTkLabel(
            self,
            text=subtitle,
            font=Theme.FONT_MUTED,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        self.lbl_sub.pack(anchor="w", padx=15, pady=(2, 12))


    def update_metrics(self, value: str, subtitle: str = ""):
        self.lbl_value.configure(text=value)
        if subtitle:
            self.lbl_sub.configure(text=subtitle)
