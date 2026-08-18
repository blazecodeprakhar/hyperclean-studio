"""
HyperClean Studio - Category & File Tree Component
Interactive scrollable file explorer with master and individual checkmarks, safety badges, search filtering, and live selection callbacks.
"""

import customtkinter as ctk
from typing import Dict, List, Callable, Optional
from core.models import CategoryType, CategoryGroup, CleanTarget, SafetyLevel
from ui.theme import Theme


class TargetRowItem(ctk.CTkFrame):
    """Single file/directory target row with checkmark, details, safety badge, and size."""

    def __init__(self, parent, target: CleanTarget, on_toggle_callback: Callable[[], None]):
        super().__init__(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=6,
        )
        self.target = target
        self.on_toggle_callback = on_toggle_callback

        self.grid_columnconfigure(1, weight=1)

        # Checkbox
        self.chk_var = ctk.BooleanVar(value=target.checked)
        self.chk = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.chk_var,
            width=24,
            height=24,
            command=self._on_check_changed,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
        )
        self.chk.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")

        # Name and Path Box
        details_box = ctk.CTkFrame(self, fg_color="transparent")
        details_box.grid(row=0, column=1, padx=5, pady=6, sticky="ew")

        lbl_name = ctk.CTkLabel(
            details_box,
            text=target.name,
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_MAIN,
            anchor="w",
        )
        lbl_name.pack(anchor="w")

        lbl_path = ctk.CTkLabel(
            details_box,
            text=target.path,
            font=Theme.FONT_MUTED,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        lbl_path.pack(anchor="w")

        # Right Meta Box (Safety badge + Size)
        meta_box = ctk.CTkFrame(self, fg_color="transparent")
        meta_box.grid(row=0, column=2, padx=(5, 12), pady=6, sticky="e")

        # Safety Level Badge
        safety_color = Theme.SAFETY_COLORS.get(target.safety_level.value, Theme.PRIMARY)
        lbl_safety = ctk.CTkLabel(
            meta_box,
            text=f" {target.safety_level.value} ",
            font=Theme.FONT_MUTED,
            text_color="#FFFFFF",
            fg_color=safety_color,
            corner_radius=4,
        )
        lbl_safety.pack(side="left", padx=5)

        # Item Count
        lbl_count = ctk.CTkLabel(
            meta_box,
            text=f"{target.item_count:,} items",
            font=Theme.FONT_MUTED,
            text_color=Theme.TEXT_MUTED,
        )
        lbl_count.pack(side="left", padx=5)

        # Formatted Size
        lbl_size = ctk.CTkLabel(
            meta_box,
            text=target.formatted_size,
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_MAIN,
        )
        lbl_size.pack(side="left", padx=5)

    def _on_check_changed(self):
        self.target.checked = self.chk_var.get()
        self.on_toggle_callback()

    def set_checked(self, checked: bool):
        self.target.checked = checked
        self.chk_var.set(checked)


class CategoryGroupWidget(ctk.CTkFrame):
    """Category Section containing master checkbox and child TargetRowItems."""

    def __init__(self, parent, group: CategoryGroup, on_selection_changed: Callable[[], None]):
        super().__init__(
            parent,
            fg_color="transparent",
        )
        self.group = group
        self.on_selection_changed = on_selection_changed
        self.rows: List[TargetRowItem] = []

        self.grid_columnconfigure(0, weight=1)

        # Header Frame
        header = ctk.CTkFrame(
            self,
            fg_color=Theme.BORDER_COLOR,
            corner_radius=8,
            height=40,
        )
        header.pack(fill="x", pady=(10, 4))
        header.grid_columnconfigure(1, weight=1)

        # Master Checkbox
        self.master_chk_var = ctk.BooleanVar(value=group.checked)
        self.master_chk = ctk.CTkCheckBox(
            header,
            text="",
            variable=self.master_chk_var,
            width=24,
            height=24,
            command=self._on_master_check_changed,
            checkbox_width=20,
            checkbox_height=20,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
        )
        self.master_chk.grid(row=0, column=0, padx=(12, 6), pady=8, sticky="w")

        # Category Title
        self.lbl_title = ctk.CTkLabel(
            header,
            text=f"{group.category.value}",
            font=Theme.FONT_SUBHEADER,
            text_color=Theme.TEXT_MAIN,
            anchor="w",
        )
        self.lbl_title.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        # Category Size & Count Pill
        from core.utils import format_size
        self.lbl_stats = ctk.CTkLabel(
            header,
            text=f"Total: {format_size(group.total_size_bytes)} ({group.total_count} targets)",
            font=Theme.FONT_TITLE,
            text_color=Theme.PRIMARY,
        )
        self.lbl_stats.grid(row=0, column=2, padx=12, pady=8, sticky="e")

        # Child Rows Container
        self.child_container = ctk.CTkFrame(self, fg_color="transparent")
        self.child_container.pack(fill="x", padx=10)

        for target in group.targets:
            row = TargetRowItem(self.child_container, target, self._on_item_toggled)
            row.pack(fill="x", pady=2)
            self.rows.append(row)

    def _on_master_check_changed(self):
        val = self.master_chk_var.get()
        self.group.checked = val
        for row in self.rows:
            row.set_checked(val)
        self.on_selection_changed()

    def _on_item_toggled(self):
        # Update master check state based on children
        all_checked = all(r.target.checked for r in self.rows)
        self.master_chk_var.set(all_checked)
        self.group.checked = all_checked
        self.on_selection_changed()

    def filter_items(self, query: str):
        """Show or hide rows matching search query."""
        visible_count = 0
        for row in self.rows:
            if not query or query in row.target.name.lower() or query in row.target.path.lower():
                row.pack(fill="x", pady=2)
                visible_count += 1
            else:
                row.pack_forget()

        if visible_count == 0 and query:
            self.pack_forget()
        else:
            self.pack(fill="x")


class CategoryTreeWidget(ctk.CTkFrame):
    """Main Container Widget hosting Search bar, Quick Selection buttons, and Scrollable Category list."""

    def __init__(self, parent, on_selection_changed: Callable[[], None]):
        super().__init__(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=10,
        )
        self.on_selection_changed = on_selection_changed
        self.group_widgets: List[CategoryGroupWidget] = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Toolbar Frame (Search + Selection Presets)
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        toolbar.grid_columnconfigure(0, weight=1)

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔎 Search targets by name, path, or extension...",
            font=Theme.FONT_BODY,
            height=34,
            border_color=Theme.BORDER_COLOR,
            fg_color=Theme.BG_DARK,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        # Preset Action Buttons
        presets_box = ctk.CTkFrame(toolbar, fg_color="transparent")
        presets_box.grid(row=0, column=1, sticky="e")

        btn_select_all = ctk.CTkButton(
            presets_box,
            text="Select All",
            font=Theme.FONT_MUTED,
            width=80,
            height=30,
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.CARD_HOVER,
            command=lambda: self._set_all_selection(True),
        )
        btn_select_all.pack(side="left", padx=2)

        btn_deselect_all = ctk.CTkButton(
            presets_box,
            text="Deselect All",
            font=Theme.FONT_MUTED,
            width=80,
            height=30,
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.CARD_HOVER,
            command=lambda: self._set_all_selection(False),
        )
        btn_deselect_all.pack(side="left", padx=2)

        btn_recommended = ctk.CTkButton(
            presets_box,
            text="Safe & Recommended Only",
            font=Theme.FONT_MUTED,
            width=160,
            height=30,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._select_recommended_only,
        )
        btn_recommended.pack(side="left", padx=2)

        # Scrollable Frame for Categories
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.BORDER_COLOR,
            scrollbar_button_hover_color=Theme.PRIMARY,
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def load_groups(self, groups: Dict[CategoryType, CategoryGroup]):
        """Populate category list from scan result."""
        # Clear existing
        for gw in self.group_widgets:
            gw.destroy()
        self.group_widgets.clear()

        if not groups:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="Click 'Scan System' to analyze system junk, developer caches, and browser storage.",
                font=Theme.FONT_SUBHEADER,
                text_color=Theme.TEXT_MUTED,
            )
            empty_lbl.pack(pady=60)
            return

        for cat, group in groups.items():
            if group.total_count > 0:
                gw = CategoryGroupWidget(self.scroll_frame, group, self.on_selection_changed)
                gw.pack(fill="x", pady=4)
                self.group_widgets.append(gw)

    def _on_search_key(self, event):
        query = self.search_entry.get().strip().lower()
        for gw in self.group_widgets:
            gw.filter_items(query)

    def _set_all_selection(self, checked: bool):
        for gw in self.group_widgets:
            gw.master_chk_var.set(checked)
            gw._on_master_check_changed()

    def _select_recommended_only(self):
        for gw in self.group_widgets:
            for row in gw.rows:
                # Select Safe and Recommended, uncheck Caution items
                is_rec = row.target.safety_level in (SafetyLevel.SAFE, SafetyLevel.RECOMMENDED)
                row.set_checked(is_rec)
            gw._on_item_toggled()
