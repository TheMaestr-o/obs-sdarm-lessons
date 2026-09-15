# Screenshot tests

Playwright scripts that drive each plan's panel + overlay and save the
"config" and "result" screenshots used on the hub page ([index.html](../index.html)).
Not an automated test suite with pass/fail assertions — these produce the
actual documentation screenshots, and are here so a future change can
regenerate them instead of retaking everything by hand.

## Setup

```bash
cd tests
npm init -y
npm install playwright
npx playwright install chromium
```

## Run

```bash
node plan1-screenshots.js
node plan3-screenshots.js
```

Each script writes directly into [../screenshots/](../screenshots/), overwriting
the existing PNGs. Both scripts resolve every path relative to their own
location, so they work from any checkout — no machine-specific paths to edit.
