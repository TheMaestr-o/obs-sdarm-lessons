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


# The end of a question: its question mark, and any quote or bracket closing after it.
QUESTION_END_RE = re.compile(r"[?？؟][»”\"’'）)」』]*")


def split_trailing_citation(text: str) -> tuple[str, str]:
    """("...draw men to Himself?", "Exodusi 34:6, 7") from a question that still
    has the start of its reference stuck to it.

    Where a source did not mark its first citation up as an entry of its own,
    that citation is simply the tail of the question's text -- "...? Exodusi
    34:6, 7;" -- and only the citations after it arrive separately. On air that
    showed as a reference half in white and half in gold. What follows the last
    question mark is moved across when it reads as a citation:

      it has a digit in it             "Псалтирь 138:23, 24;"   a whole citation
      or is a word or two, no digit    "До"                      the head of one --
                                       Ukrainian "До колосян 1:14", split mid-name

    and left alone when it ends in a question mark itself, because then it is
    not a citation but a second question: "...? What should they do?"."""
    # Japanese prints its reference in brackets -- "...を挙げなさい（ヨハネ 14:1–3）。" --
    # and the source leaves the opening one on the end of the question while the
    # closing one travels with the reference (and is dropped there). On air the
    # reference is set apart by its colour, so the bracket would open and never close.
    text = re.sub(r"\s*[（(]\s*$", "", text)
    ends = list(QUESTION_END_RE.finditer(text))
    if not ends:
        return text, ""
    cut = ends[-1].end()
    tail = text[cut:].strip()
    if not tail:
        return text, ""
    # Nothing but punctuation, or a bare number -- a page number of the printed
    # lesson. It belongs to neither the question nor the reference.
    if not any(c.isalpha() for c in tail) and ":" not in tail and "：" not in tail:
        return text[:cut].strip(), ""
    # A word or two only counts as the head of a citation while it is left open:
    # "До" is one, "Explain." is an instruction and stays with the question.
    is_citation = any(c.isdigit() for c in tail) or (
        len(tail.split()) <= 2 and tail[-1] not in ".!。！")
    if not is_citation:
        return text, ""
    return text[:cut].strip(), tail.strip(" .;:,；：。，、")


# How an entry of a reference ended in print decides how the next one joins it.
REF_CLOSERS = " .;:,；：。，、"
REF_SOFT = ",，、"      # the list carries on: "Romanos 7:12," then "14"
REF_DASHES = {"-", "–", "—"}
REF_QUOTES = "«„“\"‘'「『"
REF_OPENERS = "（(［[「【"
REF_BARE_NUMBER = re.compile(r"^[\d\s,.:;\-–—]+$")
ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"))


