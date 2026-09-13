#!/usr/bin/env python3
"""
Извлекает реальные вопросы урока из /Users/ohnedan/Developer/sbl/data/<lang>/<lang>-YYYY-Q.json
и печатает готовый JS-массив (TOPIC + questions[]) для вставки в streaming-card.html.

Использование:
    python3 extract-questions.py [--lesson N] [--source-dir PATH] [--year YYYY] [--quarter Q]

По умолчанию берёт урок №1 из data/{ru,en,de}/{lang}-2026-3.json.
"""
import json
import re
import sys
import argparse
from pathlib import Path

LANGS = ["ru", "en", "de"]

def load_lesson(source_dir: Path, lang: str, year: int, quarter: int, lesson_no: int):
    path = source_dir / lang / f"{lang}-{year}-{quarter}.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for les in data["lessons"]:
        if les.get("no") == lesson_no:
            return data, les
    # fallback: index by position if "no" doesn't match 1:1
    return data, data["lessons"][lesson_no - 1]

def strip_leading_letter(text: str) -> str:
    """Убирает встроенную букву-маркер ('а. ', 'a.', 'б.Вопрос') из начала строки —
    в JS мы генерируем букву сами (LETTERS[lang][idx]), дублировать её в тексте не нужно."""
    return re.sub(r'^\s*[a-zа-яё]\.\s*', '', text.strip(), flags=re.IGNORECASE)

def first_question_text(sub: dict) -> str | None:
    parts = [x.get("text", "").strip() for x in sub.get("q", []) if x.get("text", "").strip()]
    if not parts:
        return None
    return strip_leading_letter(parts[0])

def js_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lesson", type=int, default=1, help="Номер урока в квартале (1-13)")
    ap.add_argument("--source-dir", default="/Users/ohnedan/Developer/sbl/data")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--quarter", type=int, default=3)
    args = ap.parse_args()

    source_dir = Path(args.source_dir)
    per_lang = {}
    topic_per_lang = {}

    for lang in LANGS:
        data, les = load_lesson(source_dir, lang, args.year, args.quarter, args.lesson)
        topic_per_lang[lang] = les.get("title", "").strip()
        days_out = []
        for day in les.get("dailyLessons", []):
            sec = day.get("sectionTitle", "").strip()
            for sub in day.get("subsections", []):
                q = first_question_text(sub)
                if q:
                    days_out.append(q)
        per_lang[lang] = days_out

    counts = {lang: len(v) for lang, v in per_lang.items()}
    if len(set(counts.values())) != 1:
        print(f"ВНИМАНИЕ: разное число вопросов по языкам: {counts}", file=sys.stderr)
        print("Печатаю по минимальному общему числу, остальное проверьте вручную.", file=sys.stderr)

    n = min(counts.values())

    print("// === Извлечено из /Users/ohnedan/Developer/sbl/data — урок №%d, %d Q%d ===" % (args.lesson, args.year, args.quarter))
    print("const TOPIC = {")
    for lang in LANGS:
        print(f"  {lang}: {js_string(topic_per_lang[lang])},")
    print("};")
    print()
    print("const questions = [")
    for i in range(n):
        row = ", ".join(f"{lang}: {js_string(per_lang[lang][i])}" for lang in LANGS)
        print(f"  {{ {row} }},")
    print("];")

if __name__ == "__main__":
    main()
