"""
HyperClean Studio - Core Data Models
"""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


class SafetyLevel(Enum):
    SAFE = "Safe"           # 100% safe to delete, recreated automatically (e.g. npm cache, temp files)
    RECOMMENDED = "Recommended" # Safe to delete, standard maintenance (e.g. browser cache, logs)
    CAUTION = "Caution"     # User should verify before deleting (e.g. Prefetch, AppData leftovers)


class CategoryType(Enum):
    DEV_CACHE = "Developer Caches"
    SYSTEM_JUNK = "System Junk"
    BROWSER_CACHE = "Browser Caches"
    APP_LEFTOVERS = "App Leftovers & Logs"
    SUSPICIOUS_TEMP = "Suspicious Temp Executables"
    CUSTOM = "Custom Targets"


@dataclass
class CleanTarget:
    """Represents a file or directory discovered as a potential cleanup target."""
    id: str
    name: str
    path: str
    size_bytes: int
    category: CategoryType
    safety_level: SafetyLevel
    description: str
    is_directory: bool = True
    checked: bool = True
    item_count: int = 1
    last_modified: Optional[datetime] = None

    @property
    def formatted_size(self) -> str:
        from core.utils import format_size
        return format_size(self.size_bytes)


@dataclass
class CategoryGroup:
    """Group of targets under a specific CategoryType."""
    category: CategoryType
    targets: List[CleanTarget] = field(default_factory=list)
    checked: bool = True

    @property
    def total_size_bytes(self) -> int:
        return sum(t.size_bytes for t in self.targets)

    @property
    def selected_size_bytes(self) -> int:
        return sum(t.size_bytes for t in self.targets if t.checked)

    @property
    def total_count(self) -> int:
        return len(self.targets)

    @property
    def selected_count(self) -> int:
        return sum(1 for t in self.targets if t.checked)


@dataclass
class ScanResult:
    """Aggregated results of a complete system scan."""
    groups: Dict[CategoryType, CategoryGroup] = field(default_factory=dict)
    elapsed_seconds: float = 0.0

    @property
    def total_targets(self) -> int:
        return sum(g.total_count for g in self.groups.values())

    @property
    def total_size_bytes(self) -> int:
        return sum(g.total_size_bytes for g in self.groups.values())

    @property
    def selected_targets(self) -> int:
        return sum(g.selected_count for g in self.groups.values())

    @property
    def selected_size_bytes(self) -> int:
        return sum(g.selected_size_bytes for g in self.groups.values())


@dataclass
class CleanProgressReport:
    """Report of a clean operation."""
    total_items: int = 0
    completed_items: int = 0
    freed_bytes: int = 0
    current_item: str = ""
    errors: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    finished: bool = False
