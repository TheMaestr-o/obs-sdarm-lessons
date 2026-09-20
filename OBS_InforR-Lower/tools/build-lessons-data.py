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
# Longest reference the overlay will carry after a question -- about a third of
# a line at the question's size, enough for three or four plain citations.
REF_MAX_CHARS = 72


# One letter of any script, then a full stop: "a. ", "а.", "ข. ", "A." -- with or
# without the space, since the sources are not consistent about it.
LETTER_MARKER_RE = re.compile(r"^\s*([^\W\d_])\.\s*")


def split_letter_marker(text: str) -> tuple[str, str]:
    """("a", "What evidence...") from "a. What evidence...".

    The marker is split off because the panel prints the letter itself, and a
    question that kept its own would show it twice. It is RETURNED, not thrown
    away, because the lesson's own letter is the right one to print and cannot
    be reconstructed from an alphabet: Serbian counts а, б, ц where Russian
    counts а, б, в; Portuguese prints capitals; Thai uses ก, ข, ค. The pattern
    used to know Latin and Cyrillic only, so Thai questions went out as
    "b. ข. ..." -- both letters."""
    text = text.strip()
    m = LETTER_MARKER_RE.match(text)
    return (m.group(1), text[m.end():]) if m else ("", text)


def first_question(sub: dict) -> tuple[str, str] | None:
    """(letter marker or "", question text) for a subsection, or None if it has
    no question at all."""
    parts = [x.get("text", "").strip() for x in sub.get("q", []) if x.get("text", "").strip()]
    if not parts:
        return None
    return split_letter_marker(parts[0])


def question_reference(sub: dict, sep: str = "; ") -> str:
    """The scripture reference printed after a question -- "1. Korinther 13, 12."

    In the source, `q` is a list: the question itself first, then one entry per
    reference, each carrying an `sOsis` id. Only the first entry used to be
    read, so the overlay had nothing to set in the gold italic the design
    gives a reference. Joined as the lesson prints them; the trailing full
    stop is dropped because on air the reference ends the line, not a
    sentence."""
    # Each entry arrives with whatever closed it in print -- "Exodus 34:6, 7;",
    # "Jonah 4:2.", "出34：6，7；" -- so the closers come off before the entries are
    # joined again; left on, two of them meet in the middle as ";;".
    refs = [x.get("text", "").strip().strip(" .;:,；：。，、") for x in sub.get("q", [])[1:] if x.get("text", "").strip()]
    # An entry that opens with a quotation mark is the verse quoted out in full,
    # not a citation of it -- "«19Итак, покайтесь...»". It has no place on a lower
    # third, and leaving it in only to cut it out again leaves its punctuation behind.
    refs = [r for r in refs if r and r[0] not in "«„“\"‘'「『"]
    # Some sources (Japanese most of all) split a citation's bracketed note into
    # an entry of its own -- "ヨナ書 4:2", "（下句）" -- and occasionally leave a lone
    # bracket behind as a third. The note goes back onto the citation it belongs
    # to; an entry with nothing in it but brackets is not a citation at all.
    parts: list[str] = []
    for r in refs:
        if not r.strip("（）()[]［］「」【】 "):
            continue
        if parts and r[0] in "（(［[「【":
            parts[-1] += ("" if r[0] in "（［「【" else " ") + r
        else:
            parts.append(r)
    ref = sep.join(parts)
    # A few sources quote the verse inside the reference ("Деяния 3:19, 20: «19Итак,
    # покайтесь...»"). On a lower third that is a third line of small print, so the
    # quotation goes and the citation stays. Anything still too long to sit at the
    # end of a line is dropped whole rather than shown cut off mid-citation.
    if len(ref) > REF_MAX_CHARS:
        ref = re.sub(r"\s*(\([^)]*\))?\s*:?\s*[«„“\"][^»“”\"]*[»“”\"]", "", ref).strip(" ;")
    return ref if len(ref) <= REF_MAX_CHARS else ""


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


