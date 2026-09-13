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
  see why below), two color pickers for `color1`/`color2` (defaulting to `fff` and
  `cf4c4e`), and a **Show** button.
- `result.html` — the page to add as the OBS **Browser Source** (instead of `lower.html`
  directly). On its own it just shows a black screen with a "Waiting for panel.html…" hint.

How it works: `panel.html` sends `{id, line1, line2, color1, color2}` over a
`BroadcastChannel` named `infor-r-lower-thirds` whenever you press **Show**. `result.html`
listens on that same channel and, on receiving a message, does a full
`window.location.href = 'lower.html?id=...&line1=...&line2=...&color1=...&color2=...'`
redirect to itself.

This full-page redirect is intentional, not a workaround: `js/lower.js` is not a page that
can be updated live — it is a top-level script that runs its `document.writeln()` calls
exactly once, reading `id`/`line1`/`line2`/`color1`/`color2` from the URL at load time.
There is no function inside it that can be called again to redraw with new text, so the
only reliable way to show new text is to reload `lower.html` with a new query string —
which is exactly what happens on the animation's normal page-load path, so nothing about
the original animation is touched. `lower.html`, `js/lower.js` and `css/lower.css` are left
completely unmodified; `result.html` is a thin wrapper placed next to them.

Usage:
1. Open `panel.html` in one window.
2. Open `result.html` in another window (or add it as an OBS Browser Source pointing at its
   local file path).
3. In `panel.html`, fill in `line1`/`line2`, pick a template and colors, and press **Show**.
4. `result.html` reloads itself into `lower.html?...` with the new parameters and plays the
   animation from the start.

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
