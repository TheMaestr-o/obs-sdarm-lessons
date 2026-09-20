# Local setup

How the overlay system is put together and why it is built this way. For the
click-by-click OBS walkthrough, see [../HOW-TO-USE-IN-OBS.md](../HOW-TO-USE-IN-OBS.md);
for Wirecast, [WIRECAST-SETUP.md](WIRECAST-SETUP.md).

This folder started life as a copy of https://github.com/vjccruz/lower-thirds-obs
(MIT, by Vasco Cruz). None of that code is here anymore — the overlay was rewritten from
scratch for a requirement the original could not meet, and once nothing loaded the
borrowed files they were removed. The section "Why the animations were rebuilt" below is
the reason, and it is worth reading before changing anything in `native/`.

## The two pages

- **`panel.html`** — the control panel. It has a text field for `line1` (a short label,
  e.g. a day heading), a textarea for `line2` (the actual lesson question, which can be
  long), a choice of the three styles presented with a one-line motion description and a
  small looping preview swatch, two color pickers for `color1`/`color2` (defaulting to
  `fff` and `cf4c4e`) shown as a small round swatch each — clicking a swatch opens the
  browser's native color picker directly, there is no separate visible hex text field
  next to it (the hex value is still tracked internally for the Show payload, it is just
  not rendered as its own control) — and a **Show** button.
- **`result.html`** — the page to add as the OBS **Browser Source**, sized to the full
  canvas (e.g. 1920x1080). On its own it shows a black screen with a "Waiting for
  panel.html…" hint until the first message arrives. It embeds `native/overlay.html`.

Usage:

1. Open `panel.html` in one window.
2. Open `result.html` in another window (or add it as an OBS Browser Source at the full
   canvas size). No Chroma Key filter needed: both `result.html`'s own page
   (`background: transparent` on `html, body`) and the `native/overlay.html` it embeds
   are real CSS transparency.
3. In `panel.html`, fill in `line1`/`line2`, pick a style and colors, and press **Show**.
4. `result.html` reloads its iframe into `native/overlay.html?...` with the new
   parameters, plays the appear animation once, and holds the fully-visible result at
   the bottom of the frame until you press **Show** again.

## Why the animations were rebuilt

The requirement for this project is that a lesson question stays on screen indefinitely
until the presenter chooses to advance — not that it auto-hides after a few seconds.

The lower-thirds CSS this project began from could not do that. Every template there
hardcodes `-webkit-animation-iteration-count: 2` with `alternate` on its keyframes, so
the text slides in, holds briefly, and then the *same* animation immediately plays in
reverse and slides back out, with no parameter or hook to make it stop after appearing.

An earlier version tried to work around that from the outside: keep the original page
unmodified inside an `<iframe>`, and after it loaded, reach into the iframe's
`contentDocument` from `result.html` to set `animation-play-state: paused` on the
animated elements, freezing them mid-hold before the reverse phase could start. **This
does not work.** Chromium enforces same-origin restrictions between `file://` documents
strictly enough that a parent `file://` page cannot read another `file://` iframe's
`contentDocument`, even though both report the identical `"file://"` origin via
`window.location.origin`. This was confirmed by logging from *inside* `result.html`'s own
script (not just via an external test harness, which has its own separate cross-context
limitations that can produce misleading results) — `iframe.contentDocument` reliably
comes back `null`. Since OBS's Browser Source is Chromium-based too (CEF), this is not a
testing artifact; it would fail identically in real OBS usage. Patching further was not
viable — the approach needed replacing.

The fix: `native/` is a from-scratch implementation of the three styles, with each
animation restructured to run its "appear" phase exactly once and then hold the final
state forever (`animation-fill-mode: forwards`, no `alternate`,
`animation-iteration-count: 1`). Because there is no more reverse phase, there is nothing
left to freeze or reach into — `result.html` only ever *writes* the iframe's `src`, it
never reads anything back out of it, sidestepping the same-origin problem entirely rather
than working around it.

- `native/overlay.css` — the three style classes (`.style-slash-slide`,
  `.style-slide-up-down`, `.style-quiet-rule`). Styles 1 and 2 reproduce the *motion* of
  Matt Chestnut's CodePen (https://codepen.io/mattchestnut/pen/dMrONe) deliberately — the
  easing curve and the travel distances are his numbers, carried across on purpose, and
  the file's own header says so. `.style-quiet-rule` has nothing behind it and is this
  project's own design.
