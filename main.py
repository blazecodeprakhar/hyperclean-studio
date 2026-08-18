"""
HyperClean Studio - Main Application Launcher
Usage:
    python main.py              # Launch Modern GUI Application
    python main.py --cli scan   # Launch Terminal Scan
    python main.py --cli clean  # Launch Terminal Clean
"""

import sys
import argparse

# Reconfigure stdout/stderr to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass



def main():
    parser = argparse.ArgumentParser(description="HyperClean Studio - Master Cache & Junk Cleaner")
    parser.add_argument("--cli", choices=["scan", "clean"], help="Run in Terminal CLI mode")
    parser.add_argument("--dry-run", action="store_true", help="Simulate cleanup without deleting files")

    args = parser.parse_args()

    if args.cli:
        from cli.console import run_cli_scan, run_cli_clean
        if args.cli == "scan":
            run_cli_scan()
        elif args.cli == "clean":
            run_cli_clean(dry_run=args.dry_run)
    else:
        # Launch CustomTkinter Modern Desktop App
        from ui.app import HyperCleanApp
        app = HyperCleanApp()
        app.mainloop()


if __name__ == "__main__":
    main()
