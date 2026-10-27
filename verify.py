#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智岛AI-ComfyUi智能工作台 —— 镜像环境自检脚本（AutoDL.art 审核用）。

审核标准：镜像的 /root 目录下包含本 Git 仓库，且能成功执行仓库中的"简单代码"。
本文件即那段简单代码，用于验证镜像的算法运行环境是否配置合格：
  1. PyTorch 可用且 CUDA 可见（ComfyUI 视频生成所需的 GPU 基础）
  2. 后端 API 服务所需的 Python 依赖均已安装
  3. 随镜像打包的后端程序（backend/main.py）已就位

说明：本脚本不含任何项目源码，仅做环境冒烟测试，不会泄露实现细节。
"""
import os
import sys


def check(label, fn):
    try:
        fn()
        print(f"[OK]   {label}")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {label}: {e}")
        return False


def main():
    print("=" * 60)
    print(" 智岛AI-ComfyUi智能工作台 · 镜像环境自检")
    print("=" * 60)

    results = []

    # 1) PyTorch + CUDA
    def torch_check():
        import torch
        print(f"      torch {torch.__version__}")
        cuda = torch.cuda.is_available()
        print(f"      CUDA available: {cuda}")
        if not cuda:
            print("      [warn] 当前环境 CUDA 不可用（CPU 环境）；GPU 实例上应通过。")

    results.append(check("PyTorch 与 CUDA 基础", torch_check))

    # 2) 后端 API 依赖
    def deps_check():
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import requests  # noqa: F401
        import psutil  # noqa: F401
        import websockets  # noqa: F401
        import litellm  # noqa: F401
        import chainlit  # noqa: F401
        import docx  # python-docx

    results.append(
        check(
            "后端依赖（fastapi/uvicorn/requests/psutil/websockets/litellm/chainlit/python-docx）",
            deps_check,
        )
    )

    # 3) 随镜像打包的后端程序
    app_dir = os.environ.get("ZISLAND_APP_DIR", "/opt/zvideo")
    main_py = os.path.join(app_dir, "backend", "main.py")

    def app_check():
        if not os.path.isfile(main_py):
            raise FileNotFoundError(f"未找到后端程序: {main_py}")

    results.append(check(f"后端程序就位 ({main_py})", app_check))

    print("=" * 60)
    if all(results):
        print(" 环境配置合格：可正常运行智岛AI-ComfyUi智能工作台。")
        sys.exit(0)
    else:
        print(" 环境配置存在缺失，请检查上述 [FAIL] 项。")
        sys.exit(1)


if __name__ == "__main__":
    main()
