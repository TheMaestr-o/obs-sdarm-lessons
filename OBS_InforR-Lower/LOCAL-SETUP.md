# Local setup (Plan 3)

This copy is based on https://github.com/vjccruz/lower-thirds-obs (see `README.md` and `LICENSE`
for the original attribution — do not remove). Differences from the original:

- The absolute paths `/css/lower.css` and `/js/lower.js` in `lower.html` were replaced with
  relative ones (`css/lower.css`, `js/lower.js`) so the page works over `file://` without a
  web server.
- In `scripts/lower-thirds-read-file.lua` (line 38), the author's external hosting URL
  `https://obs.infor-r.com/lower` was replaced with the local path to this `lower.html`.

## Option A — open directly by URL with parameters

No OBS at all, for a quick check in the browser or as a static Browser Source:

```
file:///Users/ohnedan/Developer/OBS/OBS_InforR-Lower/lower.html?id=1&line1=Question%20a&line2=What%20evidence...&color1=fff&color2=cf4c4e&duration=4s
```

Parameters:
- `id` — animation template number, 1–5 (see the limitations table below)
- `line1`, `line2` — text of the two lines (URL-encoded)
- `color1`, `color2` — hex color without `#` (defaults `fff` and `cf4c4e`)
- `duration` — animation duration, e.g. `4s` (defaults to its own value per `id`)

## Option B — via a Lua script in OBS (hotkey switching)

1. In OBS Studio, add a **Browser** source (name it e.g. "Lower Thirds"); the URL can be
   left empty — the script will overwrite it.
2. **Tools → Scripts → +** → select `scripts/lower-thirds-read-file.lua`.
3. In the script's settings panel, set:
   - **Browser source name** — the name of the source from step 1 ("Lower Thirds")
   - **File** — a text file with a list of lines (format below; you can start from
     `scripts/lower-thirds-read-file_sample.txt` as a sample)
   - if needed — `color1`/`color2` colors and the default template
4. Assign **next line / prev line** hotkeys (Settings → Hotkeys, search by the script's
   name) — they switch the line in the file and update the Browser source's URL.

### Text file format

Each line is `TEMPLATE_ID|LINE1|LINE2`, where `TEMPLATE_ID` is a number 1–5:

```
5|Frederic|Colins
2|John Doe|Motion Designer
```

## Option C — panel.html + result.html (recommended, matches Plans 1/2)

This is the same two-window pattern used by Plan 1 (`control-panel.html` +
`browser-source.html`) and Plan 2 (`obs_control_panel.html` +
`obs_lower_thirds_source.html`): one window to configure, one window/Browser Source that
shows the result, kept in sync over a `BroadcastChannel`. It replaces manually editing the
URL from Option A.

- `panel.html` — the control panel. Open it in a normal browser window/tab. It has a text
  field for `line1` (a short label, e.g. "Question a"), a textarea for `line2` (the actual
  lesson question, which can be long), a choice of template (**id=1, id=2 or id=5 only** —
  see why below) presented as three named styles with a one-line motion description and a
  small looping preview swatch, two color pickers for `color1`/`color2` (defaulting to
  `fff` and `cf4c4e`), and a **Show** button.
- `result.html` — the page to add as the OBS **Browser Source** (instead of `lower.html`
  directly), sized to the full canvas (e.g. 1920x1080). On its own it shows a black screen
  with a "Waiting for panel.html…" hint until the first message arrives. It embeds
  `native/overlay.html` (see below), **not** `lower.html`.

### Why this no longer uses lower.html: the "stays visible" requirement

The actual requirement for this project is that a lesson question stays on screen
indefinitely until the presenter chooses to advance to the next one — not that it
auto-hides after a few seconds. `css/lower.css` cannot do that: every template hardcodes
`-webkit-animation-iteration-count: 2` with `alternate` on its keyframes, so the text
slides in, holds briefly, and then the *same* animation immediately plays in reverse and
slides back out, with no parameter or hook to make it just stop after appearing.

