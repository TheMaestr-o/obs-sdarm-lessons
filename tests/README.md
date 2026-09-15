# Screenshot tests

A Playwright script that drives the panel and the overlay and saves the media
used by the [README](../README.md) and the hub page ([index.html](../index.html)).
Not an automated test suite with pass/fail assertions — it produces the actual
documentation screenshots, and is here so a future change can regenerate them
instead of retaking everything by hand.

## Setup

```bash
cd tests
npm init -y
npm install playwright
npx playwright install chromium
```

`style-previews.js` also needs `ffmpeg` on the PATH, and the project served
over HTTP (the panel `fetch()`es `lessons-data.json`, which browsers refuse
under `file://`):

```bash
cd ../OBS_InforR-Lower && python3 -m http.server 8001
```

## Run

```bash
node style-previews.js      # the animated style previews + panel shot
```

It produces the media the README and hub page lead with: an animated GIF and a
matching still for each of the three overlay styles, plus the control panel at
its real dock width. It captures PNG frames at 12fps and hands them to ffmpeg
(palettegen + paletteuse) rather than using Playwright's video recording, which
records the whole viewport instead of the tight 1920×300 crop of the lower third
these want. It overrides the page background with a flat dark gradient first —
the overlay is genuinely transparent, so shooting it as-is photographs white text
on a white page. Set `OBS_BASE_URL` if the server is not on port 8001.

It writes directly into [../screenshots/](../screenshots/), overwriting the
existing files, and resolves every path relative to its own location, so it works
from any checkout — no machine-specific paths to edit.
