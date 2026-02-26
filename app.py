#!/usr/bin/env python3
"""Local video face swap demo.

Usage:
python app.py --source source.jpg --target target.mp4 --output output.mp4 --swap-model ./models/inswapper_128.onnx
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local video face swap tool")
    parser.add_argument("--source", required=True, type=Path, help="Source face image")
    parser.add_argument("--target", required=True, type=Path, help="Target video path")
    parser.add_argument("--output", required=True, type=Path, help="Output video path")
    parser.add_argument("--swap-model", required=True, type=Path, help="Path to inswapper_128.onnx")
    parser.add_argument("--det-size", type=int, default=320, help="Face detection size, e.g. 320/640")
    parser.add_argument("--ctx-id", type=int, default=-1, help="Execution context: -1 CPU, 0 GPU")
    return parser.parse_args()


def pick_largest_face(faces: list) -> object:
    if not faces:
        raise RuntimeError("No face detected.")
    return max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))


def main() -> None:
    args = parse_args()

    if not args.source.exists():
        raise FileNotFoundError(f"Source image not found: {args.source}")
    if not args.target.exists():
        raise FileNotFoundError(f"Target video not found: {args.target}")
    if not args.swap_model.exists():
        raise FileNotFoundError(f"Swap model not found: {args.swap_model}")

    # Face analyzer
    face_app = FaceAnalysis(name="buffalo_l")
    face_app.prepare(ctx_id=args.ctx_id, det_size=(args.det_size, args.det_size))

    # Face swapper
    swapper = get_model(str(args.swap_model), download=False)

    source_img = cv2.imread(str(args.source))
    if source_img is None:
        raise RuntimeError("Cannot read source image.")

    source_faces = face_app.get(source_img)
    source_face = pick_largest_face(source_faces)

    cap = cv2.VideoCapture(str(args.target))
    if not cap.isOpened():
        raise RuntimeError("Cannot open target video.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(args.output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        target_faces = face_app.get(frame)
        swapped = frame
        for face in target_faces:
            swapped = swapper.get(swapped, face, source_face, paste_back=True)

        writer.write(swapped)
        frame_idx += 1
        if frame_idx % 30 == 0:
            print(f"Processed {frame_idx} frames...")

    cap.release()
    writer.release()
    print(f"Done. Output saved to: {args.output}")


if __name__ == "__main__":
    main()