An earlier version of this page tried to work around that from the outside: keep
`lower.html` unmodified inside an `<iframe>`, and after it loaded, reach into the iframe's
`contentDocument` from `result.html` to set `animation-play-state: paused` on the animated
elements, freezing them mid-hold before the reverse phase could start. This does not work:
Chromium enforces same-origin restrictions between `file://` documents strictly enough that
a parent `file://` page cannot read another `file://` iframe's `contentDocument`, even
though both report the identical `"file://"` origin via `window.location.origin`. This was
confirmed by logging from *inside* `result.html`'s own script (not just via an external
test harness, which has its own separate cross-context limitations that can produce
misleading results) — `iframe.contentDocument` reliably comes back `null`. Since OBS's
Browser Source is Chromium-based too (CEF), this isn't a testing artifact; it would fail
identically in real OBS usage. Patching further wasn't viable — the approach needed
replacing.

The fix: `OBS_InforR-Lower/native/` contains a from-scratch re-implementation of the three
templates' *visual style* (colors, fonts, transform shapes, easing curves, relative
timing) as our own CSS, with each animation restructured to run its "appear" phase exactly
once and then hold the final state forever (`animation-fill-mode: forwards`, no
`alternate`, `animation-iteration-count: 1`). Because there's no more reverse phase, there
is nothing left to freeze or reach into — `result.html` only ever *writes* the iframe's
`src`, it never reads anything back out of it, sidestepping the same-origin problem
entirely rather than working around it.

- `native/overlay.css` — the three style classes (`.style-slash-slide`,
  `.style-slide-up-down`, `.style-framed-reveal`), each a faithful re-timing of the
  matching original `#animation-N` block's "in" half.
- `native/overlay.html` — reads `id`/`line1`/`line2`/`color1`/`color2` from
  `URLSearchParams` (the same parameters `panel.html`/`result.html` already send) and
  builds the corresponding markup via plain DOM APIs through a single `render(id, line1,
  line2, color1, color2)` function, rather than `lower.js`'s `document.writeln()`
  approach. `render()` fully clears and rebuilds the overlay's markup, so a future
  live-update path (calling `render()` again without a reload) is a small change, not a
  rewrite — the current version still simply calls it once from the URL at load time,
  reloaded via the iframe on every "Show" press, same as before.
- Colors are applied via CSS custom properties (`--line1-color`, `--line2-color`) set as
  inline styles on the render root, rather than `lower.js`'s injected `<style>` block.
- Background is true CSS `background: transparent` on `html, body`, not the original's
  solid black. This is a deliberate improvement, safe specifically because
  `native/overlay.html` is only ever loaded as a small iframe inside `result.html`'s bottom
  strip, never as a full-canvas Browser Source on its own — real alpha transparency
  composites correctly with no Chroma Key filter needed, with no risk of a dark color in
  the lesson text itself getting keyed out. `lower.html`'s own solid-black-plus-Chroma-Key
  behavior is unchanged and still correct for Option A/B use.
- Bottom-anchoring no longer needs the "short iframe as a fake 100%-height screen" trick
  that `lower.html`'s centered CSS required. `native/overlay.html`'s own `#overlay-root` is
  `position: fixed; left: 0; bottom: 0` directly, so it bottom-anchors itself regardless of
  the size of whatever embeds it. `result.html` still embeds it in a 220px-tall iframe (see
  "Bottom-anchored positioning" below) purely because that's the intended lower-third
  height on the canvas, not because the iframe needs to be short for CSS reasons anymore.

`lower.html`, `js/lower.js` and `css/lower.css` remain in this repository byte-for-byte
unmodified. They're still fully usable directly via Option A (a static URL, e.g. for a
plain Browser Source pointed straight at `lower.html`) and Option B (the Lua
hotkey-switching script), and they remain here for attribution/reference regardless — but
the recommended Option C path described in this section no longer loads or depends on them
at all.

### The three template styles

| Style name | id | Motion |
|---|---|---|
| **Slash & Slide** | 1 | A diagonal accent slash fades in, then both lines slide in from the left |
| **Slide Up / Down** | 2 | Line 1 rises from below, line 2 drops from above |
| **Framed Reveal** | 5 | An animated frame draws itself in, then both lines slide in from below/above |

