const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');

// Regenerates the animated GIF previews and the matching still PNGs for the
// three overlay styles, plus the control-panel screenshot. Paths resolve
// relative to this file (tests/), same as the other scripts here, so this
// works from any checkout.
//
// Needs the project served over HTTP -- the panel fetch()es lessons-data.json,
// which browsers refuse under file://:
//
//   cd OBS_InforR-Lower && python3 -m http.server 8001
//
// GIFs are produced by capturing PNG frames with page.screenshot() on a fixed
// interval and handing them to ffmpeg (palettegen + paletteuse). Playwright's
// own video recording was not used: it records the whole viewport at a size it
// picks, and these previews want a tight 1920x300 crop of the lower third only.

const REPO_ROOT = path.join(__dirname, '..');
const OUT_STYLES = path.join(REPO_ROOT, 'screenshots', 'plan3-styles');
const OUT_ROOT = path.join(REPO_ROOT, 'screenshots');
const BASE = process.env.OBS_BASE_URL || 'http://localhost:8001';

// The overlay page is genuinely transparent (real CSS alpha, no chroma key).
// Screenshotting it as-is photographs white text on a white page. Everything
// below is composited onto this stand-in for a camera feed -- a flat dark
// gradient, deliberately NOT a real video frame, so nothing in these previews
// claims to be footage that was actually broadcast.
const BACKDROP = `
  background: linear-gradient(160deg, #1a1d23 0%, #23262d 45%, #14161a 100%) !important;
`;

// Capture window: the longest entrance is style 1 (last line starts at 2.2s
// and runs 0.8s, so motion ends at 3.0s). 4.6s of capture leaves ~1.6s of the
// held end state on screen -- the point of the project is that it holds, so a
// preview that cut at 3.0s would show exactly the thing this system doesn't do.
const CAPTURE_MS = 4600;
const FPS = 12;

// Only the lower third of a 1920x1080 frame is captured. A full-height shot is
// mostly empty backdrop and renders the text unreadably small in a README.
const CLIP = { x: 0, y: 780, width: 1920, height: 300 };

const LINE1 = '1. БОГ ЕСТЬ ЛЮБОВЬ';
const SHORT_Q = 'а. Какое свидетельство о Божьей любви дано человечеству?';
const LONG_Q = 'б. Каким образом Бог явил Свою любовь к падшему человечеству, и что это означает для каждого из нас сегодня?';

const STYLES = [
  { id: '1', slug: 'slash-and-slide', line2: SHORT_Q },
  // One style gets a deliberately longer question so text wrapping is visible
  // in the docs rather than only ever being shown with a one-line question.
  { id: '2', slug: 'slide-up-down', line2: LONG_Q },
  { id: '3', slug: 'quiet-rule', line2: LONG_Q }
];

function overlayUrl({ id, line2 }) {
  const q = new URLSearchParams({
    id,
    line1: LINE1,
    line2,
    color1: 'ffffff',
    color2: 'c6a15b'
  });
  return `${BASE}/native/overlay.html?${q}`;
}

async function captureStyle(context, style, frameRoot) {
  const frameDir = path.join(frameRoot, style.slug);
  fs.mkdirSync(frameDir, { recursive: true });

  const page = await context.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.setViewportSize({ width: 1920, height: 1080 });

  // Load about:blank first, paint the backdrop, and only then navigate, so the
  // very first captured frame already has the dark background rather than one
  // white flash at the head of every GIF.
  await page.goto(overlayUrl(style), { waitUntil: 'domcontentloaded' });
  await page.addStyleTag({ content: `html, body { ${BACKDROP} }` });

  // Restart every animation from zero at a known moment, so frame 0 of the GIF
  // is frame 0 of the entrance. Without this the first frames land wherever
  // page load happened to leave things.
  await page.evaluate(() => {
    document.querySelectorAll('#overlay-root *').forEach((el) => {
      el.getAnimations().forEach((a) => { a.cancel(); a.play(); });
    });
  });

  const t0 = Date.now();
  const interval = 1000 / FPS;
  let n = 0;
  while (Date.now() - t0 < CAPTURE_MS) {
    await page.screenshot({
      path: path.join(frameDir, `f${String(n).padStart(4, '0')}.png`),
      clip: CLIP
    });
    n += 1;
    const drift = t0 + n * interval - Date.now();
    if (drift > 0) await page.waitForTimeout(drift);
  }

  // The still is taken after everything has settled: the held end state, which
  // is what an operator actually looks at for most of a question.
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(OUT_STYLES, `${style.slug}.png`), clip: CLIP });

  await page.close();
  if (errors.length) console.warn(`  console errors on ${style.slug}:`, errors);
  return { frameDir, frames: n };
}

