# Bundled fonts

Six font files, carried here on purpose rather than pulled from a CDN.

`overlay.css` asks for Open Sans and Arimo. The original lower-thirds CSS this project
started from (since deleted) got them with two
`@import url(https://fonts.googleapis.com/...)` lines at the top of the file. This
project has to work with no internet during a live broadcast, so that route is closed —
and simply naming the fonts without loading them (which is what `overlay.css` did until
now) means the overlay silently falls back to a generic sans-serif on any machine where
they don't happen to be installed. It looked right here only because Open Sans happened
to be installed on this machine.

So both fonts are bundled and loaded with `@font-face` from these files. Nothing is
fetched over the network at any point.

| File | Family | Axis |
|---|---|---|
| `OpenSans-Variable.woff2` | Open Sans | `wght` 300–800, `wdth` 75–100 |
| `OpenSans-Italic-Variable.woff2` | Open Sans, italic | `wght` 300–800, `wdth` 75–100 |
| `Arimo-Variable.woff2` | Arimo | `wght` 400–700 |

All are variable fonts, so one file per face covers every weight `overlay.css` uses
(Open Sans 600/700 upright and 600 italic, Arimo 400/700) instead of a separate static
file each. Converted to WOFF2 from the upstream TrueType originals — about 800 KB for the
three, against roughly 1.7 MB as `.ttf`.

## Japanese, Chinese, Thai

| File | Family | What is in it |
|---|---|---|
| `NotoSansJP-Subset.woff2` | Noto Sans JP | all kana, CJK punctuation, full-width forms, the 2,965 kanji of JIS level 1, plus every character the lessons use — about 3,470 glyphs, 870 KB |
| `NotoSansSC-Subset.woff2` | Noto Sans SC | CJK punctuation, full-width forms, the 3,755 hanzi of GB 2312 level 1, plus every character the lessons use — about 4,070 glyphs, 875 KB |
| `NotoSansThai-Subset.woff2` | Noto Sans Thai | the whole Thai block — 15 KB |

Open Sans has Latin, Cyrillic and Greek. Nineteen of the twenty-two lesson languages fit
inside that. Japanese, Chinese and Thai do not have one glyph in it, and until these files
existed the overlay drew them in whatever the machine had — which is the same failure
described at the top of this page, just harder to notice, because every Mac has *a* Japanese
font.

A complete CJK font is eight to ten megabytes, so these are cut down by
[`tools/build-cjk-fonts.py`](../../tools/build-cjk-fonts.py): to the characters that matter
(the ones the lesson data uses, padded out with each script's everyday core so that a new
quarter almost always lands on glyphs already here) and to the `wght` range 600–700, the
only two weights the overlay sets text in. `overlay.css` gives each a `unicode-range`, so
none of them is even fetched for a Latin or Cyrillic lesson.

Japanese and Chinese claim the *same* range. The two languages draw many of the same
characters differently, so which file answers is decided by the lesson's language — the
panel sends it, `overlay.html` puts it on the root as `lang`, and `:lang(zh)` reorders the
stack. None of the three scripts has an italic, so for them the scripture reference keeps
its colour and drops the slant rather than have the browser shear an upright.

`tools/build-lessons-data.py` checks every character of every language against all the
files here each time it runs, and says so if a new quarter has grown one that is missing.
Then run `tools/build-cjk-fonts.py` (needs the network once, to fetch the upstream Noto
files into a git-ignored cache; the overlay itself never does).

## The italic

The italic is its own file on purpose. The scripture reference that closes a question is
set in italic, and a browser asked for an italic it has not been given leans the upright
over by itself — a slanted roman, not an italic, and it looks like what it is. Open Sans
has a drawn italic; this is it, from the same upstream as the upright.

## Licence

All are under the **SIL Open Font License 1.1**, which permits bundling, subsetting and
redistribution and asks that the licence travel with the font. The full text of each is
here — `OpenSans-OFL.txt`, `Arimo-OFL.txt`, `NotoSansJP-OFL.txt`, `NotoSansSC-OFL.txt`,
`NotoSansThai-OFL.txt` — do not remove them.

- Open Sans — https://github.com/googlefonts/opensans
- Arimo — https://github.com/googlefonts/arimo
- Noto Sans JP, SC, Thai — https://github.com/notofonts

(`AUTHORSHIP.md` in the repository root guesses Apache 2.0 for these two. That was the
licence Open Sans shipped under years ago; both projects are on the OFL now, which is
what the files above actually say.)