def question_reference(sub: dict, sep: str = "; ", lead: str = "") -> str:
    """The scripture reference printed after a question -- "1. Korinther 13, 12."

    In the source, `q` is a list: the question itself first, then the reference
    in pieces -- one entry per citation (each carrying an `sOsis` id) and,
    between them, whatever the lesson printed there. Almost always that is a
    space. The rest is what this function is for:

      "Luc 12:32;"  "1"  " Peter 4:13."     a book's number, split off its name
      "Romanos 7:12,"  "14"  " e "  "Romanos 7:24."    a verse, and a word, between
      "ヨハネ 16:"  "20"                     a verse split off its chapter
      "Jonah 4:2"  "(last part);"           a note on the citation before it
      "Jón 4:2."  "ur; "                    the same note, abbreviated, no brackets
      "От Иоанна 1:51."  "20"               the printed lesson's page number
      "«19Итак, покайтесь...»"              the verse itself, quoted in full

    Joining every entry with "; " -- what this did at first -- put "1; Peter
    4:13" and "От Иоанна 1:51; 20" on air. Each piece now goes where print had
    it, the page numbers and quoted verses go nowhere, and the trailing full
    stop is dropped because on air the reference ends the line, not a sentence."""
    raw = [x.get("text", "") for x in sub.get("q", [])[1:]]
    # `lead` is what split_trailing_citation() took off the end of the question:
    # a citation of its own if it has a digit in it, otherwise the opening word of
    # the first citation -- which is exactly what an unclosed word entry is below.
    if lead:
        raw.insert(0, lead + ";" if any(c.isdigit() for c in lead) else lead)
    # Zero-width spaces come along from the page layout -- inside Thai book names,
    # and once as an entry with nothing else in it. A reference never wraps, so
    # they do nothing here except stop two equal citations comparing equal.
    raw = [r.translate(ZERO_WIDTH) for r in raw]
    # Out go the blanks, the verses quoted in full (they open with a quotation
    # mark), and entries that are brackets and nothing else -- the Japanese
    # source closes every reference with a "）。" of its own.
    raw = [r for r in raw if r.strip()
           and r.strip()[0] not in REF_QUOTES
           and r.strip().strip(REF_CLOSERS + "（）()[]［］「」【】")]

    parts: list[str] = []
    prefix = ""       # words waiting for the citation they open: "e", "До", "1"
    tight = False     # a dash is waiting: the next citation closes a range
    prev_end = ""     # the character the entry before ended on, in print
    for i, r in enumerate(raw):
        t = r.strip().strip(REF_CLOSERS)
        end = r.rstrip()[-1:]
        closed = end in REF_CLOSERS or i == len(raw) - 1

        if t in REF_DASHES:
            tight = True
            continue

        # "(last part)" -- a note goes back onto the citation it is about.
        if parts and t[0] in REF_OPENERS:
            parts[-1] += ("" if t[0] in "（［「【" else " ") + t
            prev_end = end
            continue

        if REF_BARE_NUMBER.match(t):
            if parts and prev_end in REF_SOFT:          # "...7:12," "14"
                parts[-1] += ("，" if prev_end in "，、" else ", ") + t
                prev_end = end
            elif parts and prev_end == ":":             # "...16:" "20"
                parts[-1] += ":" + t
                prev_end = end
            elif t in {"1", "2", "3", "4"} and not closed:   # "1" " Peter 4:13"
                prefix = f"{prefix} {t}".strip()
            elif not parts and ":" in t:                # a lead with no book name: "3:8–10"
                parts.append(t)
                prev_end = end
            # Anything else is a page number of the printed lesson, caught up in
            # the text where the page happened to break. It is not shown.
            continue

        if not any(c.isdigit() for c in t):             # a word, not a citation
            if closed and parts:
                # It closes what it follows: Hungarian "ur" (utolsó rész, "last
                # part"). Where the citation itself ended on an abbreviation's
                # dot -- "2Kor 5:14, 15 e." "r" -- the two are one abbreviation.
                one_word = prev_end == "." and parts[-1][-1:].isalpha()
                parts[-1] += ("." if one_word else " ") + t
                prev_end = end
            elif not closed:
                prefix = f"{prefix} {t}".strip()
            continue

        joined_by_word = bool(prefix)
        if prefix:
            t = f"{prefix} {t}"
        # A citation after a comma still gets the full separator. Print had "Romans
        # 7:12, 14, 24"; the source spells each verse out as a citation of its own,
        # and "Romans 7:12, Romans 7:14" reads as one run-on where "; " keeps them apart.
        if tight and parts:
            # "Псалом 51:12" "-" "Псалми 51:15" is print's "Псалом 51:12-15".
            a = re.search(r"(\d+)[:：]\d+$", parts[-1])
            z = re.search(r"(\d+)[:：](\d+)$", t)
            parts[-1] += "-" + (z.group(2) if a and z and a.group(1) == z.group(1) else t)
        elif parts and joined_by_word and prev_end not in REF_CLOSERS:
            parts[-1] += " " + t                         # "Daniel 1:8" "e" "Daniel 1:15"
        else:
            parts.append(t)
        prefix, tight, prev_end = "", False, end
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
                    # A citation still attached to the question's text joins the rest
                    # of its reference -- but only when that leaves a reference short
                    # enough to show; otherwise the question keeps its text as it was.
                    trimmed, lead = split_trailing_citation(q)
                    ref = question_reference(sub, ref_sep, lead)
                    if lead and not ref:
                        trimmed, ref = q, question_reference(sub, ref_sep)
                    questions.append({
                        "letter": letter,
                        "sectionTitle": day_title,
                        "text": trimmed,
                        "ref": ref,
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
