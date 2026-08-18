"""
HyperClean Studio - Modern Dark Theme System
Defines color palette, typography, and styling parameters for CustomTkinter UI.
"""

import customtkinter as ctk

# Configure CustomTkinter defaults
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Theme:
    # Color Palette (Dark Obsidian / Glassmorphism)
    BG_DARK = "#0F172A"         # Main background
    CARD_BG = "#1E293B"         # Card / Frame container
    CARD_HOVER = "#273549"      # Interactive item hover
    BORDER_COLOR = "#334155"    # Subtle borders

    # Brand Colors
    PRIMARY = "#3B82F6"         # Electric Blue
    PRIMARY_HOVER = "#2563EB"
    SUCCESS = "#10B981"         # Emerald Green
    SUCCESS_HOVER = "#059669"
    WARNING = "#F59E0B"         # Amber
    DANGER = "#EF4444"          # Rose Red
    DANGER_HOVER = "#DC2626"
    PURPLE = "#8B5CF6"          # Royal Purple

    # Text Colors
    TEXT_MAIN = "#F8FAFC"       # Bright Slate
    TEXT_MUTED = "#94A3B8"      # Subtle Slate
    TEXT_DARK = "#64748B"

    # Typography
    FONT_FAMILY = "Segoe UI"
    FONT_HEADER = (FONT_FAMILY, 20, "bold")
    FONT_SUBHEADER = (FONT_FAMILY, 15, "bold")
    FONT_TITLE = (FONT_FAMILY, 13, "bold")
    FONT_BODY = (FONT_FAMILY, 11, "normal")
    FONT_MUTED = (FONT_FAMILY, 10, "normal")
    FONT_STAT_NUM = (FONT_FAMILY, 22, "bold")

    # Safety Level Colors
    SAFETY_COLORS = {
        "Safe": "#10B981",        # Emerald
        "Recommended": "#3B82F6", # Blue
        "Caution": "#F59E0B",     # Amber
    }
