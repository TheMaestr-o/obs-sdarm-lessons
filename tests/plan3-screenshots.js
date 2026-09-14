const { chromium } = require('playwright');
const path = require('path');

// Run from anywhere inside the repo checkout: paths are resolved relative to
// this file's location (tests/), not hardcoded to one machine's home folder.
const REPO_ROOT = path.join(__dirname, '..');
const OBS_DIR = path.join(REPO_ROOT, 'OBS_InforR-Lower');
const OUT_DIR = path.join(REPO_ROOT, 'screenshots', 'plan3-styles');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();

  const panel = await context.newPage();
  const result = await context.newPage();

  await result.setViewportSize({ width: 1920, height: 1080 });

  await panel.goto('file://' + path.join(OBS_DIR, 'panel.html'));
  await result.goto('file://' + path.join(OBS_DIR, 'result.html'));

  // Give BroadcastChannel a moment and confirm result.html shows the waiting state first.
  await result.waitForTimeout(300);

  // Screenshot the new descriptive picker UI on panel.html.
  await panel.screenshot({ path: path.join(OUT_DIR, 'plan3-panel-new-picker.png'), fullPage: true });
  console.log('Saved panel screenshot.');

  await panel.fill('#line1', 'Question a');
  await panel.fill('#line2', "What evidence of God's love is given to humanity?");

  // Per-template settle time: css/lower.css durations are 4s (id=1), 3s (id=2),
  // 3.1s (id=5), and each animation's text keyframes only finish landing well past
  // the halfway point (id=1's second line lands at 75% of 4s = 3s in). Wait past
  // each animation's full "in" duration so the screenshot lands in the settled
  // hold phase, not mid-slide.
  const templates = [
    { id: '1', settleMs: 3400 },
    { id: '2', settleMs: 2200 },
    { id: '5', settleMs: 2400 }
  ];
  for (const { id, settleMs } of templates) {
    await panel.check(`input[name="template"][value="${id}"]`);
    await panel.click('#showBtn');

    // Wait for the iframe to appear and load lower.html, then wait past the
    // animation's "in" phase so text is fully visible and settled.
    await result.waitForSelector('#overlayFrame:not([hidden])', { timeout: 5000 });
    await result.waitForTimeout(settleMs);

    const shotPath = path.join(OUT_DIR, `plan3-bottom-id${id}.png`);
    await result.screenshot({ path: shotPath });
    console.log(`Saved ${shotPath}`);

    // Sanity-check: confirm the iframe is bottom-pinned and short (not full-screen).
    const frameBox = await result.evaluate(() => {
      const el = document.getElementById('overlayFrame');
      const rect = el.getBoundingClientRect();
      return {
        top: rect.top,
        bottom: rect.bottom,
        left: rect.left,
        width: rect.width,
        height: rect.height,
        windowInnerHeight: window.innerHeight
      };
    });
    console.log(`id=${id} iframe box:`, JSON.stringify(frameBox));

    // Also check the inner lower.html document to see where the actual .animation
    // content is positioned within the frame, and whether it renders any child nodes.
    const frame = result.frames().find(f => f.url().includes('lower.html'));
    if (frame) {
      const animBox = await frame.evaluate(() => {
        const el = document.querySelector('.animation');
        if (!el) return null;
        const rect = el.getBoundingClientRect();
        const text = el.innerText || el.textContent || '';
        return { top: rect.top, bottom: rect.bottom, height: rect.height, text: text.trim().slice(0, 120) };
      });
      console.log(`id=${id} .animation box inside iframe:`, JSON.stringify(animBox));
    } else {
      console.log(`id=${id} WARNING: could not find lower.html frame`);
    }
  }

  await browser.close();
  console.log('Done.');
})().catch(err => {
  console.error(err);
  process.exit(1);
});
