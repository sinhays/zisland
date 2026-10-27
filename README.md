# zisland · 智岛AI-ComfyUi智能工作台

基于 **ComfyUI + PyTorch + CUDA** 运行的 AI 视频生成调度台。本仓库是发布到
AutoDL.art 的**算法镜像所对应的公开 Git 仓库**。

## 关于「不公布源码」的说明（重要）

本项目对源码闭源。为同时满足 AutoDL.art 的审核要求与"不公开源码"的诉求，采用
**双层结构**：

- **本公开仓库（你正在看的）**：只放**验证脚手架**——`verify.py`、`requirements.txt`、
  `run.sh`、本说明。它**不含任何 `backend/` / `frontend/` 源码**，`verify.py` 仅做
  环境冒烟测试，不会泄露实现细节。
- **Docker 镜像**：在构建时把本地 `backend/` + `frontend/`（源码）COPY 进镜像内部
  （位于 `/opt/zvideo`），**源码只存在于镜像内，从不进入公开 GitHub**。镜像同时克隆
  本仓库到 `/root/zisland`，因此 `/root` 下既有合规的 Git 仓库，又能跑通其中的
  `verify.py`。

这样：✅ 镜像 = 该算法项目运行所需的 Docker 镜像；✅ `/root` 含对应 Git 仓库；
✅ 能成功执行仓库中的简单代码（`verify.py`）；✅ 源码不公开。

## 目录（公开仓库）

```
zisland/
├── verify.py            # 审核用的环境自检脚本（"简单代码"）
├── requirements.txt     # 后端运行依赖清单（公开，不含源码）
├── run.sh               # 手动启动后端的参考脚本
├── config.example.json  # 配置模板（已抹去密钥）
├── README.md
└── .gitignore
```

## 审核如何验证

审核员进入容器后执行：

```bash
cd /root/zisland
python verify.py
```

脚本会检查：PyTorch/CUDA 是否就绪、后端依赖是否装好、镜像内打包的后端程序
（`/opt/zvideo/backend/main.py`）是否就位。全部通过即"环境配置合格"。

> 注：审核只验证**环境是否合格**，不需要真正生成视频（那需要数 GB 的模型权重）。

## 发布流程（给你自己看的）

1. **推送本仓库到 GitHub**
   ```bash
   # 在 zisland-public/ 目录下
   git init
   git remote add origin https://github.com/sinhays/zisland.git
   git add -A
   git commit -m "chore: add autodl review scaffolding"
   git push -u origin main --force   # 仓库原本只有 README，覆盖即可
   ```
2. **构建镜像**（在 `E:\zisland\zvideo` 目录，需 Docker + GPU 环境）
   ```bash
   docker build -t sinhays/zisland:v1 .
   ```
3. **本地自测**（GPU 机器）
   ```bash
   docker run --rm -it --gpus all -p 8000:8000 -p 8188:8188 sinhays/zisland:v1
   docker run --rm --gpus all sinhays/zisland:v1 python /root/zisland/verify.py
   ```
4. **推送镜像**到 Docker Hub 或阿里云容器镜像服务。
5. 在 AutoDL.art 注册"应用/镜像"，填写镜像地址，审核会用 `/root/zisland/verify.py` 校验。

## 密钥与安全

镜像**不内置任何 API Key**。真实 `config.json`（含 DeepSeek / agnes 等 Key）请通过
运行时挂载提供，切勿提交到公开仓库或烤进镜像：

```bash
docker run --gpus all -p 8000:8000 -p 8188:8188 \
  -v /你的路径/config.json:/opt/zvideo/config.json:ro \
  sinhays/zisland:v1
```

## 真实运行还需要（算法运行时补充）

镜像内置了 ComfyUI 与 PyTorch/CUDA 基础。要真正出片，还需：
- 安装 **MiniMax H3 官方节点及权重**（你本地用的"H3 整合包"），放进 ComfyUI 的
  `custom_nodes/` 与 `models/`；
- 模型权重体积大，建议运行时挂载数据盘，不烤进镜像。