- `native/overlay.html` — reads `id`/`line1`/`line2`/`color1`/`color2` from
  `URLSearchParams` (the same parameters `panel.html`/`result.html` already send) and
  builds the corresponding markup via plain DOM APIs through a single `render(id, line1,
  line2, color1, color2)` function. `render()` fully clears and rebuilds the overlay's
  markup, so a future live-update path (calling `render()` again without a reload) is a
  small change, not a rewrite — the current version still simply calls it once from the
  URL at load time, reloaded via the iframe on every "Show" press.
- Colors are applied via CSS custom properties (`--line1-color`, `--line2-color`) set as
  inline styles on the render root.
- Background is true CSS `background: transparent` on `html, body`. Real alpha
  transparency composites correctly with no Chroma Key filter needed, with no risk of a
  dark color in the lesson text itself getting keyed out.
- Bottom-anchoring needs no tricks. `native/overlay.html`'s own `#overlay-root` is
  `position: fixed; left: 0; bottom: 0` directly, so it bottom-anchors itself regardless
  of the size of whatever embeds it.

## The three styles

| Style name | id | Motion |
|---|---|---|
| **Slash & Slide** | 1 | A gold stripe draws up its own slant, a plate cut at the same 13° wipes out from behind it, then both lines slide in from the plate's edge |
| **Slide Up / Down** | 2 | A scrim fades in; line 1 rises from below, line 2 drops from above |
| **Quiet Rule** | 3 | A vertical rule draws down at the right, both lines settling in beside it |

The panel offers the first two. Quiet Rule is still in `native/overlay.css` and still
renders for `id=3`; the design settled on two styles, so the panel's list did too.

Style 1's geometry is read off the author's Figma frame, not eyeballed — text block at
x 121, heading at 150.76 and question at 134.20 so the two lines step along the slant,
each line stopping as far from the right edge as it starts from the left. The plate has no
fixed height: it is pinned 16px above and 35.6px below the text block, so a question that
wraps simply makes it taller. The one thing CSS cannot work out is how far left the foot of
the slant must reach for a given height, so `overlay.html` measures the plate and writes
that number (`--ss-slant`, height × 26.5/115.5) back for the `clip-path` to use.

Ids 1 and 2 keep the numbers the original used for the same two motions. Id 3 does not:
it is this project's own style, and it took over the number from an original id-3
template that was unusable here — its two lines sat in 50%-width halves of one row and
overlapped whenever line2 ran long. Two further originals were dropped for related
reasons: id 4 never rendered line2 at all, only line1 plus a decorative bar; and id 5
"Framed Reveal" drew an SVG frame that boxed in a wrapping question sentence it was never
sized for. All three failures are the same underlying problem — those templates were
designed for a short "Name — Job Title" pair, not a full lesson question that wraps.

## How it works

`panel.html` sends `{id, line1, line2, ref, color1, color2, mode}` over a
`BroadcastChannel` named `infor-r-lower-thirds` whenever you press **Show**, and
`{mode: 'hide'}` on **Stop**. `result.html` keeps a single, persistent
`<iframe id="overlayFrame">` and passes what it receives on to `native/overlay.html`
inside it — in one of two ways.

**The first thing shown goes by URL.** The iframe starts empty, so `result.html` sets its
`src` to `native/overlay.html?id=...&line1=...&line2=...&ref=...&_t=...` (the trailing
`_t` is a cache-buster: setting `.src` to an unchanged value is a no-op in every browser).
The overlay reads those parameters at load and plays its entrance. This is the route the
overlay has always had, and `result-wirecast.html` still uses nothing else.

**Everything after that goes by `postMessage`.** Once loaded, the overlay tells its parent
it is listening (`{type: 'ready'}`), and from then on `result.html` posts
`{type: 'show', data}` and `{type: 'hide'}` to it instead of reloading it. The overlay
decides how the new content should arrive:

- nothing on air, or a different style → a fresh render and the full entrance;
- same style already on air → a **swap**: only the row whose text changed slides out and
  back, the plate and any unchanged line are left alone, and if the line count changed the
  block's height is walked from old to new so the plate grows rather than jumps;
- `hide` → the **exit**, the entrance in reverse; when it has played the overlay reports
  `{type: 'hidden'}` and `result.html` hides the iframe. A 1.2s timer hides it regardless,
  so Stop means stop even if the page inside is in no state to answer.

