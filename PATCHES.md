# 补丁说明（相对上游 v5.6.0）

- 上游仓库：https://github.com/Anjok07/ultimatevocalremovergui
- 上游提交：5517e0cf0d1acd16a1618eeedec596957523f9e1
- 生成时间：2026-09-10 11:15:00

本仓库是上游代码的**非官方补丁快照**，只改了下面这些地方，其余保持原样。
所有补丁都由 `patch_uvr5.py` 自动应用，幂等、可重复执行。

| # | 文件 | 修改 | 原因 |
|---|---|---|---|
| 1 | `gui_data/app_size_values.py` | `Image.ANTIALIAS` -> `Image.Resampling.LANCZOS` | Pillow >= 10 删除了 `Image.ANTIALIAS`，不改会在启动时抛 `AttributeError`，表现为「双击没反应 / 打不开」 |
| 2 | `models/MDX_Net_Models/model_data/model_data.json` | 新增 hash `116f6f9dabb907b53d847ed9f7a9475f` -> `model_2_stem_full_band_8k.yaml` | `MDX23C-8KFFT-InstVoc_HQ_2` 未在上游模型表里注册，加载后拿不到配置，推理会卡住 |
| 3 | `lib_v5/vr_network/modelparams/*.json` | `res_type` 的 `sinc_*` -> `soxr_hq` | `sinc_*` 需要额外的 `samplerate` 包；`soxr` 随 librosa 一起装，质量相当，48 kHz 素材也不会报错 |
| 4 | `demucs/states.py`、`separate.py` | `torch.load(...)` 加 `weights_only=False` | torch >= 2.6 默认 `weights_only=True`，Demucs 权重会加载失败 |
| 5 | `separate.py` | 新增 `USE_HALF_PRECISION` / `_uvr5_amp()`，5 处推理用 `torch.autocast` 包裹 | 可选半精度加速（默认关闭）。开启后 MDX 推理约快 1.9 倍，输出差异在 1e-5 量级 |
| 6 | `gui_data/constants.py` | 新增 `LANGUAGE_*` / `HALF_PRECISION_*` 文案 | 中文界面 + 半精度开关的界面文字 |
| 7 | `gui_data/i18n.py`、`gui_data/lang/zh_CN.json`、`UVR.py` | 运行期翻译层 + 设置页语言下拉 | 界面中英切换，默认跟随系统显示语言 |
| 8 | `UVR.py` | 设置页新增「Use half precision」复选框并持久化 | 半精度开关 |
| 9 | `UVR.py` | `fill_gpu_list()` 检测到 CUDA 时默认选中第一块 N 卡 | 免去手动在设置里选显卡 |
| 10 | `requirements.txt` | 依赖版本更新到 Python 3.13 / torch cu128 | 官方依赖太旧，装不上新硬件 |
| 11 | `UVR.py`、`separate.py` | `pytorch_lightning` / `matchering` / `onnx2pytorch` 改为**按需导入** | 这三个库每次启动都会被连带加载（约 3 秒），但它们只在跑 `.ckpt` 模型 / 用 Matchering 工具 / 做 ONNX 转换时才需要。改完「双击到窗口出现」约 6 秒 -> 约 3 秒 |

> 第 3 项：安装包里另外**自带**了 `samplerate 0.2.4`，所以 `soxr_hq` 只是双保险，改回 `sinc_best` 也没问题。

## 运行环境相关（不改源码，但 Release 里的安装包已包含）

| # | 项目 | 说明 |
|---|---|---|
| A | `torch 2.11.0+cu128` | 支持 sm_120（RTX 50 系）的关键；官方旧包内置的是 CUDA 11 构建，最高只到 sm_90 |
| B | `onnxruntime-gpu 1.24.4` | 官方带的 `1.29` 需要 CUDA 13，会让 `.onnx` 模型**悄悄退回 CPU**；1.24.4 导入 `cublas64_12.dll`，与 CUDA 12.8 匹配 |
| C | `samplerate 0.2.4` | `lib_v5/spec_utils.py` 在 Windows 上用 `sinc_fastest` 重采样，缺它会报 `ModuleNotFoundError: No module named 'samplerate'` |
| D | 预热好的 CUDA 内核缓存 | RTX 50 系要现场编译约 80 MB 内核，而 NVIDIA 默认缓存上限只有 32 MB，导致**每次启动都重编译、首次推理卡 1 分钟**。安装包内置预热缓存，启动器同时把缓存上限调到 2 GB |

## 关于 RTX 50 系列（sm_120）

RTX 50 系列是 **sm_120** 架构，需要 **PyTorch >= 2.7 + CUDA 12.8** 的构建才有可用 kernel。
官方旧版安装包里内置的是 CUDA 11 / cuDNN 8 的 torch（最高只编译到 sm_90），
在 50 系卡上会出现「模型加载完成、一开始推理就卡住」的现象。
这不是改几行 Python 能修的，**必须换 torch**。Release 里的安装包已经内置了 CUDA 12.8 的便携运行时；
如果你想自己搭源码环境，请按 `requirements.txt` 安装 `torch` 的 cu128 版本。

## 模型权重

本仓库**不包含**大模型权重（`*.ckpt` / `*.onnx` / `*.th` 等），
请从官方渠道下载后放到 `models/` 对应目录。
`lib_v5/mixer.ckpt` 与 `models/VR_Models/UVR-DeNoise-Lite.pth` 是上游自带的源码资源，已保留。

## 许可

上游 README 声明代码为 MIT 许可，但上游仓库 HEAD 中缺少 `LICENSE` 文件，
因此本仓库按上游声明补上了标准 MIT 全文，版权归 Anjok07 / aufr33 及各位贡献者所有。