# 照片生成随机跳舞视频（本地版）

这是一个**本地离线运行**的轻量工具：

- 输入：一张照片（如 `me.jpg`）
- 输出：一段“随机跳舞”风格的短视频（`dance.mp4`）

它通过给前景人物添加随机位移、旋转、节奏缩放来模拟舞动效果，无需云端服务。

## 1. 环境准备

建议 Python 3.10+。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. 快速开始

```bash
python app.py \
  --photo me.jpg \
  --output out/dance.mp4 \
  --duration 8 \
  --fps 30 \
  --size 720x1280 \
  --style random
```

## 3. 参数说明

- `--photo`：输入照片路径（必填）
- `--output`：输出视频路径（必填）
- `--duration`：时长（秒），默认 `8`
- `--fps`：帧率，默认 `30`
- `--size`：输出分辨率，默认 `720x1280`
- `--style`：舞蹈风格，可选：
  - `hiphop`：幅度较大、动感更明显
  - `swing`：摆动感更强
  - `robot`：偏机械卡点
  - `random`：每次随机一种风格
- `--seed`：随机种子（可选），用于复现同一效果

## 4. 进阶建议

- 想让人物更突出：使用背景干净、主体居中的照片。
- 想做“音乐视频”：可用 ffmpeg 后期加音轨，例如：

```bash
ffmpeg -i out/dance.mp4 -i bgm.mp3 -shortest -c:v copy -c:a aac out/dance_with_music.mp4
```

## 5. 免责声明

请仅在合法、合规、获得授权的场景中使用。