Why messages and not reaching into the iframe: a `file://` page cannot read another
`file://` iframe's `contentDocument` — that dead end is what `native/` was built to get
around in the first place — but posting to it is allowed across any origins, `file://`
included. `result.html` still never reads anything out of the iframe.

The "stays until advanced" requirement is met the same way as before: no animation in
`native/overlay.css` reverses or repeats. Every entrance is a `from`-only keyframe with
`backwards` fill, so the resting state in the stylesheet *is* the visible state — if an
animation ever fails to start, the question is simply on screen without having moved,
rather than invisible.

### Bottom-anchored positioning

`native/overlay.html`'s `#overlay-root` bottom-anchors itself directly
(`position:fixed;left:0;bottom:0;width:100%`), so the iframe's own height is not
load-bearing for positioning. `result.html` still pins `#overlayFrame` to a **220px-tall
strip at the bottom of the page** (`position:fixed;left:0;bottom:0;width:100%;height:220px`),
simply because that is the intended lower-third height on the 1920x1080 canvas. 220px was
sized by checking the tallest element across the three styles (style 1's first line at
`font-size:5em` = 80px, inside a `.animation{height:4em}` = 64px box) — every style fits
comfortably with margin to spare. This was verified visually with Playwright screenshots
for all three styles (see [`../screenshots/plan3-styles/`](../screenshots/plan3-styles/)).

## Custom Browser Dock setup (an alternative to Control scene + Interact)

The steps above assume `panel.html` runs as a Browser Source inside a dedicated,
never-live "Control" scene, opened via right-click → **Interact** while you work — that
setup is confirmed working live. OBS also has a second way to keep a page permanently on
screen: **View → Docks → Custom Browser Docks**, which embeds a page directly into OBS's
own main window, alongside panels like Audio Mixer or Loudness (no scene, no Interact
needed — it is just always there).

**`BroadcastChannel` does not cross from a Custom Browser Dock to a scene's Browser
Source**, even though both run "inside OBS" — confirmed live: a docked `panel.html`'s own
UI works fine (clicking, typing), but pressing Show never updates `result.html`. Docks
appear to run in a separate CEF (Chromium Embedded Framework) request context from scene
sources, so `BroadcastChannel` — and `localStorage` under `file://` — do not share state
across that boundary, the same way two entirely different browsers would not.

The fix is the same category of fix as the dock-vs-source browser-isolation problem
generally: use something that is not a same-context, in-memory browser API. `panel.html`
and `result.html` also write/read a shared `localStorage` key
(`infor-r-lower-thirds-state`) as a fallback alongside `BroadcastChannel`, and
`result.html` listens for the browser's `storage` event (which fires in *other*
same-origin documents when `localStorage` changes — the correct primitive for "another
window/dock changed something, react to it"). This only works if both pages share a real
origin, though — and `file://` origins are partitioned per-directory/tab in ways that do
not reliably share storage across dock vs. scene-source contexts either, mirroring the
`BroadcastChannel` problem instead of solving it.

So Custom Browser Dock setup additionally requires serving this folder over `http://`
instead of `file://`:

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
4. Everything else (fill in `line1`/`line2`, pick a style, press Show) works the same as
   the Interact-based setup.

The `Control` scene + Interact setup from the main steps above still works exactly as
documented and does not need the local server — use whichever fits how you like to work;
a docked panel stays visible regardless of which scene is live, while the Interact
approach needs you to switch to the Control scene first.

## Lesson & Question picker

`panel.html` has a third collapsible section, **Lesson & Question** (open by default,
above **Settings** which stays collapsed — Settings is set once per session and left
alone, while picking a lesson/question is the thing actually used every single question
during a stream). It shows which lesson is currently active as a small label (e.g. "1.
Любовь Божья к человеку" — the **Lesson** dropdown itself lives inside **Settings**, see
below), then lets you click a small letter button (**а**, **б**, **в**...) from that
lesson's question list to auto-fill Line 1 and Line 2, and step forward/back through that
lesson's questions with **Previous**/**Next** buttons instead of reopening the list each
time. Line 1/Line 2 stay plain, manually-editable text fields after a pick — this only
fills them in as a starting point, e.g. so you can still shorten a long question by hand
afterwards. Line 1/Line 2 have no visible field labels above them either (just a
placeholder shown only while empty) — keeping this section short is the point, since it
sits on screen for the whole stream.

