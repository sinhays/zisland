#!/usr/bin/env bash
# 手动启动智岛后端 API（需 ComfyUI 已运行于 127.0.0.1:8188）。
# 前端由后端通过 FastAPI 直接托管，访问 http://<host>:8000/ 即可。
set -e
APP_DIR="${ZISLAND_APP_DIR:-/opt/zvideo}"
cd "$APP_DIR"
exec python backend/main.py
