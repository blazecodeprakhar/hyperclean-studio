# ⚡ HyperClean Studio v2.0 - Performance & Gaming Suite

<p align="center">
  <img src="https://img.shields.io/badge/Author-blazecodeprakhar-blueviolet?style=for-the-badge&logo=github" alt="Author" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/UI-CustomTkinter-00B4D8?style=for-the-badge" alt="CustomTkinter UI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

---

## 🌟 Overview

**HyperClean Studio v2.0** is an all-in-one Windows disk cleanup and performance booster built by **[blazecodeprakhar](https://github.com/blazecodeprakhar)**. It reclaims massive disk space by targeting heavy developer build caches, system junk, browser storage, and uninstalled app leftovers, while featuring a **One-Click Game & RAM Booster** that flushes GPU shader caches and trims process RAM memory safely.

---

## 🔥 Key Features

### 🚀 1. One-Click Game & RAM Booster
- **RAM Working Set Trimming**: Safely forces background processes to release unused physical RAM back to the operating system using native Win32 `EmptyWorkingSet` APIs.
- **GPU Shader Cache Purge**: Clears compiled shader pipelines for NVIDIA (`DXCache`, `GLCache`), AMD Radeon (`DxCache`, `OglCache`), DirectX (`D3DSCache`), and Intel Arc graphics.
- **DNS Resolver Flush**: Flushes Windows DNS cache to optimize network latency for online gaming.

### 🛠️ 2. Massive Developer Cache Cleaner
- **Node.js & Web**: NPM Cache, Yarn Cache, PNPM Store & Global Cache.
- **Python**: Pip Wheel Cache, PyPI HTTP downloads, Poetry Cache, UV fast package store.
- **Java / Mobile**: Gradle Build & Dependency Cache (`.gradle/caches`), Maven Local Repo (`.m2/repository`).
- **Rust & Go**: Cargo Registry Cache (`.cargo/registry`), Git Databases, Go Build Cache (`go-build`).
- **IDE & Editors**: VS Code Workspace Storage (`workspaceStorage`), Cached Data, JetBrains / Android Studio system indexes.

### 🧹 3. Registry-Matched App Leftovers & Dropped Executables
- Cross-references `%AppData%` folders against installed software entries in the Windows Registry to identify orphaned folders from uninstalled applications.
- Flags auto-generated dropped executable scripts (`.exe`, `.bat`, `.vbs`, `.ps1`) in temporary folders.


---

## 🚀 Quickstart Guide

### Prerequisites
- Windows 10 / 11
- Python 3.10+ (Optional if using standalone `.exe`)

### Installation & Run

```bash
# Clone repository
git clone https://github.com/blazecodeprakhar/hyperclean-studio.git
cd hyperclean-studio

# Install dependencies
pip install -r requirements.txt

# Launch Application
python main.py
```

### 📦 Build Standalone Executable (.exe)

Want to distribute HyperClean Studio on the Internet so anyone can run it without Python? Run:

```bash
python build_exe.py
```
Your single portable executable will be generated in `dist/HyperCleanStudio.exe`!

---

## 📄 Author & License

Created with ❤️ by **[blazecodeprakhar](https://github.com/blazecodeprakhar)**.
Distributed under the MIT License.

> **Code Signing Notice**: Code signing provided by the [SignPath Foundation](https://signpath.org/).

