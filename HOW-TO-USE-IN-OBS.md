# How to use these overlays in real OBS Studio

This is the practical, step-by-step version — not the technical writeups in
each plan's own folder. Pick one plan, follow its steps below.

**Recommended: Plan 3 (`OBS_InforR-Lower/`)** — it's the only one that (a)
holds the question on screen until you manually advance it, (b) needs no
Chroma Key filter at all, and (c) works fully offline. Plans 1 and 2 are
included for comparison but both auto-hide after a few seconds and Plan 2
needs internet for fonts.

---

## Plan 3 — recommended

### One-time setup

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
8. **No Chroma Key filter needed** — skip this step entirely for Plan 3, the
   background is genuinely transparent.

### Controlling it during the stream

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
     Up / Down, Framed Reveal) — click to preview the little animation
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

### Alternative: a permanent dock instead of a Control scene

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

### Quick pre-stream checklist

- [ ] `result.html` added as a Browser Source, sized to your canvas
- [ ] `panel.html` open in a separate window, ready to type into
- [ ] Tested at least one "Show" press to confirm text appears on the OBS
      preview (not just in the browser tab — always check the actual OBS
      output)
- [ ] Confirmed no Chroma Key filter is on the source (it would do nothing
      useful here and could theoretically key out dark parts of your text)

---

## Plan 1 — Animated Lower Thirds (alternative)

Use this if you specifically want the dark-strip-with-logo look. Note: it
**auto-hides after a few seconds** — you'd need to press Show again for
every viewer glance, which is less practical for a lesson question people
should have time to read and discuss.

1. **Sources → (+) → Browser**, Local file, browse to:
   ```
   /Users/ohnedan/Developer/OBS/OBS_Animated-Lower-Thirds/lower thirds/browser-source.html
   ```
   1920×1080, same as above.
2. Open `control-panel.html` (same folder) in a browser window as your
   control panel.
3. **Switch on the top "Main settings" toggle first** — this is easy to
   miss, and without it every slot stays forced off no matter what else you
   do.
4. Type your question into slot 1's Name/Info fields, switch that slot's
   toggle on — it appears on stream.
5. No Chroma Key needed here either — this plan already renders on a
   transparent page.

## Plan 2 — Ultimate OBS Lower Thirds System (alternative)

Needs internet during the stream (pulls jQuery and fonts from a CDN) — skip
this one if your connection isn't reliable.

1. **Sources → (+) → Browser**, Local file, browse to:
   ```
   /Users/ohnedan/Developer/OBS/OBS_LowerThirds/obs_lower_thirds_source.html
   ```
2. Open `obs_control_panel.html` (same folder) as your control panel.
3. Fill in slot 1's Name/Title fields, click its **Show** button.
4. This one auto-hides on its own timer too — same caveat as Plan 1.

---

## If something looks wrong

- **Nothing shows up at all**: open the same `result.html` /
  `browser-source.html` / `obs_lower_thirds_source.html` file directly in a
  normal browser tab (not through OBS) and check if it works there first —
  if it doesn't, the panel and result windows probably aren't talking to
  each other (both need to stay open, and for Plan 1 specifically, remember
  the Main settings toggle from step 3 above).
- **Text is there but looks different from these instructions' screenshots**:
  OBS renders Browser Sources through its own engine, which can differ
  slightly from a regular browser in fonts/spacing — this is normal, not a
  bug. Judge it by the actual OBS preview, not by how it looks in a browser
  tab.
- **Want to see all three plans side by side first**: open
  `/Users/ohnedan/Developer/OBS/index.html` in a browser — it links to every
  plan with the same setup steps and screenshots of what each one looks
  like.
