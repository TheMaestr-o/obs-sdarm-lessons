# How to use this overlay in real OBS Studio

This is the practical, step-by-step version — not the technical writeup in
[`OBS_InforR-Lower/LOCAL-SETUP.md`](OBS_InforR-Lower/LOCAL-SETUP.md), which
covers how the thing works and why.

Everything lives in `OBS_InforR-Lower/`. The overlay holds the question on
screen until you manually advance it, needs no Chroma Key filter at all, and
works fully offline.

---

## One-time setup

1. In OBS, add a new source: **Sources → (+) → Browser**.
2. Name it something like "Lesson Question".
3. Check **Local file**, then browse to:
   ```
   /Users/ohnedan/Developer/OBS/OBS_InforR-Lower/result.html
   ```
4. Set **Width: 1920, Height: 1080** (or match your canvas size).
5. Leave **Shutdown source when not visible** unchecked, so it doesn't reset
   between scene switches.
6. Click OK. The source will look empty for now — that's expected, nothing
   shows until you press Show in the control panel (see below).
7. Position it in your scene: it always renders at the **bottom-left** of
   its own 1920×1080 box, so if your Browser Source is full-canvas, the
   overlay will sit at the bottom of the stream. Resize/reposition the
   *source* in OBS if you want it somewhere else.
8. **No Chroma Key filter needed** — skip that step entirely, the background
   is genuinely transparent.

## Controlling it during the stream

**Important — do not open `panel.html` in a regular browser (Chrome, Safari,
Brave...).** The panel and the overlay talk to each other over a mechanism
(`BroadcastChannel`) that only works between pages running inside the *same*
browser engine. OBS's Browser Source runs its own separate, isolated engine
— a page open in Chrome/Safari/Brave cannot reach it, even though it's the
same file on the same computer. The panel has to run *inside OBS too*.

Set this up once:

1. Create a **new, separate scene** just for the panel — click the **+**
   under the Scenes list, name it something like "Control". Never switch
   this scene to live/program output; it's only for your own use.
2. With the "Control" scene selected, add another **Sources → (+) →
   Browser** — a brand-new source, not the same one as `result.html`.
3. Local file → browse to:
   ```
   /Users/ohnedan/Developer/OBS/OBS_InforR-Lower/panel.html
   ```
   Size doesn't matter much — 900×800 is comfortable.

To actually type into it during the stream:

1. Switch to the "Control" scene (this never goes live, so it's safe to sit
   on it while you work).
2. Right-click the panel source in the Sources list → **Interact**. A
   separate window opens where the panel is actually clickable/typeable.
3. In that window, for each question, fill in:
   - **Line 1** — the lesson topic (e.g. "God's Love for Man")
   - **Line 2** — the letter and the question (e.g. "a. What evidence of
     God's love is given to humanity?")
   - **Template** — pick one of the three style cards (Slash & Slide, Slide
     Up / Down, Quiet Rule) — click to preview the little animation
     right in the panel before committing
   - **Colors** — leave as-is (gold accent, matching the lesson) or pick
     your own
3. Press **Show**. The question animates onto the bottom of your stream and
   **stays there** — it will not disappear on its own.
4. When you're ready for the next question, just fill in the new Line
   1/Line 2 and press **Show** again — the old question is replaced
   instantly by the new one, playing the entrance animation again.
5. To temporarily clear the overlay without a new question queued, you'd
   need to hide the Browser Source in OBS itself (click the eye icon next
   to the source) and unhide it later — there's currently no "hide" button
   in the panel itself, only "show the next thing."

## Alternative: a permanent dock instead of a Control scene

The Control-scene setup above works, but you have to switch to that scene
every time you want to type a new question. OBS has a way to keep the panel
**permanently visible** in its own main window instead — a **Custom Browser
Dock**, the same kind of panel as the built-in Audio Mixer or Loudness
meters. This needs one extra piece of setup (a small local server) but then
you never have to switch scenes to reach the panel again.

**One-time setup:**

1. A small file server for this folder already runs automatically on this
   machine (via a `launchd` LaunchAgent, `com.ohnedan.obs-lowerthirds-server`)
   at `http://localhost:8001` — nothing to start manually. If it's ever not
   responding, run `launchctl list | grep obs-lowerthirds` to check, or start
   it by hand with `cd /Users/ohnedan/Developer/OBS/OBS_InforR-Lower && python3
   -m http.server 8001`.
2. **View → Docks → Custom Browser Docks** → add one → URL:
   ```
   http://localhost:8001/panel.html
   ```
3. **Important:** the live `result.html` Browser Source's URL must also be
   switched to `http://localhost:8001/result.html` (uncheck "Local file",
   type that URL instead) — the panel and the overlay only talk to each
   other correctly when both are loaded from the exact same
   `http://localhost:8001` address. Mixing a `file://` result.html with an
   `http://` docked panel will not work.

Once both are on `http://localhost:8001`, the dock behaves exactly like the
Control-scene panel — fill in Line 1/Line 2, pick a style, press Show — except
it's always on screen in OBS's own window, regardless of which scene is live.

## Quick pre-stream checklist

- [ ] `result.html` added as a Browser Source, sized to your canvas
- [ ] `panel.html` open in a separate window, ready to type into
- [ ] Tested at least one "Show" press to confirm text appears on the OBS
      preview (not just in the browser tab — always check the actual OBS
      output)
- [ ] Confirmed no Chroma Key filter is on the source (it would do nothing
      useful here and could theoretically key out dark parts of your text)

---

## If something looks wrong

- **Nothing shows up at all**: open `result.html` directly in a normal
  browser tab (not through OBS) and check if it works there first — if it
  doesn't, the panel and result windows probably aren't talking to each
  other (both need to stay open, and both need to be on the same origin —
  see the dock section above).
- **Text is there but looks different from these instructions' screenshots**:
  OBS renders Browser Sources through its own engine, which can differ
  slightly from a regular browser in fonts/spacing — this is normal, not a
  bug. Judge it by the actual OBS preview, not by how it looks in a browser
  tab.
- **Want to see what it looks like first**: open
  `/Users/ohnedan/Developer/OBS/index.html` in a browser — it links to both
  pages and shows an animated preview of each of the three styles.
