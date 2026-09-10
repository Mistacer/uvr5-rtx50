# Ultimate Vocal Remover 5 v5.6.0 — RTX 50 系兼容补丁版

**一句话**：把官方 v5.6.0 内置的 torch 换成 CUDA 12.8 构建，让 RTX 50 系（sm_120）显卡不再「加载完模型、一开始推理就卡住」。

---

## 这个版本修好了什么

| # | 问题 | 修复 |
|---|---|---|
| 1 | **RTX 50 系卡在 10%**（官方内置 torch 是 CUDA 11 / 最高 sm_90） | 换成 **PyTorch 2.11 + CUDA 12.8**，包含 `sm_120` kernel |
| 2 | 双击没反应 / 打不开（Pillow ≥ 10 删了 `Image.ANTIALIAS`） | 改为 `Image.Resampling.LANCZOS` |
| 3 | 新增的 MDX23C 模型不被识别 | 按官方算法（文件末尾 10000 KB 的 MD5）注册模型 hash |
| 4 | VR 模型 `res_type: sinc_best` 需要额外的 `samplerate` 包 | 改用内置的 `soxr_hq`，质量相当、免装包 |
| 5 | torch ≥ 2.6 默认 `weights_only=True`，Demucs 权重加载失败 | 加 `weights_only=False` |
| 6 | 启动时先弹一个黑色控制台窗口 | 启动器改用 `pythonw.exe` |
| 7 | 默认走 CPU、默认模型不对 | 默认开启 GPU、自动选中 N 卡、按包内模型自动挑默认模型 |
| 8 | 界面全英文 | 新增**中文界面**（588 条翻译），设置里可切换，安装时跟随系统语言 |
| 9 | ONNX 版 MDX 模型**悄悄跑 CPU**（自带的 `onnxruntime-gpu 1.29` 需要 CUDA 13，而 torch 是 CUDA 12.8） | 换成 **`onnxruntime-gpu 1.24.4`**（导入 `cublas64_12.dll`），ONNX 模型同样走 GPU |
| 10 | 装好后**第一次推理要等 1 分钟**（RTX 50 系是 sm_120，CUDA 要现场编译约 80 MB 内核，而默认缓存上限只有 32 MB，每次启动都得重编译） | 打包时**预先编译好内核缓存**一起装进去，并把缓存上限调到 2 GB；装完第一次推理就是快的 |
| 11 | **启动慢**（每次启动都连带加载 `pytorch_lightning`、`matchering`、`torchvision` 约 3 秒） | 改成**按需导入**：`pytorch_lightning` 只在跑 `.ckpt` 模型时加载、`matchering` 只在用 Matchering 工具时加载、`onnx2pytorch` 只在 ONNX 转 PyTorch 时加载。**双击到窗口出现：约 6 秒 → 约 3 秒** |

另外新增一个**半精度开关**（设置页，默认关闭）：5060 Ti 实测推理 205 ms/块 → 107 ms/块，约快 1.9 倍，输出差异在 1e-5 量级。

> 实测（RTX 5060 Ti + MDX23C）：冷启动首次推理 55~60 秒 → 修复后 **0.6 秒**，完整分离一首歌约 4.4 秒。
> 启动（双击到窗口出现）实测：**约 3.1 秒**（修复前约 6 秒左右）。

---

## 下载

| 文件 | 大小 | 说明 |
|---|---|---|
| `UVR5-5.6.0-Setup.exe.001` / `.002` | 约 1.1 GB × 2 | 完整安装包分卷：便携 Python 3.13 + torch 2.11 CUDA 12.8 + 常用模型 + 中文界面 |
| `HOW-TO-MERGE.txt` | — | 分卷合并方法（cmd / PowerShell 两种写法） |
| `SHA256SUMS.txt` | — | 合并后安装包的校验值 |
| 源码 | — | 本仓库 `main` 分支（不含模型权重） |

> **关于分卷**：GitHub 单个 Release 资产上限 2 GB，所以安装包被拆成 `UVR5-5.6.0-Setup.exe.001` / `.002` 两个分卷。
> 请把分卷下载到同一个文件夹，按 `HOW-TO-MERGE.txt` 合并，再用 `SHA256SUMS.txt` 校验。

---

## 系统要求

- Windows 10 / 11 64 位
- **NVIDIA 显卡**，驱动 **570 以上**（建议直接更新到最新）
  - 支持 RTX 20 / 30 / 40 / 50 全系；内置架构：`sm_75 / sm_80 / sm_86 / sm_90 / sm_100 / sm_120`
  - 非 N 卡会自动退回 CPU（很慢，不推荐）
- 显存：6 GB 可跑，8 GB 以上更稳（开启半精度可省显存）
- 磁盘：至少 12 GB 空闲

---

## 安装与使用

1. 下载 `UVR5-5.6.0-Setup.exe`，双击
2. 选择安装目录（**不要装到 `C:\Program Files`**，需要管理员权限会导致解压失败）
3. 勾选「同时卸载旧版 `D:\UVR`」（如果检测到）
4. 装完双击桌面图标即可

首次运行若出现 Windows SmartScreen 提示，点「更多信息」→「仍要运行」（安装包没有代码签名）。

**安装后要点**
- 主界面「GPU Conversion」默认已勾选，设置里的显卡会自动选中你的 N 卡
- 安装包**不含** MDX23C 模型，默认模型是 `1_HP-UVR`；想要 MDX23C 的效果，把 `MDX23C-8KFFT-InstVoc_HQ_2.ckpt` 放到
  `<安装目录>\app\models\MDX_Net_Models\`，重启后在主界面选择即可
- 界面语言：设置 → 语言 / Language，切换后重启

---

## 已知限制

- 安装包约 2.2 GB，**不支持 FAT32**（单文件 > 4 GB 限制），请放在 NTFS 盘上
- 装到 `C:\Program Files` 这类需要管理员权限的目录时，CUDA 缓存写不进去，启动器会自动改用 `%LOCALAPPDATA%\UVR5\cuda-cache`（首次启动多一次复制，约 1 秒）
- 设置页里的「Matchering」音频工具点了会报 `save_audiofile` 不存在 —— 这是上游 v5.6.0 自带的 bug
  （它用的 `matchering 2.0.6` 里没有这个函数），和本次修复无关，VR / MDX / Demucs 分离都不受影响。

---

## 许可与致谢

- 上游项目：[Anjok07/ultimatevocalremovergui](https://github.com/Anjok07/ultimatevocalremovergui)，MIT 许可
- 本仓库是**非官方补丁版**，只做了兼容性修复与中文界面，代码版权归 Anjok07 / aufr33 及各位贡献者所有
- 详细补丁清单见 [`PATCHES.md`](PATCHES.md)
