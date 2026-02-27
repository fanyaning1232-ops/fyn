#!/usr/bin/env python3
"""小红书一键排版工具.

功能:
- 自动清洗文本空白
- 自动分段和加小标题
- 一键添加 emoji 风格标签
- 自动生成结尾互动引导与话题标签
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

EMOJI_STYLES: dict[str, list[str]] = {
    "none": ["", "", ""],
    "soft": ["✨", "🌿", "📝"],
    "cute": ["💖", "🐻", "🎀"],
    "clean": ["✅", "📌", "🧠"],
}

SECTION_TITLES = [
    "先说重点",
    "展开聊聊",
    "实操建议",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="小红书文案一键排版")
    parser.add_argument("--text", help="直接传入文案内容")
    parser.add_argument("--input", type=Path, help="从文件读取文案")
    parser.add_argument("--output", type=Path, help="输出到文件，不填则打印到终端")
    parser.add_argument("--title", default="", help="可选标题，会放在文案顶部")
    parser.add_argument("--emoji-style", choices=tuple(EMOJI_STYLES), default="soft", help="emoji 风格")
    parser.add_argument("--hashtags", default="", help="额外话题标签，空格分隔，如: 护肤 通勤穿搭")
    parser.add_argument("--cta", default="你还想看哪类内容？欢迎评论区告诉我～", help="结尾互动引导")
    return parser.parse_args()


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"([。！？!?；;])", r"\1\n", text)
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    return parts


def split_to_sections(items: list[str], section_count: int = 3) -> list[list[str]]:
    if not items:
        return [[] for _ in range(section_count)]

    chunk = (len(items) + section_count - 1) // section_count
    sections: list[list[str]] = []
    for i in range(section_count):
        sections.append(items[i * chunk : (i + 1) * chunk])
    while len(sections) < section_count:
        sections.append([])
    return sections


def normalize_hashtags(raw_hashtags: str) -> list[str]:
    if not raw_hashtags.strip():
        return []
    tags = []
    for tag in raw_hashtags.split():
        token = tag.strip().lstrip("#")
        if token:
            tags.append(f"#{token}")
    return tags


def format_post(
    text: str,
    title: str,
    emoji_style: str,
    hashtags: str,
    cta: str,
) -> str:
    cleaned = normalize_text(text)
    sentence_items = split_sentences(cleaned)
    sections = split_to_sections(sentence_items)
    emojis = EMOJI_STYLES[emoji_style]

    blocks: list[str] = []

    if title.strip():
        blocks.append(f"{emojis[0]} {title.strip()} {emojis[0]}".strip())

    for i, section in enumerate(sections):
        if not section:
            continue
        head = f"{emojis[i % len(emojis)]} {SECTION_TITLES[i]}"
        body = "\n".join(f"- {line}" for line in section)
        blocks.append(f"{head}\n{body}")

    if cta.strip():
        blocks.append(f"\n{emojis[1]} {cta.strip()}")

    default_tags = ["#小红书文案", "#一键排版", "#内容创作"]
    all_tags = default_tags + normalize_hashtags(hashtags)
    blocks.append(" ".join(all_tags))

    return "\n\n".join(blocks).strip() + "\n"


def read_source_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.input:
        if not args.input.exists():
            raise FileNotFoundError(f"输入文件不存在: {args.input}")
        return args.input.read_text(encoding="utf-8")
    raise ValueError("请提供 --text 或 --input")


def main() -> None:
    args = parse_args()
    source = read_source_text(args)
    result = format_post(source, args.title, args.emoji_style, args.hashtags, args.cta)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
        print(f"排版完成，已输出到: {args.output}")
        return

    print(result, end="")


if __name__ == "__main__":
    main()
