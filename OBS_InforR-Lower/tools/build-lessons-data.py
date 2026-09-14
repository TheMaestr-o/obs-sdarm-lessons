#!/usr/bin/env python3
"""
Builds a single lessons-data.json bundling every lesson/question, in every
available language, for the panel's Lesson/Language picker.

Reads the same source the earlier extract-questions.py script reads from
(/Users/ohnedan/Developer/sbl/data/<lang>/<lang>-<year>-<quarter>.json) but
walks ALL languages and ALL lessons in one pass instead of printing one
lesson's JS snippet at a time, and writes real JSON instead.

Usage:
    python3 build-lessons-data.py [--year YYYY] [--quarter Q]

Output: ../lessons-data.json (relative to this script), served by the same
static file server as panel.html/result.html so the panel can `fetch()` it.
"""
import json
import re
import sys
import argparse
from pathlib import Path

SOURCE_DIR = Path("/Users/ohnedan/Developer/sbl/data")
OUT_PATH = Path(__file__).resolve().parent.parent / "lessons-data.json"


def strip_leading_letter(text: str) -> str:
    """Drop an already-embedded letter marker ('a. ', 'а.') from the start of a
    question -- the panel adds its own letter/label, so a source string that
    already starts with one would otherwise show up doubled."""
    return re.sub(r"^\s*[a-zA-Zа-яА-ЯёЁ]\.\s*", "", text.strip())


def first_question_text(sub: dict) -> str | None:
    parts = [x.get("text", "").strip() for x in sub.get("q", []) if x.get("text", "").strip()]
    if not parts:
        return None
    return strip_leading_letter(parts[0])


def load_quarter(lang: str, year: int, quarter: int):
    path = SOURCE_DIR / lang / f"{lang}-{year}-{quarter}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--quarter", type=int, default=3)
    args = ap.parse_args()

    languages = sorted(p.name for p in SOURCE_DIR.iterdir() if p.is_dir())

    # Letter labels per lesson, regenerated per-language so e.g. Cyrillic
    # languages get а/б/в... and Latin-script languages get a/b/c... -- same
    # rule the earlier extract-questions.py used.
    CYRILLIC_LETTERS = list("абвгдежзиклмноп")
    LATIN_LETTERS = list("abcdefghijklmnop")

    def letters_for(lang: str):
        return CYRILLIC_LETTERS if lang in ("ru", "bg", "uk", "sr", "mk") else LATIN_LETTERS

    bundle = {"year": args.year, "quarter": args.quarter, "languages": {}}

    for lang in languages:
        data = load_quarter(lang, args.year, args.quarter)
        if not data:
            print(f"skip {lang}: no data file", file=sys.stderr)
            continue

        letters = letters_for(lang)
        lang_out = {"quarterTitle": data.get("title", ""), "lessons": []}

        for les in data.get("lessons", []):
            questions = []
            for day in les.get("dailyLessons", []):
                for sub in day.get("subsections", []):
                    q = first_question_text(sub)
                    if q:
                        letter = letters[len(questions)] if len(questions) < len(letters) else str(len(questions) + 1)
                        questions.append({"letter": letter, "text": q})

            lang_out["lessons"].append({
                "no": les.get("no"),
                "title": les.get("title", "").strip(),
                "questions": questions,
            })

        bundle["languages"][lang] = lang_out
        print(f"{lang}: {len(lang_out['lessons'])} lessons")

    OUT_PATH.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