The question list itself is a compact grid of small per-letter buttons, not a list of
full question sentences — this is deliberately scannable for clicking through fast during
a live stream instead of reading a wall of text each time. The full question text for any
button is available two ways: hovering it shows the browser's native tooltip, and
hovering/keyboard-focusing/clicking it also fills a small preview line just below the
button grid with `letter. full text` — the preview is the faster of the two to read live,
since a native tooltip is slow to appear and does not work on touch/keyboard.

**Quarter**, **Language**, and the **Lesson** dropdown itself all live inside the
collapsed **Settings** section (alongside style/colors) — picking those is a "choose once
per session" action, unlike the question list, which changes every question. The
always-visible Lesson & Question area only shows which lesson is currently active, as a
small label. Changing Quarter, Language, or Lesson inside Settings still correctly updates
that label and repopulates the always-visible question list above it, even though the
controls you just used are tucked inside a collapsed section — that is intentional, not a
bug: open Settings to change quarter, language, or lesson, then collapse it again and
forget about it for the rest of the stream.

- **Language** defaults to `ru` (the base language this project's lesson content is
  written in) if present, else whichever language code sorts first — unless a valid saved
  value exists (see "Remembering your settings" below), which takes priority over this
  default.
- **Quarter** defaults to the newest quarter (the data's `"YYYY-Q"` keys sorted
  descending) — unless a valid saved value exists, same as Language.
- Switching **Quarter** or **Language** preserves the current **Lesson** number rather
  than resetting to lesson 1 — smoother if you are mid-question and just want the same
  lesson in a different language/quarter. Switching **Quarter** also preserves the current
  **Language** selection when the new quarter still has it. The question list resets
  (nothing "loaded") on any quarter, language, or lesson change, since there is no single
  obviously-correct question to jump to automatically; click a question or use
  Previous/Next once one is loaded.
- **Previous**/**Next** are disabled (not wrapped) at the first/last question of a lesson,
  matching how disabled controls already behave elsewhere in this project.
- Each lesson's letter buttons are grouped under their own **day heading** (e.g. "1. БОГ
  ЕСТЬ ЛЮБОВЬ", "2. МИССИЯ ИИСУСА") rather than shown as one flat row. **Letters restart
  at a/а for every day** — a lesson has multiple days, each with its own 2-3 questions
  lettered independently (day 1: а, б; day 2: а, б; day 4: а, б, в; etc.) — so each
  group's heading is what makes that restart make sense instead of reading like a bug.
  Clicking a letter button (or reaching it via Previous/Next) fills **Line 1 with that
  question's own day heading** (not the lesson's overall title) and **Line 2 with
  `letter. question text`** — crossing from one day's last question into the next day's
  first question via Next/Previous correctly updates Line 1 to the new day's heading.
- Both the letter and the day heading render in **exactly the case they have in the source
  lesson data** — no CSS forces upper/lowercase on them. This matters because not every
  language's day heading is stored the same way: Russian's happens to already be written
  in full caps in the source ("1. БОГ ЕСТЬ ЛЮБОВЬ"), but German/English/French are not
  ("1. Gott ist Liebe", "1. God Is Love") — forcing a transform would have shown those in
  a case that does not match the actual lesson content.

This case-preservation is specific to the panel's own question list. The **overlay itself**
(`native/overlay.css`) still renders Line 1 in caps by design — that is the lower-third's
day/topic heading, styled after the CodePen reference, which was already all-caps. Line 2
(the actual question) on the overlay is NOT forced to caps either, for the same reason as
the panel's list: a full question sentence shown in caps on stream reads as shouting and
does not match how the lesson itself presents it.

### Color pickers

**Color 1** and **Color 2** are shown as small circular swatches only — clicking one opens
your OS's native color picker directly, same as any `<input type="color">`, just styled to
read as a compact icon instead of the browser's default rectangular control. The hex value
next to each swatch (e.g. `fff`, `c6a15b`) is no longer shown as a visible text field — it
still exists in the page (kept in sync with the swatch, and read when building the Show
payload), it is just not rendered as a separate control anymore, since the swatch alone is
enough to pick and see the current color.

### Remembering your settings

**Quarter**, **Language**, and the last-selected **Lesson** are saved to `localStorage`
(key `infor-r-lower-thirds-panel-settings`) every time you change any of them, and restored
automatically the next time you open `panel.html` — no need to re-pick your language every
stream. This is a separate `localStorage` key from the one `panel.html`/`result.html`
already use to hand off the currently-shown overlay to each other
(`infor-r-lower-thirds-state`, see "Custom Browser Dock setup" above); the two do not
interact. On load, a saved value is only restored if it is still valid against the
freshly-fetched `lessons-data.json` (e.g. if a saved language was removed from a rebuilt
bundle, or a saved lesson number does not exist in the restored quarter/language) —
otherwise the normal defaults above apply. Works under the same `http://localhost:8001`
setup the picker already requires (see below); no internet connection is used or needed,
`localStorage` under `http://` persists locally regardless of whether the machine is
online.

### Where the data comes from

The picker reads `lessons-data.json` (in this same folder), built by
`tools/build-lessons-data.py` from the same per-language source files the rest of this
project's tooling reads
(`/Users/ohnedan/Developer/sbl/data/<lang>/<lang>-<year>-<quarter>.json`). Its top-level
shape is:

```json
{
  "quarters": {
    "2026-3": {
      "year": 2026,
      "quarter": 3,
      "languages": {
        "ru": { "quarterTitle": "...", "lessons": [ /* ... */ ] },
        "en": { "quarterTitle": "...", "lessons": [ /* ... */ ] }
      }
    }
  }
}
```

Each `"YYYY-Q"` key under `quarters` bundles every lesson/question for that quarter, in all
22 supported languages. Each lesson's `questions` array is flattened from the source's
per-day `dailyLessons`, but every question keeps its own `sectionTitle` (the day heading it
came from) and its own `letter` (restarting at a/а per day) — see the "day heading" bullet
above for why this matters to the UI.

**Re-run this script whenever a new quarter's data appears** under
`/Users/ohnedan/Developer/sbl/data/<lang>/`:

```
cd /Users/ohnedan/Developer/OBS/OBS_InforR-Lower
python3 tools/build-lessons-data.py
```

This scans every language's folder for whatever `<lang>-YYYY-Q.json` files actually exist
there and overwrites `lessons-data.json` in place with all of them — no year/quarter
arguments needed, and no code change needed here to pick up a new quarter, just drop its
files in and rerun. `panel.html` just `fetch()`es the result by its relative path on page
load — no other step is needed afterwards, just reload the panel. The new quarter will
appear as an extra option in the Quarter dropdown (inside Settings) automatically.

### file:// vs. http:// — the picker needs the http:// setup

`fetch('lessons-data.json')` (a relative path) **throws under `file://`** — confirmed
directly in this project with Playwright: Chromium refuses the request outright (`Fetch API
cannot load file://... URL scheme "file" is not supported`), the same `TypeError: Failed to
fetch` behavior this project had already run into elsewhere with `file://` and local JSON.
It works cleanly under `http://` (the Custom Browser Dock setup described above, `python3
-m http.server 8001`), fetching and parsing all 22 languages without issue.

