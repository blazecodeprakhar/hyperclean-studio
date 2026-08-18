"""
HyperClean Studio - Developer Caches Detector
Detects heavy build caches and package manager artifacts across web, python, java, rust, go, and mobile dev tools.
"""

import os
from typing import List
from core.models import CleanTarget, CategoryType, SafetyLevel
from core.utils import get_dir_stats, format_size


def scan_dev_caches(user_profile: str, local_app_data: str, app_data: str) -> List[CleanTarget]:
    targets: List[CleanTarget] = []

    dev_cache_definitions = [
        # Node.js / Web Dev
        {
            "id": "dev_npm_cache",
            "name": "NPM Package Cache",
            "paths": [
                os.path.join(local_app_data, "npm-cache"),
                os.path.join(app_data, "npm-cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Downloaded NPM packages and tarballs. Automatically re-downloaded when npm install runs.",
        },
        {
            "id": "dev_yarn_cache",
            "name": "Yarn Cache",
            "paths": [
                os.path.join(local_app_data, "Yarn", "Cache"),
                os.path.join(local_app_data, "Yarn", "v6"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Yarn package manager cached tarballs and metadata.",
        },
        {
            "id": "dev_pnpm_store",
            "name": "PNPM Cache Store",
            "paths": [
                os.path.join(local_app_data, "pnpm-store"),
                os.path.join(local_app_data, "pnpm", "cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "PNPM global package content addressable store.",
        },
        # Python
        {
            "id": "dev_pip_cache",
            "name": "Python Pip Wheel Cache",
            "paths": [
                os.path.join(local_app_data, "pip", "cache"),
                os.path.join(local_app_data, "pip", "http-v2"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Cached Python wheels and PyPI HTTP download cache.",
        },
        {
            "id": "dev_poetry_uv",
            "name": "Poetry & UV Cache",
            "paths": [
                os.path.join(local_app_data, "pypoetry", "Cache"),
                os.path.join(local_app_data, "uv", "cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Poetry virtual environment artifact cache and UV fast-pip package cache.",
        },
        # Java / Android
        {
            "id": "dev_gradle_caches",
            "name": "Gradle Build & Dependency Cache",
            "paths": [
                os.path.join(user_profile, ".gradle", "caches"),
                os.path.join(user_profile, ".gradle", "daemon"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Downloaded Gradle JARs, transformed classes, and daemon build logs.",
        },
        {
            "id": "dev_maven_repo",
            "name": "Maven Local Build Cache",
            "paths": [
                os.path.join(user_profile, ".m2", "repository"),
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "Maven local repository dependency cache.",
        },
        # Rust / Go
        {
            "id": "dev_cargo_cache",
            "name": "Rust Cargo Registry Cache",
            "paths": [
                os.path.join(user_profile, ".cargo", "registry", "cache"),
                os.path.join(user_profile, ".cargo", "git", "db"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Rust cargo downloaded crate source archives and git index databases.",
        },
        {
            "id": "dev_go_cache",
            "name": "Go Build Cache",
            "paths": [
                os.path.join(local_app_data, "go-build"),
                os.path.join(user_profile, "go", "pkg", "mod", "cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Compiled Go object files, packages, and module download archives.",
        },
        # VS Code & IDE Caches
        {
            "id": "dev_vscode_storage",
            "name": "VS Code Workspace Storage & Cache",
            "paths": [
                os.path.join(app_data, "Code", "User", "workspaceStorage"),
                os.path.join(app_data, "Code", "CachedData"),
                os.path.join(app_data, "Code", "Cache"),
                os.path.join(app_data, "Code", "CachedExtensions"),
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "VS Code state history, extension caches, and binary updates.",
        },
        # JetBrains / Android Studio
        {
            "id": "dev_jetbrains_cache",
            "name": "JetBrains / Android Studio System Caches",
            "paths": [
                os.path.join(local_app_data, "Google", "AndroidStudio*"),
                os.path.join(local_app_data, "JetBrains"),
            ],
            "safety": SafetyLevel.RECOMMENDED,
            "desc": "Indexing data, build caches, and compiled bytecode for IntelliJ, PyCharm, and Android Studio.",
        },
    ]

    for item in dev_cache_definitions:
        for path_pattern in item["paths"]:
            # Handle wildcards if any
            target_paths = [path_pattern]
            if "*" in path_pattern:
                import glob
                target_paths = glob.glob(path_pattern)

            for target_path in target_paths:
                if os.path.exists(target_path):
                    size_bytes, file_count = get_dir_stats(target_path)
                    if size_bytes > 0:
                        targets.append(
                            CleanTarget(
                                id=f"{item['id']}_{hash(target_path)}",
                                name=f"{item['name']} ({os.path.basename(target_path)})",
                                path=target_path,
                                size_bytes=size_bytes,
                                category=CategoryType.DEV_CACHE,
                                safety_level=item["safety"],
                                description=item["desc"],
                                is_directory=os.path.isdir(target_path),
                                item_count=file_count,
                            )
                        )

    return targets
