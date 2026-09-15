# Bundled fonts

Two font files, carried here on purpose rather than pulled from a CDN.

`overlay.css` asks for Open Sans and Arimo. The original `css/lower.css` gets them with
two `@import url(https://fonts.googleapis.com/...)` lines at the top of the file. This
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
| `Arimo-Variable.woff2` | Arimo | `wght` 400–700 |

Both are variable fonts, so one file per family covers every weight `overlay.css` uses
(Open Sans 300/400/600, Arimo 400/700) instead of five separate static files. Converted
to WOFF2 from the upstream TrueType originals — about 490 KB for both, against roughly
1 MB as `.ttf`.

## Licence

Both are under the **SIL Open Font License 1.1**, which permits bundling and
redistribution and asks that the licence travel with the font. The full text of each is
here as `OpenSans-OFL.txt` and `Arimo-OFL.txt` — do not remove them.

- Open Sans — https://github.com/googlefonts/opensans
- Arimo — https://github.com/googlefonts/arimo

(`AUTHORSHIP.md` in the repository root guesses Apache 2.0 for these two. That was the
licence Open Sans shipped under years ago; both projects are on the OFL now, which is
what the files above actually say.)
