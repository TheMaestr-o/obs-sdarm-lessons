#!/usr/bin/env python3
"""
Builds the three fonts Open Sans cannot stand in for: Japanese, Chinese, Thai.

Open Sans has Latin, Cyrillic and Greek. Nineteen of the twenty-two lesson
languages live inside that; ja, zh and th do not have a single glyph in it, so
the overlay was drawing them in whatever the machine happened to have -- fine on
the Mac this was written on, and exactly the "looks right here because it is
installed here" failure fonts/README.md warns about. A full CJK font is eight
to ten megabytes, so these are cut down instead:

  glyphs  the characters the lesson data actually uses, plus the whole of the
          small closed sets around them (all kana, CJK punctuation, full-width
          forms, the Thai block) and the everyday core of each script -- JIS
          level 1 kanji, GB 2312 level 1 hanzi -- so that a new quarter's text
          almost always lands on glyphs that are already here;
  weights the variable `wght` axis is narrowed to 600-700, the only two weights
          the overlay sets text in.

Run it after build-lessons-data.py whenever a new quarter arrives; that script
tells you when the lesson text has grown a character these files do not have.

Needs the network ONCE, to fetch the upstream Noto files into tools/.font-cache
(git-ignored). The overlay itself never needs it.

Usage:
    python3 build-cjk-fonts.py
"""
import json
import sys
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
DATA_PATHS = [HERE.parent / "lessons-data.json", HERE.parent / "lessons-data.sample.json"]
OUT_DIR = HERE.parent / "native" / "fonts"
CACHE = HERE / ".font-cache"
UPSTREAM = "https://github.com/google/fonts/raw/main/ofl"


def rows(codec: str, first_row: int, last_row: int) -> set[str]:
    """Every character in a run of rows of a 94x94 national character set."""
    out = set()
    for row in range(first_row, last_row + 1):
        for cell in range(1, 95):
            try:
                out.add(bytes([row + 0xA0, cell + 0xA0]).decode(codec))
            except UnicodeDecodeError:
                pass
    return out


def block(first: int, last: int) -> set[str]:
    return {chr(c) for c in range(first, last + 1)}


SHARED = block(0x3000, 0x303F) | block(0xFF00, 0xFFEF)   # CJK punctuation, full-width forms

FONTS = [
    {
        "langs": ["ja"],
        "source": "notosansjp/NotoSansJP%5Bwght%5D.ttf",
        "licence": "notosansjp/OFL.txt",
        "out": "NotoSansJP-Subset.woff2",
        "licence_out": "NotoSansJP-OFL.txt",
        # all kana, and JIS X 0208 level 1 -- the 2,965 kanji of everyday use
        "always": SHARED | block(0x3040, 0x30FF) | rows("euc_jp", 16, 47),
        "pin": {},
    },
    {
        "langs": ["zh"],
        "source": "notosanssc/NotoSansSC%5Bwght%5D.ttf",
        "licence": "notosanssc/OFL.txt",
        "out": "NotoSansSC-Subset.woff2",
        "licence_out": "NotoSansSC-OFL.txt",
        # GB 2312 level 1 -- the 3,755 most frequent simplified characters
        "always": SHARED | rows("gb2312", 16, 55),
        "pin": {},
    },
    {
        "langs": ["th"],
        "source": "notosansthai/NotoSansThai%5Bwdth%2Cwght%5D.ttf",
        "licence": "notosansthai/OFL.txt",
        "out": "NotoSansThai-Subset.woff2",
        "licence_out": "NotoSansThai-OFL.txt",
        "always": block(0x0E00, 0x0E7F),
        "pin": {"wdth": 100},
    },
]


def fetch(relative: str) -> Path:
    CACHE.mkdir(exist_ok=True)
    target = CACHE / relative.replace("/", "__").replace("%5B", "[").replace("%5D", "]").replace("%2C", ",")
    if not target.exists():
        print(f"  fetching {relative} ...")
        urllib.request.urlretrieve(f"{UPSTREAM}/{relative}", target)
    return target


def used_characters(langs: list[str]) -> set[str]:
    """Every character of every string the overlay could be handed for these
    languages -- headings in capitals too, since the overlay capitalises them."""
    chars: set[str] = set()
    for path in DATA_PATHS:
        if not path.exists():
            continue
        bundle = json.loads(path.read_text(encoding="utf-8"))
        for quarter in bundle.get("quarters", {}).values():
            for lang in langs:
                for lesson in quarter.get("languages", {}).get(lang, {}).get("lessons", []):
                    texts = [lesson.get(k, "") for k in ("title", "header", "introduction", "introductionRef")]
                    for q in lesson.get("questions", []):
                        texts += [q.get("text", ""), q.get("ref", ""), q.get("letter", ""), q.get("sectionTitle", "")]
                    for t in texts:
                        chars.update(t)
                        chars.update(t.upper())
    return {c for c in chars if not c.isspace()}


def main() -> None:
    for spec in FONTS:
        print(spec["out"])
        font = TTFont(fetch(spec["source"]))
        cmap = font.getBestCmap()

        used = used_characters(spec["langs"])
        wanted = {c for c in (used | spec["always"]) if ord(c) in cmap}
        # Anything the lessons use that even the full upstream font lacks is
        # worth saying out loud; ASCII and the like belong to Open Sans anyway.
        absent = sorted(c for c in used if ord(c) not in cmap and ord(c) > 0x2E7F)
        if absent:
            print(f"  not in the upstream font either: {''.join(absent[:40])}")

        # Glyphs first, weights second: narrowing the axis walks every glyph's
        # variation data, which is a great deal less work on three thousand
        # glyphs than on sixteen thousand -- and the instancer trips over
        # glyphs in the full font that the subset never keeps.
        options = subset.Options()
        options.layout_features = ["*"]     # Thai needs its mark positioning; CJK its width forms
        options.name_IDs = ["*"]
        options.notdef_outline = True
        options.drop_tables += ["DSIG"]
        cutter = subset.Subsetter(options)
        cutter.populate(unicodes=[ord(c) for c in wanted])
        cutter.subset(font)

        font = instancer.instantiateVariableFont(font, {"wght": (600, 700), **spec["pin"]})

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / spec["out"]
        font.flavor = "woff2"
        font.save(out)
        (OUT_DIR / spec["licence_out"]).write_bytes(fetch(spec["licence"]).read_bytes())
        print(f"  {len(used)} characters in the lessons, {len(wanted)} in the file, {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    try:
        main()
    except OSError as err:     # no network on the first run, mostly
        sys.exit(f"build-cjk-fonts: {err}")
