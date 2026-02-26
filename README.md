# 本地视频换脸（Face Swap）工具

这是一个**可在本地离线运行**的基础视频换脸项目脚手架，目标是：

- 输入：`source.jpg`（要替换上的人脸）和 `target.mp4`（待处理视频）
- 输出：`output.mp4`（换脸后视频）
- 默认不上传任何数据到云端

> ⚠️ 请仅在合法、合规和获得授权的场景下使用（如影视后期、匿名化、研究、本人素材处理）。

## 1. 环境准备

建议 Python 3.10。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. 下载模型

本项目使用 `insightface` 的 `inswapper_128.onnx` 模型。

1. 安装依赖后，首次运行会自动下载部分人脸分析模型。
2. `inswapper_128.onnx` 通常需手动准备，放到：

```text
./models/inswapper_128.onnx
```

## 3. 运行示例

```bash
python app.py \
  --source source.jpg \
  --target target.mp4 \
  --output output.mp4 \
  --swap-model ./models/inswapper_128.onnx
```

## 4. 常见问题

- **速度慢**：
  - 优先使用 GPU 版本 `onnxruntime-gpu`（需匹配 CUDA）。
  - 降低输入视频分辨率或帧率。
- **有些帧没换脸**：
  - 增大检测分辨率：`--det-size 640` 或更高。
  - 确保源图是清晰正脸。
- **输出音频丢失**：
  - 当前脚本聚焦视频帧处理，不处理音轨。可后处理用 ffmpeg 合并音轨。

## 5. 免责声明

使用者需对数据与产出负责，严禁用于诈骗、伪造身份、侵犯肖像权或其他违法用途。