These are just friendlier names/descriptions for the same three `id` values `lower.js`
already understood — nothing about the underlying animations changed, only how `panel.html`
presents the choice.

### How it works

`panel.html` sends `{id, line1, line2, color1, color2}` over a `BroadcastChannel` named
`infor-r-lower-thirds` whenever you press **Show**. `result.html` keeps a single, persistent
`<iframe id="overlayFrame">` (created once, on page load) and, on receiving a message, sets
that iframe's `src` to
`native/overlay.html?id=...&line1=...&line2=...&color1=...&color2=...&_t=...` (the trailing
`_t` is just a cache-buster timestamp so pressing **Show** twice with identical text still
forces a reload — setting `.src` to an unchanged value is a no-op in every browser).
Reloading the iframe re-runs `native/overlay.html`'s `render()` call and replays the
animation, without navigating `result.html` itself away.

Pressing **Show** again — whether with the same text or different text — always replaces
whatever was showing, including an overlay whose animation had already finished and was
sitting in its held, fully-visible state: reloading the iframe discards the old DOM
entirely and `render()` rebuilds it from scratch for the new parameters. This is how the
two halves of the "stays until advanced" requirement are both satisfied: the overlay holds
indefinitely on its own (native/overlay.css's `forwards` fill, no reverse), and it still
changes cleanly the instant the presenter acts.

`result.html` no longer needs any logic to reach into the iframe after it loads (no
freeze-on-load, no `contentDocument` access at all) — see "Why this no longer uses
lower.html" above for why that used to be necessary and why it was removed instead of
fixed. This makes the current `result.html` simpler than the version it replaced, not more
complex: it only ever sets the iframe's `src` and never reads anything back out of it.

### Bottom-anchored positioning

`native/overlay.html`'s `#overlay-root` bottom-anchors itself directly
(`position:fixed;left:0;bottom:0;width:100%`), so — unlike the old `lower.html`-in-an-iframe
setup — the iframe's own height isn't load-bearing for positioning anymore. `result.html`
still pins `#overlayFrame` to a **220px-tall strip at the bottom of the page**
(`position:fixed;left:0;bottom:0;width:100%;height:220px`), simply because that's the
intended lower-third height on the 1920x1080 canvas, matching Plans 1/2's visual weight.
220px was sized by checking the tallest element across the three kept templates in
`css/lower.css` (animation 1's first line at `font-size:5em` = 80px, inside a
`.animation{height:4em}` = 64px box; animation 5's frame at `height:3.8em` ≈ 61px) — every
template fits comfortably with margin to spare, and `native/overlay.css` reuses the same
`4em`/`3.8em` box sizes. This was verified visually with Playwright screenshots for all
three templates (see the repo's `screenshots/plan3-styles/` folder and the native-overlay
test screenshots referenced in this file's history).

Usage:
1. Open `panel.html` in one window.
2. Open `result.html` in another window (or add it as an OBS Browser Source at the full
   canvas size, pointing at its local file path). No Chroma Key filter needed: both
   `result.html`'s own page (`background: transparent` on `html, body`) and the
   `native/overlay.html` it embeds are real CSS transparency — this is the one plan in
   the repo where Chroma Key genuinely isn't required, unlike Plans 1/2 and Options A/B
   of this same plan.
3. In `panel.html`, fill in `line1`/`line2`, pick a style and colors, and press **Show**.
4. `result.html` reloads its iframe into `native/overlay.html?...` with the new parameters,
   plays the appear animation once, and holds the fully-visible result at the bottom of the
   frame until you press **Show** again.

### Custom Browser Dock setup (an alternative to Control scene + Interact)

The steps above assume `panel.html` runs as a Browser Source inside a dedicated,
never-live "Control" scene, opened via right-click → **Interact** while you work — that
setup is confirmed working live. OBS also has a second way to keep a page permanently
on screen: **View → Docks → Custom Browser Docks**, which embeds a page directly into
OBS's own main window, alongside panels like Audio Mixer or Loudness (no scene, no
Interact needed — it's just always there).

**`BroadcastChannel` does not cross from a Custom Browser Dock to a scene's Browser
Source**, even though both run "inside OBS" — confirmed live: a docked `panel.html`'s
own UI works fine (clicking, typing), but pressing Show never updates `result.html`.
Docks appear to run in a separate CEF (Chromium Embedded Framework) request context
from scene sources, so `BroadcastChannel` — and `localStorage` under `file://` — don't
share state across that boundary, the same way two entirely different browsers
wouldn't.

The fix is the same category of fix as the dock-vs-source browser-isolation problem
generally: use something that isn't a same-context, in-memory browser API.
`panel.html` and `result.html` now also write/read a shared `localStorage` key
(`infor-r-lower-thirds-state`) as a fallback alongside `BroadcastChannel`, and
`result.html` listens for the browser's `storage` event (which fires in *other*
same-origin documents when `localStorage` changes — the correct primitive for
"another window/dock changed something, react to it"). This only works if both pages
share a real origin, though — and `file://` origins are partitioned per-directory/tab
in ways that don't reliably share storage across dock vs. scene-source contexts
either, mirroring the `BroadcastChannel` problem instead of solving it.

So Custom Browser Dock setup additionally requires serving this folder over
`http://` instead of `file://`:

1. Run a tiny static file server rooted at this folder, e.g.:
   ```
   cd /Users/ohnedan/Developer/OBS/OBS_InforR-Lower
   python3 -m http.server 8001
   ```
   (A `launchd` LaunchAgent — `~/Library/LaunchAgents/com.ohnedan.obs-lowerthirds-server.plist`
   — is set up on this machine to start this automatically at login, matching the same
   pattern already used for the unrelated `sbl` lesson project's own server. `launchctl
   list | grep obs-lowerthirds` should show it registered.)
2. In OBS, **View → Docks → Custom Browser Docks** → add one, URL:
   `http://localhost:8001/panel.html` (not `file://...` this time).
3. Set the live `result.html` Browser Source's URL to `http://localhost:8001/result.html`
   too — both pages need to be on the exact same origin (`http://localhost:8001`) for
   `localStorage`/the `storage` event to bridge them. Mixing `file://` for one and
   `http://` for the other will not work.
4. Everything else (fill in `line1`/`line2`, pick a style, press Show) works the same
   as the Interact-based setup.

The `Control` scene + Interact setup from the main steps above still works exactly as
documented and does not need the local server — use whichever fits how you like to
work; a docked panel stays visible regardless of which scene is live, while the
Interact approach needs you to switch to the Control scene first.

## Lesson & Question picker

`panel.html` has a third collapsible section, **Lesson & Question** (open by default,
above **Style & colors** which stays collapsed — style/colors is set once and left
alone, while picking a lesson/question is the thing actually used every single question
during a stream). It lets you pick a language and lesson from dropdowns, click a
question from that lesson's question list to auto-fill Line 1 (the lesson title) and
Line 2 (`letter. question text`), and then step forward/back through that lesson's
questions with **Previous**/**Next** buttons instead of reopening the list each time.
Line 1/Line 2 stay plain, manually-editable text fields after a pick — this only fills
them in as a starting point, e.g. so you can still shorten a long question by hand
afterwards.

- **Language** defaults to `ru` (the base language this project's lesson content is
  written in) if present, else whichever language code sorts first.
- Switching **Language** preserves the current **Lesson** number rather than resetting
  to lesson 1 — smoother if you're mid-question and just want the same lesson in a
  different language. The question list resets (nothing "loaded") on any language or
  lesson change, since there's no single obviously-correct question to jump to
  automatically; click a question or use Previous/Next once one is loaded.
- **Previous**/**Next** are disabled (not wrapped) at the first/last question of a
  lesson, matching how disabled controls already behave elsewhere in this project.

### Where the data comes from

The picker reads `lessons-data.json` (in this same folder), a single bundle of every
lesson/question in all 22 supported languages, built by `tools/build-lessons-data.py`
from the same per-language source files the rest of this project's tooling reads
(`/Users/ohnedan/Developer/sbl/data/<lang>/<lang>-<year>-<quarter>.json`). **Re-run this
script whenever a new quarter's data appears there:**

```
cd /Users/ohnedan/Developer/OBS/OBS_InforR-Lower
python3 tools/build-lessons-data.py --year YYYY --quarter Q
```

This overwrites `lessons-data.json` in place. `panel.html` just `fetch()`s it by its
relative path on page load — no other step is needed afterwards, just reload the panel.

### file:// vs. http:// — the picker needs the http:// dock setup

`fetch('lessons-data.json')` (a relative path) **throws under `file://`** — confirmed
directly in this project with Playwright: Chromium refuses the request outright
(`Fetch API cannot load file://... URL scheme "file" is not supported`), the same
`TypeError: Failed to fetch` behavior this project had already run into elsewhere with
`file://` and local JSON. It works cleanly under `http://` (the Custom Browser Dock
setup described above, `python3 -m http.server 8001`), fetching and parsing all 22
languages without issue.

Because of this, **the Lesson & Question picker only works when `panel.html` is opened
over `http://localhost:8001/panel.html`, not as a plain `file://` path.** When opened
via `file://`, `panel.html` detects this up front (checking `location.protocol` before
ever calling `fetch()`, so no console error is thrown) and replaces the picker's
controls with a short inline note — *"Lesson/question picker requires the http:// dock
setup — see LOCAL-SETUP.md"* — instead of failing silently or leaving a broken control
on screen. Line 1/Line 2, Style & colors, and the Show button are completely unaffected
either way; only the picker itself needs the server.

## Design limitation: short "Name — Title" format

Like Plans 1 and 2, this design (based on the original CodePen
https://codepen.io/mattchestnut/pen/dMrONe) is built for a short pair of lines like
"Name — Job Title/Role", not a long multi-line lesson question. When a long `line2` is used
(e.g. a full lesson question), behavior differs by template:

| id | Behavior with a long line2 |
|----|---------------------------|
| 1  | Works fine — both lines stack one under the other, readable |
| 2  | Works fine — both lines centered, readable |
| 3  | **Not usable** — line1 and line2 sit in two halves of one row (50% width each) and **overlap** if line2 is longer than half the screen width |
| 4  | **line2 is not used at all** in this template — only line1 plus a decorative bar is drawn |
| 5  | Works fine — both lines framed, readable |

This is exactly why the Option C panel only offers id=1, id=2 and id=5 as template choices.

The rest of this section describes `lower.html`/`css/lower.css`/`js/lower.js` themselves,
which is what Options A and B load directly. **Option C's `native/overlay.html` behaves
differently on both points below** — see "Why this no longer uses lower.html" earlier in
this file for the full reasoning:

- `lower.html`'s page background is solid black (`background-color: black` in
  `css/lower.css`), not CSS `transparent` — there is no real alpha transparency in that
  page itself, and Transparency in OBS for Options A/B is achieved with a **Chroma Key**
  filter on the Browser source (keying out black), same as Plans 1/2. This is expected
  design behavior for `lower.html`, not a bug. `native/overlay.html` (Option C) instead
  uses true CSS `background: transparent`, since it's only ever loaded as a small iframe
  rather than a full-canvas source — see above for why that's safe there.
- `lower.html`'s animations loop for 2 iterations (`alternate`, back and forth): the text
  appears, stays visible briefly, then the same animation plays in reverse and the text
  disappears again. A static screenshot/pause of `lower.html` only makes sense in the
  middle of the "hold" phase — see [../screenshots/plan3/](../screenshots/plan3/) for a
  screenshot of each template (`id=1..5`) captured at that point. `native/overlay.html`
  (Option C) instead runs its appear animation once and then holds indefinitely — there is
  no reverse phase and no auto-hide, so a screenshot taken at any point after the appear
  animation finishes (immediately after, or minutes later) shows the same fully-visible
  result.
