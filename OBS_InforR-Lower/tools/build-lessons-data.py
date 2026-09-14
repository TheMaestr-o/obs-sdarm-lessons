#!/usr/bin/env python3
"""
Builds a single lessons-data.json bundling every lesson/question, in every
available language AND every available quarter, for the panel's
Lesson/Language/Quarter picker.

Reads the same source the earlier extract-questions.py script reads from
(/Users/ohnedan/Developer/sbl/data/<lang>/<lang>-<year>-<quarter>.json), but
instead of one hardcoded year/quarter, SCANS each language's folder for every
"<lang>-YYYY-Q.json" file that actually exists there. This means: to add a
new quarter later, just drop its per-language JSON files into
/Users/ohnedan/Developer/sbl/data/<lang>/ (matching the existing naming) and
rerun this script -- no code change needed here.

Usage:
    python3 build-lessons-data.py

Output: ../lessons-data.json (relative to this script), served by the same
static file server as panel.html/result.html so the panel can `fetch()` it.
"""
import json
import re
import sys
from pathlib import Path

SOURCE_DIR = Path("/Users/ohnedan/Developer/sbl/data")
OUT_PATH = Path(__file__).resolve().parent.parent / "lessons-data.json"
QUARTER_FILE_RE = re.compile(r"^([a-z]{2})-(\d{4})-(\d)\.json$")


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


def find_quarter_files(lang: str):
    """Every "<lang>-YYYY-Q.json" file actually present in this language's
    folder, as (year, quarter, path) tuples, newest first."""
    lang_dir = SOURCE_DIR / lang
    if not lang_dir.is_dir():
        return []
    found = []
    for path in lang_dir.iterdir():
        m = QUARTER_FILE_RE.match(path.name)
        if m and m.group(1) == lang:
            found.append((int(m.group(2)), int(m.group(3)), path))
    return sorted(found, key=lambda t: (t[0], t[1]), reverse=True)


def build_lesson_entries(data: dict, letters: list[str]):
    lessons = []
    for les in data.get("lessons", []):
        questions = []
        for day in les.get("dailyLessons", []):
            # Each day carries its own subheading (e.g. "1. БОГ ЕСТЬ ЛЮБОВЬ",
            # "2. МИССИЯ ИИСУСА"), and the letter sequence RESTARTS at "a" for
            # every day -- the source data itself does this (see the raw text
            # embedded in each question, which the earlier extract-questions.py
            # script and this one both strip off). A single running counter
            # across the whole lesson produces wrong letters for every day
            # after the first, since it never resets: day 3's real "a., b."
            # would show up mislabeled as "e., f." because days 1-2 already
            # used up 4 letters.
            day_title = day.get("sectionTitle", "").strip()
            day_index = 0
            for sub in day.get("subsections", []):
                q = first_question_text(sub)
                if q:
                    letter = letters[day_index] if day_index < len(letters) else str(day_index + 1)
                    questions.append({"letter": letter, "sectionTitle": day_title, "text": q})
                    day_index += 1

        lessons.append({
            "no": les.get("no"),
            "title": les.get("title", "").strip(),
            "questions": questions,
        })
    return lessons


def main():
    languages = sorted(p.name for p in SOURCE_DIR.iterdir() if p.is_dir())

    # Letter labels per lesson, regenerated per-language so e.g. Cyrillic
    # languages get а/б/в... and Latin-script languages get a/b/c... -- same
    # rule the earlier extract-questions.py used.
    CYRILLIC_LETTERS = list("абвгдежзиклмноп")
    LATIN_LETTERS = list("abcdefghijklmnop")

    def letters_for(lang: str):
        return CYRILLIC_LETTERS if lang in ("ru", "bg", "uk", "sr", "mk") else LATIN_LETTERS

    # Keyed by "YYYY-Q" so the panel can offer a Quarter dropdown even though
    # only one quarter exists today -- adding a second one later is just
    # dropping its files in and rerunning this script, no code change here.
    quarters = {}

    for lang in languages:
        letters = letters_for(lang)
        for year, quarter, path in find_quarter_files(lang):
            key = f"{year}-{quarter}"
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            quarters.setdefault(key, {"year": year, "quarter": quarter, "languages": {}})
            quarters[key]["languages"][lang] = {
                "quarterTitle": data.get("title", ""),
                "lessons": build_lesson_entries(data, letters),
            }

    if not quarters:
        print("No quarter files found under", SOURCE_DIR, file=sys.stderr)
        sys.exit(1)

    for key, q in sorted(quarters.items()):
        print(f"{key}: {len(q['languages'])} languages")

    bundle = {"quarters": quarters}
    OUT_PATH.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