def build_lesson_entries(data: dict, letters: list[str], ref_sep: str = "; "):
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
                found = first_question(sub)
                if found and found[1]:
                    marker, q = found
                    # The lesson's own letter where it printed one; the positional
                    # alphabet only for a source that left it out.
                    fallback = letters[day_index] if day_index < len(letters) else str(day_index + 1)
                    letter = marker or fallback
                    questions.append({
                        "letter": letter,
                        "sectionTitle": day_title,
                        "text": q,
                        "ref": question_reference(sub, ref_sep),
                    })
                    day_index += 1

        # Extract introduction from keyText.text (opening verse/summary), and the
        # reference that goes with it -- shown after the verse the same way a
        # question's reference is. For a source that carries only the label and
        # no verse (Ukrainian, this quarter) the reference is all there is to show.
        introduction = ""
        introduction_ref = ""
        key_text = les.get("keyText")
        if isinstance(key_text, dict):
            introduction = key_text.get("text", "").strip()
            ref = key_text.get("ref")
            introduction_ref = (ref.get("text", "") if isinstance(ref, dict) else ref or "").strip().rstrip(". ")
        elif isinstance(key_text, str):
            introduction = key_text.strip()

        lessons.append({
            "no": les.get("no"),
            # The lesson's own "Lesson N" line, already in the lesson's language
            # and already numbered -- "УРОК 1", "1. Lektion", "Lección 1". Worth
            # carrying rather than composing in the panel: the word differs per
            # language and so does where the number goes, and the source has it
            # right for all 22.
            "header": les.get("header", "").strip(),
            "title": les.get("title", "").strip(),
            "introduction": introduction,
            "introductionRef": introduction_ref,
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
                # Chinese separates its citations with its own full-width
                # semicolon; everything else here uses the ASCII one.
                "lessons": build_lesson_entries(data, letters, "；" if lang == "zh" else "; "),
            }

    if not quarters:
        print("No quarter files found under", SOURCE_DIR, file=sys.stderr)
        sys.exit(1)

    for key, q in sorted(quarters.items()):
        print(f"{key}: {len(q['languages'])} languages")

    bundle = {"quarters": quarters}
    OUT_PATH.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")

    check_font_coverage(quarters)


def check_font_coverage(quarters: dict) -> None:
    """Says so when the lesson text contains a character none of the bundled
    fonts can draw. The overlay runs offline, so such a character comes out in
    whatever the streaming machine happens to have installed -- or as a box.
    A new quarter is the one moment that can change, and this is the script
    that runs then. Needs fontTools; without it the check is skipped, not failed."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print("(fontTools not installed -- skipped the font coverage check)")
        return

    fonts_dir = OUT_PATH.parent / "native" / "fonts"
    covered: set[int] = set()
    for path in sorted(fonts_dir.glob("*.woff2")):
        covered |= set(TTFont(path).getBestCmap())

    missing: dict[str, set[str]] = {}
    for q in quarters.values():
        for lang, data in q["languages"].items():
            for lesson in data["lessons"]:
                texts = [lesson["title"], lesson["header"], lesson["introduction"], lesson["introductionRef"]]
                for question in lesson["questions"]:
                    texts += [question["text"], question["ref"], question["letter"],
                              question["sectionTitle"], question["sectionTitle"].upper()]
                for t in texts:
                    gaps = {c for c in t if not c.isspace() and ord(c) not in covered}
                    if gaps:
                        missing.setdefault(lang, set()).update(gaps)

    if not missing:
        print("Fonts: every character in every language is covered by the bundled files.")
        return
    print("\nFonts: some characters are NOT in the bundled fonts:")
    for lang, chars in sorted(missing.items()):
        sample = "".join(sorted(chars))[:40]
        print(f"  {lang}: {len(chars)} -- {sample}")
    print("  For ja / zh / th run tools/build-cjk-fonts.py, which re-cuts those fonts from this data.")


if __name__ == "__main__":
    main()
