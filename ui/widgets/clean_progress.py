import webbrowser
import customtkinter as ctk
from ui.theme import Theme
from core.models import CleanProgressReport
from core.utils import format_size


class CleanProgressModal(ctk.CTkToplevel):
    def __init__(self, parent, title: str = "Cleaning System Caches..."):
        super().__init__(parent)
        self.title(title)
        self.geometry("560x470")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_DARK)
        self._auto_close_job = None

        # Make modal window transient to parent and handle closing cleanly
        self.transient(parent)
        self.after(10, lambda: self.focus_force())
        self.protocol("WM_DELETE_WINDOW", self._on_close_click)

        self.grid_columnconfigure(0, weight=1)

        # Header Title
        self.lbl_title = ctk.CTkLabel(
            self,
            text=title,
            font=Theme.FONT_HEADER,
            text_color=Theme.TEXT_MAIN,
        )
        self.lbl_title.pack(pady=(18, 2))

        # Watermark Badge
        self.lbl_watermark = ctk.CTkButton(
            self,
            text="Developed by @blazecodeprakhar ↗",
            font=Theme.FONT_MUTED,
            fg_color="transparent",
            text_color=Theme.PRIMARY,
            hover_color=Theme.CARD_BG,
            cursor="hand2",
            height=22,
            command=self._open_github,
        )
        self.lbl_watermark.pack(pady=(0, 6))

        # Status text
        self.lbl_status = ctk.CTkLabel(
            self,
            text="Preparing operation...",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
        )
        self.lbl_status.pack(pady=4)

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self,
            width=480,
            height=12,
            progress_color=Theme.SUCCESS,
            fg_color=Theme.BORDER_COLOR,
        )
        self.progress.set(0.0)
        self.progress.pack(pady=8)

        # Log Activity Text Box
        self.log_box = ctk.CTkTextbox(
            self,
            width=500,
            height=210,
            font=("Consolas", 10),
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            text_color=Theme.TEXT_MAIN,
        )
        self.log_box.pack(pady=8)

        # Close button (Disabled during operation)
        self.btn_close = ctk.CTkButton(
            self,
            text="Close",
            font=Theme.FONT_TITLE,
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.CARD_HOVER,
            state="disabled",
            command=self._on_close_click,
        )
        self.btn_close.pack(pady=(4, 15))

    def _open_github(self):
        webbrowser.open_new_tab("https://github.com/blazecodeprakhar")

    def _on_close_click(self):
        if self._auto_close_job:
            self.after_cancel(self._auto_close_job)
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def update_progress(self, report: CleanProgressReport):
        if report.total_items > 0:
            pct = min(1.0, report.completed_items / report.total_items)
            self.progress.set(pct)

        self.lbl_status.configure(
            text=f"Processed {report.completed_items}/{report.total_items} items | Freed: {format_size(report.freed_bytes)}"
        )

        if report.current_item:
            self.log_box.insert("end", f"[CLEAN] {report.current_item}\n")
            self.log_box.see("end")

        if report.finished:
            # Force progress bar to 100% full upon completion
            self.progress.set(1.0)
            self.lbl_title.configure(text="✅ Cleanup Operation Complete!", text_color=Theme.SUCCESS)
            self.lbl_status.configure(
                text=f"Successfully reclaimed {format_size(report.freed_bytes)} of disk space!"
            )
            self.log_box.insert("end", f"\n=== SUMMARY ===\nTotal Space Reclaimed: {format_size(report.freed_bytes)}\n")
            if report.skipped:
                self.log_box.insert("end", f"Skipped/Locked items: {len(report.skipped)}\n")
            
            self.btn_close.configure(state="normal", text="Done", fg_color=Theme.PRIMARY)
