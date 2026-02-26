#!/usr/bin/env python3
"""照片生成随机跳舞视频工具.

示例:
python app.py --photo input.jpg --output dance.mp4 --duration 8 --fps 30 --style random
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

import cv2
import numpy as np


DANCE_STYLES = ("hiphop", "swing", "robot", "random")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从单张照片合成随机跳舞视频")
    parser.add_argument("--photo", required=True, type=Path, help="输入照片路径")
    parser.add_argument("--output", required=True, type=Path, help="输出视频路径 (mp4)")
    parser.add_argument("--duration", type=float, default=8.0, help="视频时长（秒）")
    parser.add_argument("--fps", type=int, default=30, help="帧率")
    parser.add_argument("--size", default="720x1280", help="输出分辨率，例如 720x1280")
    parser.add_argument("--style", choices=DANCE_STYLES, default="random", help="舞蹈风格")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现")
    return parser.parse_args()


def parse_size(size_text: str) -> tuple[int, int]:
    try:
        w, h = size_text.lower().split("x")
        width, height = int(w), int(h)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"无效分辨率格式: {size_text}, 应为 720x1280") from exc
    if width <= 0 or height <= 0:
        raise ValueError("分辨率必须为正整数")
    return width, height


def build_background(src_img: np.ndarray, width: int, height: int) -> np.ndarray:
    """创建背景层：基于原图拉伸 + 高斯模糊。"""
    bg = cv2.resize(src_img, (width, height), interpolation=cv2.INTER_CUBIC)
    bg = cv2.GaussianBlur(bg, (0, 0), sigmaX=20, sigmaY=20)
    return bg


def fit_foreground(src_img: np.ndarray, width: int, height: int) -> np.ndarray:
    """将原图按比例缩放，确保主体完整显示。"""
    ih, iw = src_img.shape[:2]
    scale = min(width / iw, height / ih) * 0.8
    nw, nh = int(iw * scale), int(ih * scale)
    return cv2.resize(src_img, (nw, nh), interpolation=cv2.INTER_AREA)


def style_params(style: str, rng: random.Random) -> dict[str, float]:
    if style == "random":
        style = rng.choice(("hiphop", "swing", "robot"))

    if style == "hiphop":
        return {"sx": 28, "sy": 20, "rot": 12, "pulse": 0.08, "freq": 1.4}
    if style == "swing":
        return {"sx": 20, "sy": 36, "rot": 8, "pulse": 0.06, "freq": 1.0}
    if style == "robot":
        return {"sx": 16, "sy": 16, "rot": 5, "pulse": 0.03, "freq": 2.1}

    raise ValueError(f"未知舞蹈风格: {style}")


def motion_at_t(t: float, params: dict[str, float], rng: random.Random) -> tuple[float, float, float, float]:
    """返回位移 dx/dy、旋转角度、缩放比例。"""
    freq = params["freq"]

    if freq > 2.0:
        step = 0.12
        t = round(t / step) * step

    jitter = rng.uniform(-0.6, 0.6)
    dx = params["sx"] * math.sin(2 * math.pi * freq * t + jitter)
    dy = params["sy"] * math.cos(2 * math.pi * (freq * 0.6) * t + jitter)
    rot = params["rot"] * math.sin(2 * math.pi * (freq * 0.7) * t)
    scale = 1.0 + params["pulse"] * math.sin(2 * math.pi * (freq * 0.8) * t)
    return dx, dy, rot, scale


def render_frame(bg: np.ndarray, fg: np.ndarray, t: float, params: dict[str, float], rng: random.Random) -> np.ndarray:
    height, width = bg.shape[:2]
    fh, fw = fg.shape[:2]

    dx, dy, rot, scale = motion_at_t(t, params, rng)
    sw, sh = max(16, int(fw * scale)), max(16, int(fh * scale))
    scaled = cv2.resize(fg, (sw, sh), interpolation=cv2.INTER_LINEAR)

    mat = cv2.getRotationMatrix2D((sw / 2, sh / 2), rot, 1.0)
    rotated = cv2.warpAffine(
        scaled,
        mat,
        (sw, sh),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT,
    )

    cx = width // 2 + int(dx)
    cy = height // 2 + int(dy)
    x0 = cx - sw // 2
    y0 = cy - sh // 2
    x1 = x0 + sw
    y1 = y0 + sh

    frame = bg.copy()

    rx0 = max(0, x0)
    ry0 = max(0, y0)
    rx1 = min(width, x1)
    ry1 = min(height, y1)
    if rx0 >= rx1 or ry0 >= ry1:
        return frame

    sx0 = rx0 - x0
    sy0 = ry0 - y0
    sx1 = sx0 + (rx1 - rx0)
    sy1 = sy0 + (ry1 - ry0)

    frame[ry0:ry1, rx0:rx1] = rotated[sy0:sy1, sx0:sx1]

    return frame


def main() -> None:
    args = parse_args()

    if args.seed is None:
        args.seed = random.randint(1, 10**9)
    rng = random.Random(args.seed)

    if not args.photo.exists():
        raise FileNotFoundError(f"输入照片不存在: {args.photo}")

    width, height = parse_size(args.size)
    total_frames = int(args.duration * args.fps)
    if total_frames <= 0:
        raise ValueError("duration * fps 必须大于 0")

    src = cv2.imread(str(args.photo))
    if src is None:
        raise RuntimeError("无法读取输入照片，请检查格式")

    bg = build_background(src, width, height)
    fg = fit_foreground(src, width, height)
    params = style_params(args.style, rng)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(args.output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        float(args.fps),
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"无法写出视频到: {args.output}")

    print(f"开始生成，随机种子: {args.seed}")
    for i in range(total_frames):
        t = i / args.fps
        frame = render_frame(bg, fg, t, params, rng)
        writer.write(frame)
        if i % args.fps == 0:
            print(f"进度: {i}/{total_frames} 帧")

    writer.release()
    print(f"完成！输出文件: {args.output}")


if __name__ == "__main__":
    main()