Because of this, **the Lesson & Question picker (and Quarter/Language inside Settings) only
works when `panel.html` is opened over `http://localhost:8001/panel.html`, not as a plain
`file://` path.** When opened via `file://`, `panel.html` detects this up front (checking
`location.protocol` before ever calling `fetch()`, so no console error is thrown) and
replaces both the Lesson/question controls and the Quarter/Language row with a short,
friendly inline note — *"This panel needs the local server. Open it as
**http://localhost:8001/panel.html** instead of double-clicking panel.html — see
LOCAL-SETUP.md for details."* — instead of failing silently or leaving broken/empty controls
on screen. The **Lesson & Question** section's own collapsed-summary label also changes to
*"Lesson & Question (needs http://localhost:8001)"* in this state, so it is clear at a
glance without even opening the section. If you ever see either of these, it almost always
means `panel.html` was opened by double-clicking the file (giving a `file://...` address
bar) instead of via the `http://localhost:8001/...` URL the launchd-started local server
already serves — switch the tab/address to that URL and the picker works immediately, no
other fix needed. Line 1/Line 2, the style/color picker, and the Show button are unaffected
either way; only the data-driven parts of the picker (Lesson/Question, Quarter, Language)
need the server.

## Design note: the styles came from a short "Name — Title" format

The CodePen the motion of styles 1 and 2 comes from
(https://codepen.io/mattchestnut/pen/dMrONe) was built for a short pair of lines like
"Name — Job Title/Role", not a long multi-line lesson question. Styles 1 and 2 survived
that change of purpose because both stack their two lines vertically and wrap cleanly;
the originals that did not survive are listed under "The three styles" above. Keep this
in mind when adding a fourth style: whatever it does has to stay readable when `line2` is
a full sentence that wraps to two or three lines.
