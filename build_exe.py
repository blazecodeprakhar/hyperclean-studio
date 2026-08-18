"""
HyperClean Studio - Standalone Executable Builder
Run this script to package HyperClean Studio into a single portable Windows .exe file
that can be downloaded and run by anyone without needing Python installed!
Usage:
    python build_exe.py
"""

import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def build():

    print("⚡ Building HyperClean Studio Standalone Windows Executable...")
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    import os
    import shutil
    import ctypes

    root_exe = "HyperCleanStudio.exe"
    try:
        subprocess.run(["taskkill", "/F", "/IM", "HyperCleanStudio.exe"], capture_output=True)
    except Exception:
        pass

    if os.path.exists(root_exe):
        try:
            os.remove(root_exe)
        except Exception:
            pass

    # Purge PyInstaller system cache directory to force complete fresh compilation
    pyi_cache = os.path.expanduser(r"~\AppData\Local\pyinstaller")
    if os.path.exists(pyi_cache):
        try:
            shutil.rmtree(pyi_cache)
        except Exception:
            pass

    icon_path = os.path.abspath("app_icon.ico")
    icon_args = [f"--icon={icon_path}"] if os.path.exists(icon_path) else []

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=HyperCleanStudio",
        "--collect-all=customtkinter",
        "--clean",
    ] + icon_args + ["main.py"]

    print("Running PyInstaller fresh build command:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

    dist_exe = os.path.join("dist", "HyperCleanStudio.exe")
    if os.path.exists(dist_exe):
        try:
            shutil.copy(dist_exe, root_exe)
        except Exception as e:
            print(f"Warning copying to root: {e}")

    # Post-build cleanup of unwanted build files
    for item in ["build", "dist", "HyperCleanStudio.spec"]:
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item):
            shutil.rmtree(item)

    # Force Windows Shell Icon Cache to refresh
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        subprocess.run(["ie4uinit.exe", "-Show"], capture_output=True)
    except Exception:
        pass

    print("\n✅ FRESH BUILD COMPLETE & CLEANED!")
    print("Your executable with shield icon is saved at:")
    print(f" -> {os.path.abspath(root_exe)}")


if __name__ == "__main__":
    build()

