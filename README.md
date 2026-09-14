# SDARM Lesson Questions — OBS Lower Thirds

A comparison of ready-made "lower thirds" solutions for displaying Sabbath School lesson questions during a live OBS/Wirecast broadcast.

## ⚠️ Browser ≠ OBS

What you see here when opening these files directly in a regular browser (Chrome/Safari) is an approximation, not a guarantee of the exact look inside OBS. OBS renders a Browser Source through its own embedded engine (CEF), which may differ in font versions and spacing. Opening files here is fine for a quick check of text and logic, but **always verify the final look by adding the file as a real Browser Source inside OBS itself** — that's the only way to see what viewers will actually see.

Open [index.html](index.html) — it collects links to every plan with step-by-step instructions.

## Structure

```
OBS/
├── index.html                    — test bench with links to all plans
├── screenshots/                  — "config → result" screenshots for each plan
├── sbl-question-card/            — our own work (script that extracts real lesson questions)
│   ├── extract-questions.py
│   └── STREAMING_GUIDE.md
├── OBS_Animated-Lower-Thirds/    — Plan 1
├── OBS_LowerThirds/              — Plan 2
└── OBS_InforR-Lower/             — Plan 3
```

## Three plans

| # | Name | Panel↔overlay link | Offline | Text format |
|---|---|---|---|---|
| 1 | Animated Lower Thirds | BroadcastChannel + localStorage | ✅ fully | short: name + subtitle |
| 2 | Ultimate OBS Lower Thirds | BroadcastChannel + localStorage | ⚠️ pulls jQuery/fonts from a CDN | short: name + title |
| 3 | infor-r Lower Thirds | BroadcastChannel panel (`panel.html` → `result.html`), or raw URL params | ✅ fully (after localizing paths) | short: two lines, animated CodePen design rebuilt as our own CSS; 3 named styles (Slash & Slide, Slide Up / Down, Framed Reveal), always bottom-anchored, holds on screen indefinitely instead of auto-hiding |

All three are built for short "Name — Title" lower thirds, one line per field, and would need layout changes to fit a long Bible lesson question. In Plan 3, out of the 5 built-in templates (`id=1..5`) only `id=1,2,5` stay readable — `id=3` overlaps its two lines, `id=4` doesn't render the second line at all (see the screenshots in [screenshots/plan3/](screenshots/plan3/) and details in [OBS_InforR-Lower/LOCAL-SETUP.md](OBS_InforR-Lower/LOCAL-SETUP.md)).

## Origin and credit

- **Plan 1** — [Animated Lower Thirds](https://github.com/noeal-dac/Animated-Lower-Thirds) by NoeAL, MIT license
- **Plan 2** — Ultimate OBS Lower Thirds System (source not explicitly credited by its author)
- **Plan 3** — [lower-thirds-obs](https://github.com/vjccruz/lower-thirds-obs) by Vasco Cruz, based on an After Effects template by Amaksi and [CodePen mattchestnut/dMrONe](https://codepen.io/mattchestnut/pen/dMrONe)

Original files for each plan were left unchanged, except where explicitly noted inside that plan's own folder (see `LOCAL-SETUP.md` inside `OBS_InforR-Lower/`).

## Our own work

`sbl-question-card/extract-questions.py` — a script that pulls the real lesson questions (not made-up samples) straight from `/Users/ohnedan/Developer/sbl/data/<lang>/<lang>-YYYY-Q.json` for any lesson in the quarter, in every available language.

## Future plans

The list isn't closed — more options will be added here as we find them (see the "Plan 4" block on [index.html](index.html)), along with, likely, our own design that supports line-wrapping for a long question.