function framesToGif(frameDir, outPath) {
  const pattern = path.join(frameDir, 'f%04d.png');
  const palette = path.join(frameDir, 'palette.png');
  // Half width (960) keeps the GIFs small enough for a README while the text
  // stays readable; a generated palette avoids the banding a default web
  // palette produces on the gold and the dark gradient.
  const filters = 'scale=960:-1:flags=lanczos';
  // -framerate on the INPUT is what makes the GIF play back at the rate the
  // frames were actually captured. Without it ffmpeg assumes 25fps for an
  // image sequence and the whole preview runs at roughly double speed, which
  // cuts the held end state off the end.
  const inArgs = ['-framerate', String(FPS), '-i', pattern];
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inArgs,
    '-vf', `${filters},palettegen=max_colors=128:stats_mode=diff`, palette]);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inArgs, '-i', palette,
    // new=1 keeps paletteuse honest across the whole clip; without an explicit
    // output -r the held frames at the end get dropped as duplicates and the
    // GIF ends on the last moving frame -- exactly the thing these previews
    // exist to disprove.
    '-lavfi', `${filters}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3`,
    '-r', String(FPS), '-loop', '0', outPath]);
  fs.unlinkSync(palette);
}

async function capturePanel(context) {
  // The panel runs as a narrow dock inside OBS, not at 1920 wide -- shooting it
  // full width would show a layout nobody sees.
  const page = await context.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.setViewportSize({ width: 460, height: 1000 });
  await page.goto(`${BASE}/panel.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);

  // Drive the real pickers so the shot shows a lesson actually loaded and a
  // question selected, rather than the empty first-run state. Russian is
  // selected on purpose: it matches the lesson text used in the style
  // previews, so the docs show one coherent example throughout.
  const picked = await page.evaluate(async () => {
    const fire = (el) => el.dispatchEvent(new Event('change', { bubbles: true }));
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    const select = (sel, match) => {
      const el = document.querySelector(sel);
      if (!el || !el.options.length) return null;
      const opt = match
        ? [...el.options].find((o) => match(o))
        : el.options[el.options.length - 1];
      if (!opt) return null;
      el.value = opt.value;
      fire(el);
      return opt.value;
    };
    const out = {};
    // Latest quarter -- the one an operator would actually be running.
    out.quarter = select('#quarterSelect'); await wait(400);
    out.language = select('#languageSelect', (o) =>
      o.value === 'ru' || /рус|russ/i.test(o.textContent)); await wait(400);
    out.lesson = select('#lessonSelect', (o) => o.value === '1'); await wait(700);
    const rows = document.querySelectorAll('.question-row');
    out.questionCount = rows.length;
    if (rows.length) {
      rows[0].click();
      out.question = rows[0].textContent.trim().slice(0, 50);
    }
    return out;
  });
  console.log('  panel state:', JSON.stringify(picked));
  await page.waitForTimeout(800);

  // Shoot only as tall as the panel's own content: fullPage against a tall
  // viewport leaves a long empty strip under the last control.
  const h = await page.evaluate(() => {
    // Measure to the bottom of the last element that actually paints
    // something. Zero-size wrappers and the full-height background container
    // would otherwise report the whole viewport and reintroduce the empty
    // strip this is meant to trim.
    const bottom = [...document.querySelectorAll('body *')].reduce((m, e) => {
      if (e.offsetParent === null) return m;
      const r = e.getBoundingClientRect();
      if (r.height < 2 || r.width < 2) return m;
      const cs = getComputedStyle(e);
      const paints = cs.borderStyle !== 'none'
        || (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent')
        || (e.textContent || '').trim().length > 0;
      return paints ? Math.max(m, r.bottom) : m;
    }, 0);
    return Math.ceil(bottom + window.scrollY + 14);
  });
  // Clip rather than resize: the panel's own layout reflows when the viewport
  // shrinks (the Settings block is collapsed, so the measured content bottom
  // and the rendered page height disagree), which left a dead strip under the
  // last control. A clip takes exactly the measured region at the dock width
  // the panel is actually used at.
  const clipH = Math.max(600, Math.min(h, 1400));
  await page.screenshot({
    path: path.join(OUT_ROOT, 'panel.png'),
    clip: { x: 0, y: 0, width: 460, height: clipH }
  });
  await page.close();
  if (errors.length) console.warn('  console errors on panel:', errors);
}

(async () => {
  fs.mkdirSync(OUT_STYLES, { recursive: true });
  const frameRoot = fs.mkdtempSync(path.join(require('os').tmpdir(), 'obs-frames-'));
  const browser = await chromium.launch();
  const context = await browser.newContext({ deviceScaleFactor: 1 });

  for (const style of STYLES) {
    console.log(`Capturing ${style.slug} (id=${style.id})...`);
    const { frameDir, frames } = await captureStyle(context, style, frameRoot);
    const gif = path.join(OUT_STYLES, `${style.slug}.gif`);
    framesToGif(frameDir, gif);
    const kb = (fs.statSync(gif).size / 1024).toFixed(0);
    console.log(`  ${frames} frames -> ${path.basename(gif)} (${kb} KB)`);
  }

  console.log('Capturing panel...');
  await capturePanel(context);

  await browser.close();
  fs.rmSync(frameRoot, { recursive: true, force: true });
  console.log('Done.');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
