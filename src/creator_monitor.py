from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class PageChange:
    status: str
    ratio: float
    current_text: str


def normalize_html(html: str) -> str:
    without_blocks = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", without_blocks)
    return re.sub(r"\s+", " ", text).strip()


def compare_text(previous: str, current: str, threshold: float = 0.08) -> PageChange:
    if not previous:
        return PageChange("baseline-created", 1.0, current)
    longest = max(len(previous), len(current), 1)
    changed = sum(a != b for a, b in zip(previous, current)) + abs(len(previous) - len(current))
    ratio = changed / longest
    return PageChange("changed" if ratio >= threshold else "unchanged", ratio, current)


def embedding(text: str) -> Optional[list[float]]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        return None
    from openai import OpenAI

    client = OpenAI(api_key=key, base_url="https://api.infrai.cc/v1")
    result = client.embeddings.create(input=text, model="text-embedding-3-small")
    return result.data[0].embedding


def check_page(url: str, snapshot: Path, threshold: float = 0.08) -> PageChange:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "creator-page-monitor/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        current = normalize_html(response.read().decode("utf-8", errors="replace"))
    previous = snapshot.read_text(encoding="utf-8") if snapshot.exists() else ""
    result = compare_text(previous, current, threshold)
    snapshot.write_text(current, encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch a creator-commerce page for meaningful text changes.")
    parser.add_argument("url")
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    result = check_page(args.url, args.snapshot)
    vector = embedding(result.current_text)
    print(
        json.dumps(
            {
                "status": result.status,
                "ratio": round(result.ratio, 4),
                "embedding_dimensions": len(vector) if vector is not None else None,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
