"""
HyperClean Studio - GPU Shader Cache Detector
Detects NVIDIA DirectX/OpenGL/Compute shader caches, AMD Radeon shader caches, and DirectX D3DSCache.
"""

import os
from typing import List
from core.models import CleanTarget, CategoryType, SafetyLevel
from core.utils import get_dir_stats


def scan_gpu_cache(local_app_data: str, app_data: str) -> List[CleanTarget]:
    targets: List[CleanTarget] = []

    gpu_definitions = [
        # NVIDIA
        {
            "id": "gpu_nvidia_dxcache",
            "name": "NVIDIA DirectX Shader Cache",
            "paths": [
                os.path.join(local_app_data, "NVIDIA", "DXCache"),
                os.path.join(local_app_data, "NVIDIA Corporation", "NV_Cache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Compiled DirectX shader cache for NVIDIA GeForce GPUs. Automatically re-compiled by games as needed.",
        },
        {
            "id": "gpu_nvidia_glcache",
            "name": "NVIDIA OpenGL & Vulkan Cache",
            "paths": [
                os.path.join(local_app_data, "NVIDIA", "GLCache"),
                os.path.join(app_data, "NVIDIA", "ComputeCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Compiled OpenGL, Vulkan, and CUDA compute shader cache.",
        },
        # AMD
        {
            "id": "gpu_amd_dxcache",
            "name": "AMD Radeon Shader Cache",
            "paths": [
                os.path.join(local_app_data, "AMD", "DxCache"),
                os.path.join(local_app_data, "AMD", "OglCache"),
                os.path.join(local_app_data, "AMD", "VkCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Compiled DirectX, OpenGL, and Vulkan shader pipeline caches for AMD Radeon graphics.",
        },
        # DirectX System Cache
        {
            "id": "gpu_directx_d3d",
            "name": "DirectX D3D Shader Cache",
            "paths": [
                os.path.join(local_app_data, "D3DSCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Universal Windows DirectX 11/12 graphics pipeline compiled shader cache.",
        },
        # Intel
        {
            "id": "gpu_intel_cache",
            "name": "Intel Arc & HD Graphics Shader Cache",
            "paths": [
                os.path.join(local_app_data, "Intel", "ShaderCache"),
            ],
            "safety": SafetyLevel.SAFE,
            "desc": "Compiled shader cache for Intel Arc and Iris Xe graphics processors.",
        },
    ]

    for item in gpu_definitions:
        for target_path in item["paths"]:
            if os.path.exists(target_path):
                size_bytes, file_count = get_dir_stats(target_path)
                if size_bytes > 0:
                    targets.append(
                        CleanTarget(
                            id=f"{item['id']}_{hash(target_path)}",
                            name=f"{item['name']} ({os.path.basename(target_path)})",
                            path=target_path,
                            size_bytes=size_bytes,
                            category=CategoryType.SYSTEM_JUNK,
                            safety_level=item["safety"],
                            description=item["desc"],
                            is_directory=os.path.isdir(target_path),
                            item_count=file_count,
                        )
                    )

    return targets
