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
6. Click OK. The source will look empty/black for now — that's expected,
   it's waiting for the control panel.
7. Position it in your scene: it always renders at the **bottom-left** of
   its own 1920×1080 box, so if your Browser Source is full-canvas, the
   overlay will sit at the bottom of the stream. Resize/reposition the
   *source* in OBS if you want it somewhere else.
8. **No Chroma Key filter needed** — skip this step entirely for Plan 3, the
   background is genuinely transparent.

### Controlling it during the stream

1. Open `/Users/ohnedan/Developer/OBS/OBS_InforR-Lower/panel.html` in a
   regular browser window (Chrome, Safari, whatever you normally use) — on
   the same computer running OBS, or on your second monitor. This is your
   control panel; it never appears on stream itself.
2. For each question, fill in:
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
