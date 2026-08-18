"""
HyperClean Studio - Simple & Safe Clean Confirmation Modal
Provides a clear, friendly, and non-intimidating file cleanup confirmation dialog.
Displays target names, paths, total storage size to be freed, and reassurance.
"""

import webbrowser
import customtkinter as ctk
from typing import List, Callable
from ui.theme import Theme
from core.models import CleanTarget, SafetyLevel, CategoryType
from core.utils import format_size


class CleanConfirmationModal(ctk.CTkToplevel):
    def __init__(self, parent, targets: List[CleanTarget], on_confirm: Callable[[], None]):
        super().__init__(parent)
        self.targets = targets
        self.on_confirm_callback = on_confirm

        self.title("🧹 Confirm System Cleanup - HyperClean Studio")
        self.geometry("660x540")
        self.minsize(600, 480)
        self.resizable(True, True)
        self.configure(fg_color=Theme.BG_DARK)

        # Make modal window transient to parent and handle focus/closing cleanly
        self.transient(parent)
        self.after(10, lambda: self.focus_force())
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self.total_size_bytes = sum(t.size_bytes for t in targets)
        self.has_custom_items = any(
            t.safety_level == SafetyLevel.CAUTION or t.category in (CategoryType.APP_LEFTOVERS, CategoryType.SUSPICIOUS_TEMP, CategoryType.CUSTOM)
            for t in targets
        )

        # Grid Configuration (5 Rows, 2 Columns)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Row 0: Title & Header
        self.grid_rowconfigure(1, weight=0)  # Row 1: Summary Card
        self.grid_rowconfigure(2, weight=1)  # Row 2: Target File Scroll List (Expands)
        self.grid_rowconfigure(3, weight=0)  # Row 3: Safety Checkbox
        self.grid_rowconfigure(4, weight=0)  # Row 4: Action Buttons

        # -------------------------------------------------------------
        # Row 0: Header Title & Author Link
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(16, 2))

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="🧹 Confirm System Cleanup",
            font=Theme.FONT_HEADER,
            text_color=Theme.TEXT_MAIN,
            anchor="w",
        )
        lbl_title.pack(anchor="w")

        lbl_watermark = ctk.CTkButton(
            header_frame,
            text="Developed by @blazecodeprakhar ↗",
            font=Theme.FONT_MUTED,
            fg_color="transparent",
            text_color=Theme.PRIMARY,
            hover_color=Theme.CARD_BG,
            cursor="hand2",
            height=18,
            command=self._open_github,
        )
        lbl_watermark.pack(anchor="w")

        # -------------------------------------------------------------
        # Row 1: Reassuring Summary Banner Card
        # -------------------------------------------------------------
        summary_card = ctk.CTkFrame(
            self,
            fg_color=Theme.CARD_BG,
            border_color=Theme.PRIMARY,
            border_width=1,
            corner_radius=8,
        )
        summary_card.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(4, 8))

        lbl_summary_title = ctk.CTkLabel(
            summary_card,
            text=f"Ready to free up {format_size(self.total_size_bytes)} of disk space",
            font=Theme.FONT_TITLE,
            text_color=Theme.SUCCESS,
            anchor="w",
        )
        lbl_summary_title.pack(anchor="w", padx=14, pady=(8, 2))

        sub_msg = (
            f"You have selected {len(targets)} targets for cleanup. "
            f"The files listed below will be safely deleted from your computer."
        )
        if self.has_custom_items:
            sub_msg += " (Includes custom app leftover folders selected by you)."

        lbl_summary_desc = ctk.CTkLabel(
            summary_card,
            text=sub_msg,
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
            justify="left",
            wraplength=580,
        )
        lbl_summary_desc.pack(anchor="w", padx=14, pady=(0, 8))

        # -------------------------------------------------------------
        # Row 2: Target File Scroll List (Direct Grid on Top Level)
        # -------------------------------------------------------------
        scroll_box = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=8,
        )
        scroll_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 10))
        scroll_box.grid_columnconfigure(0, weight=1)

        for idx, t in enumerate(targets):
            item_frame = ctk.CTkFrame(scroll_box, fg_color=Theme.CARD_HOVER)
            item_frame.grid(row=idx, column=0, sticky="ew", padx=4, pady=2)
            item_frame.grid_columnconfigure(0, weight=1)

            is_caution = (t.safety_level == SafetyLevel.CAUTION or t.category in (CategoryType.APP_LEFTOVERS, CategoryType.SUSPICIOUS_TEMP))
            badge_symbol = "📂" if is_caution else "✓"

            lbl_name = ctk.CTkLabel(
                item_frame,
                text=f"{badge_symbol} {t.name} ({t.formatted_size})",
                font=Theme.FONT_BODY,
                text_color=Theme.WARNING if is_caution else Theme.TEXT_MAIN,
                anchor="w",
            )
            lbl_name.grid(row=0, column=0, sticky="w", padx=10, pady=(3, 0))

            lbl_path = ctk.CTkLabel(
                item_frame,
                text=f"Path: {t.path}",
                font=Theme.FONT_MUTED,
                text_color=Theme.TEXT_MUTED,
                anchor="w",
            )
            lbl_path.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 3))

        # -------------------------------------------------------------
        # Row 3: Confirmation Checkbox
        # -------------------------------------------------------------
        self.chk_var = ctk.BooleanVar(value=True)
        self.chk_confirm = ctk.CTkCheckBox(
            self,
            text="I confirm and want to delete the selected items listed above.",
            variable=self.chk_var,
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MAIN,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            command=self._on_checkbox_toggle,
        )
        self.chk_confirm.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))

        # -------------------------------------------------------------
        # Row 4: Direct Action Buttons Grid (Cancel = Col 0, Clean = Col 1)
        # -------------------------------------------------------------
        self.btn_cancel = ctk.CTkButton(
            self,
            text="Cancel / Keep Files",
            font=Theme.FONT_TITLE,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            hover_color=Theme.CARD_HOVER,
            command=self._on_window_close,
            height=42,
        )
        self.btn_cancel.grid(row=4, column=0, sticky="ew", padx=(20, 8), pady=(0, 16))

        self.btn_delete = ctk.CTkButton(
            self,
            text="⚡ Clean Files Now",
            font=Theme.FONT_TITLE,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            command=self._on_delete_click,
            height=42,
        )
        self.btn_delete.grid(row=4, column=1, sticky="ew", padx=(8, 20), pady=(0, 16))

    def _open_github(self):
        webbrowser.open_new_tab("https://github.com/blazecodeprakhar")

    def _on_checkbox_toggle(self):
        if self.chk_var.get():
            self.btn_delete.configure(state="normal", fg_color=Theme.SUCCESS)
        else:
            self.btn_delete.configure(state="disabled", fg_color=Theme.BORDER_COLOR)

    def _on_window_close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.withdraw()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass

    def _on_delete_click(self):
        callback = self.on_confirm_callback
        parent = self.master
        self._on_window_close()
        if callback and parent:
            parent.after(50, callback)
