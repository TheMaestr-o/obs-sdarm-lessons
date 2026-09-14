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
  with a "Waiting for panel.html…" hint until the first message arrives.

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
that iframe's `src` to `lower.html?id=...&line1=...&line2=...&color1=...&color2=...&_t=...`
(the trailing `_t` is just a cache-buster timestamp so pressing **Show** twice with
identical text still forces a reload — setting `.src` to an unchanged value is a no-op in
every browser). Reloading only the iframe re-triggers `lower.js`'s `document.writeln` logic
and replays the animation, without navigating `result.html` itself away — unlike the
previous version of this file, which did a full top-level `window.location.href` redirect.

This reload-via-iframe approach is intentional, not a workaround: `js/lower.js` is not a
script that can be updated live — it runs its `document.writeln()` calls exactly once,
reading `id`/`line1`/`line2`/`color1`/`color2` from the URL at load time, with no exported
function to call again. Reloading the page it lives on is still the only reliable way to
show new text; doing that reload inside an iframe instead of at the top level is what makes
bottom-anchoring possible (see next section) and lets `result.html`'s own "Waiting for
panel.html…" message stay visible as a background fallback. `lower.html`, `js/lower.js` and
`css/lower.css` are left completely unmodified; `result.html` is a thin wrapper placed next
to them.

### Bottom-anchored positioning

`css/lower.css` centers its content on the full page (`main{position:absolute;height:100%}`
plus `.animation{margin:1em auto}`), which is fine when `lower.html` fills the whole OBS
canvas, but Plans 1 and 2 both anchor their overlay to the bottom-left corner instead — the
conventional "lower third" position. Rather than edit `css/lower.css` to change that
centering, `result.html` pins its `#overlayFrame` iframe to a **short strip at the bottom**
of the page (`position:fixed;left:0;bottom:0;width:100%;height:220px`). Percentage heights
inside an iframe resolve against the iframe's own height, not the outer page's — so
`lower.html`'s `main{height:100%}` becomes "100% of 220px", and its already-centered
`.animation` block ends up centered *within that short strip*, which reads visually as
bottom-anchored on the real 1920x1080 canvas. 220px was sized by checking the tallest
element in `css/lower.css` (animation 1's first line at `font-size:5em` = 80px, inside a
`.animation{height:4em}` = 64px box; animation 5's frame at `height:3.8em` ≈ 61px) — every
template fits comfortably with margin to spare. This was verified visually with Playwright
screenshots for all three templates (see the repo's `screenshots/plan3/` folder).

Usage:
1. Open `panel.html` in one window.
2. Open `result.html` in another window (or add it as an OBS Browser Source at the full
   canvas size, pointing at its local file path — no separate Chroma Key region setup is
   needed beyond the usual black-background keying, since the overlay is already confined
   to the bottom strip by the iframe).
3. In `panel.html`, fill in `line1`/`line2`, pick a style and colors, and press **Show**.
4. `result.html` reloads its iframe into `lower.html?...` with the new parameters and plays
   the animation from the start, anchored at the bottom of the frame.

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

The page background is solid black (`background-color: black` in `css/lower.css`), not CSS
`transparent`: there is no real alpha transparency in the page itself. Transparency in OBS
is achieved with a **Chroma Key** filter on the Browser source (keying out black) — as in
Plans 1/2, this is expected design behavior, not a bug.

Animations loop for 2 iterations (`alternate`, back and forth): the text appears, stays
visible briefly, then the same animation plays in reverse and the text disappears again. A
static screenshot/pause only makes sense in the middle of the "hold" phase — see
[../screenshots/plan3/](../screenshots/plan3/) for a screenshot of each template (`id=1..5`)
captured at that point.
