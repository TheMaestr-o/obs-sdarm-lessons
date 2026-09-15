// Capture 4 screenshots for two OBS Lower Thirds plugin plans:
//  - Plan 1 (Animated Lower Thirds): control-panel.html + browser-source.html
//  - Plan 2 (Ultimate OBS Lower Thirds): obs_control_panel.html + obs_lower_thirds_source.html
//
// Question used for the test (lesson "Любовь Божья к человеку", question а):
//   line1 = "Вопрос а"
//   line2 = "Какое свидетельство о Божьей любви дано человечеству?"

const { chromium } = require('playwright');
const path = require('path');

// Run from anywhere inside the repo checkout: paths are resolved relative to
// this file's location (tests/), not hardcoded to one machine's home folder.
const REPO_ROOT = path.join(__dirname, '..');
const OUT_DIR = path.join(REPO_ROOT, 'screenshots');
const LINE1 = 'Question a';
const LINE2 = "What evidence of God's love is given to humanity?";

const PLAN1_DIR = path.join(REPO_ROOT, 'OBS_Animated-Lower-Thirds', 'lower thirds');
const PLAN1_PANEL = path.join(PLAN1_DIR, 'control-panel.html');
const PLAN1_SOURCE = path.join(PLAN1_DIR, 'browser-source.html');

const PLAN2_DIR = path.join(REPO_ROOT, 'OBS_LowerThirds');
const PLAN2_PANEL = path.join(PLAN2_DIR, 'obs_control_panel.html');
const PLAN2_SOURCE = path.join(PLAN2_DIR, 'obs_lower_thirds_source.html');

function toFileUrl(p) {
  // Encode each path segment but keep the slashes, so spaces in folder names
  // become %20 while the path structure stays intact.
  const parts = p.split('/').map((seg) => encodeURIComponent(seg));
  return 'file://' + parts.join('/');
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function capturePlan1(browser) {
  console.log('\n=== PLAN 1: Animated Lower Thirds ===');
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });

  // Order matters: open the source (browser-source.html) FIRST so its
  // BroadcastChannel subscriber is registered before the panel sends anything.
  const sourcePage = await context.newPage();
  console.log('Opening source page:', PLAN1_SOURCE);
  await sourcePage.goto(toFileUrl(PLAN1_SOURCE), { waitUntil: 'load' });
  await sleep(800);

  const panelPage = await context.newPage();
  console.log('Opening panel page:', PLAN1_PANEL);
  await panelPage.goto(toFileUrl(PLAN1_PANEL), { waitUntil: 'load' });
  await sleep(2000);

  console.log('Filling panel fields and sending...');
  await panelPage.evaluate(
    ({ line1, line2 }) => {
      $('#lower-thirds-masterswitch').prop('checked', true).change();
      $('#alt-1-name').val(line1).change();
      $('#alt-1-info').val(line2).change();
      $('#lower-thirds-switch1').prop('checked', true).change();
      if (typeof function_send === 'function') function_send();
    },
    { line1: LINE1, line2: LINE2 }
  );

  // Give the panel UI a moment to visually reflect the changes before we
  // screenshot it (checkbox animations, field focus rings settling, etc).
  await sleep(500);

  console.log('Screenshotting panel (fullPage)...');
  await panelPage.screenshot({
    path: path.join(OUT_DIR, 'plan1-panel-config.png'),
    fullPage: true,
  });

  // Wait for the slide-in text animation on the source page to finish.
  console.log('Waiting for lower-third animation on source page...');
  await sleep(4000);

  console.log('Screenshotting source/result page...');
  await sourcePage.screenshot({
    path: path.join(OUT_DIR, 'plan1-result.png'),
  });

  await context.close();
  console.log('Plan 1 done.');
}

async function capturePlan2(browser) {
  console.log('\n=== PLAN 2: Ultimate OBS Lower Thirds ===');
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });

  const sourcePage = await context.newPage();
  console.log('Opening source page:', PLAN2_SOURCE);
  await sourcePage.goto(toFileUrl(PLAN2_SOURCE), { waitUntil: 'load' });
  await sleep(1500);

  const panelPage = await context.newPage();
  console.log('Opening panel page:', PLAN2_PANEL);
  await panelPage.goto(toFileUrl(PLAN2_PANEL), { waitUntil: 'load' });
  await sleep(1500);

  console.log('Disabling typewriter effect, filling fields...');
  await panelPage.evaluate(() => {
    const tw = document.getElementById('typewriter-1');
    if (tw) tw.checked = false;
  });
  await panelPage.fill('#name-1', LINE1);
  await panelPage.fill('#info-1', LINE2);

  console.log('Screenshotting panel (fullPage) BEFORE show, to capture configured state...');
  // Screenshot the panel now: fields are filled, typewriter disabled — this
  // is the "configured" state. We take it before clicking Show so the panel
  // screenshot doesn't race the source's auto-hide timer.
  await panelPage.screenshot({
    path: path.join(OUT_DIR, 'plan2-panel-config.png'),
    fullPage: true,
  });

  console.log('Clicking Show...');
  await panelPage.locator('.btn-show').first().click();

  // Exactly ~3s: long enough for the reveal, short enough to beat auto-hide.
  await sleep(3000);

  console.log('Screenshotting source/result page...');
  await sourcePage.screenshot({
    path: path.join(OUT_DIR, 'plan2-result.png'),
  });

  await context.close();
  console.log('Plan 2 done.');
}

(async () => {
  const browser = await chromium.launch();
  try {
    await capturePlan1(browser);
    await capturePlan2(browser);
  } finally {
    await browser.close();
  }
  console.log('\nAll screenshots captured in', OUT_DIR);
})().catch((err) => {
  console.error('FATAL:', err);
  process.exit(1);
});
