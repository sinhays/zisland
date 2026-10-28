# 智岛AI-ComfyUi智能工作台（算法镜像）

基于 **ComfyUI + PyTorch + CUDA** 的 AI 视频生成调度台（"导演工作台"）。镜像启动后自动拉起 ComfyUI 与后端 API，并通过网页前端提供操作界面，可驱动 MiniMax H3 等 ComfyUI 节点完成视频生成。

> 本仓库（GitHub `sinhays/zisland`）是发布到 AutoDL.art 的**算法镜像所对应的公开 Git 仓库**，位于镜像内 `/root/zisland`，供审核执行其中的"简单代码"（`verify.py`）。

---

## 镜像内容

| 路径 | 说明 |
|------|------|
| `/opt/ComfyUI` | ComfyUI 算法运行时（端口 **8188**） |
| `/opt/zvideo` | 应用代码（后端 `backend/` + 前端 `frontend/`，随镜像打包） |
| `/root/zisland` | 本公开 Git 仓库（含审核脚本 `verify.py`） |
| `/opt/zvideo/config.json` | 运行配置（由 `config.example.json` 生成，**不含密钥**） |

依赖清单见 `requirements.txt`：`fastapi / uvicorn / requests / psutil / websockets / litellm / chainlit / python-docx`。

> **Python 解释器**：镜像使用 AutoDL 基础镜像自带的 conda 环境 `/root/miniconda3/bin/python`（已软链到 `/usr/local/bin/python`），`verify.py` 与后端均运行于此。该环境**已预装** `torch 2.8.0+cu128 / fastapi / uvicorn / requests / psutil / websockets / numpy`，镜像构建时仅补充安装 `litellm / chainlit / python-docx`，因此**不重复安装 torch**，节省镜像体积。

## 环境信息

- **操作系统**：Linux（AutoDL 基础镜像）
- **CUDA**：12.8（cu128，随 AutoDL 基础镜像提供）
- **PyTorch**：2.8.0+cu128（AutoDL 基础镜像已预装，镜像内不重复安装）
- **Python**：3.12（AutoDL 基础镜像 conda 环境 `/root/miniconda3`）
- **GPU**：需要 NVIDIA GPU（AutoDL 实例提供）

## 快速开始

镜像启动（容器 `ENTRYPOINT`）会自动完成：

1. 启动 **ComfyUI** → `0.0.0.0:8188`
2. 启动 **智岛后端 API** → `0.0.0.0:8000`（同时托管网页前端）

启动后即可访问：

- 工作台前端：`http://<实例IP>:8000/`
- ComfyUI：`http://<实例IP>:8188/`

> 在 AutoDL 控制台点击 **HTTP** 按钮即可打开对应端口页面。

若自行用 Docker 运行（需宿主机有 NVIDIA 驱动 + nvidia-container-runtime）：

```bash
docker run --gpus all -p 8000:8000 -p 8188:8188 \
  -v /你的路径/config.json:/opt/zvideo/config.json:ro \
  sinhays/zisland:v1
```

## 端口说明

| 端口 | 服务 |
|------|------|
| `8000` | 智岛后端 API + 网页前端 |
| `8188` | ComfyUI |

## 配置（API Key 与模型）

镜像**不内置任何密钥**。运行前需提供真实 `config.json`（含 DeepSeek / agnes 等 Key），通过挂载传入：

```bash
-v /你的路径/config.json:/opt/zvideo/config.json:ro
```

`config.example.json` 为配置模板（已抹去密钥）。模型权重体积较大，建议运行时挂载数据盘，不烤进镜像。

## 审核与验证（AutoDL.art）

审核标准：镜像 `/root` 目录下包含本 Git 仓库，且能成功执行仓库中的"简单代码"作为环境配置合格的标准。

进入容器后执行：

```bash
cd /root/zisland
python verify.py
```

`verify.py` 依次检查（全部 `[OK]` 即合格）：

1. **PyTorch 与 CUDA 基础** —— `torch` 可导入、`torch.cuda.is_available()` 可见（GPU 实例应通过）
2. **后端依赖** —— `fastapi / uvicorn / requests / psutil / websockets / litellm / chainlit / python-docx` 均已安装
3. **后端程序就位** —— `/opt/zvideo/backend/main.py` 存在
4. **后端主程序可编译** —— `backend/main.py` 语法可编译（证明随镜像打包的算法代码可正常解析/执行）

> 注：审核只验证**环境是否合格**，不需要真正生成视频（那需要数 GB 的模型权重）。

## 关于「不公布源码」（透明说明）

本项目对源码闭源。为同时满足 AutoDL.art 审核要求与"不公开源码"的诉求，采用**双层结构**：

- **本公开仓库（你正在看的）**：只放**验证脚手架**（`verify.py` / `requirements.txt` / `run.sh` / 本说明），**不含任何 `backend/` / `frontend/` 源码**，`verify.py` 仅做环境冒烟测试，不泄露实现细节。
- **Docker 镜像**：构建时把本地 `backend/` + `frontend/`（源码）COPY 进镜像内部（`/opt/zvideo`），**源码只存在于镜像内，从不进入公开 GitHub**；镜像同时克隆本仓库到 `/root/zisland`，因此 `/root` 下既有合规的 Git 仓库，又能跑通其中的 `verify.py`。

即：✅ 镜像 = 该算法项目运行所需的 Docker 镜像；✅ `/root` 含对应 Git 仓库；✅ 能成功执行仓库中的简单代码；✅ 源码不公开。

## 真实出片还需（运行时补充）

镜像内置 ComfyUI 与 PyTorch/CUDA 基础。要真正出片，还需：

- 安装 **MiniMax H3 官方节点及权重**（即本地使用的"H3 整合包"），放入 ComfyUI 的 `custom_nodes/` 与 `models/`；
- 权重体积大，建议运行时挂载数据盘。

## 版本

- `v1`：初始发布。
