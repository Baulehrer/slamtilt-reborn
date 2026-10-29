#!/usr/bin/env node
'use strict';
// Private original fixtures are read locally and never copied into a release.
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {spawnSync} = require('node:child_process');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
function option(name, fallback) { const i = args.indexOf(name); return i < 0 ? fallback : args[i + 1]; }
const html = path.resolve(option('--html', path.join(root, 'build/web-release/native/Slamtilt-Reborn.html')));
const output = path.resolve(option('--output', path.join(root, 'build/web-release/test-browser')));
const assetSource=option('--source','windows');
const fixtures = path.resolve(option('--fixtures', path.join(root, 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT')));
fs.mkdirSync(output, {recursive: true});
const report = {html, asset_source:assetSource, html_sha256: fs.existsSync(html) ? crypto.createHash('sha256').update(fs.readFileSync(html)).digest('hex') : null, original_assets_packaged: false, checks: [], network_requests: [], errors: [], console: [], screenshots: []};
let browser;
const watchdog = setTimeout(() => { report.timed_out = true; if (browser) browser.close(); }, 240000);
watchdog.unref();
function check(name, detail) { report.checks.push({name, passed: true, detail}); fs.writeFileSync(path.join(output, 'progress.json'), JSON.stringify(report, null, 2) + '\n'); console.log('PASS ' + name); }
async function run() {
  if (!fs.existsSync(html)) throw new Error('BLOCKED: HTML build does not exist: ' + html);
  const files = assetSource==='amiga' ? fs.readdirSync(fixtures).filter(n=>/\.adf$/i.test(n)).sort().map(n=>path.join(fixtures,n)) : ['MAIN.DAT', 'MEAN.DAT', 'PIRATE.DAT', 'SPACE.DAT', 'DEMON.DAT'].map(n => path.join(fixtures, n));
  if(assetSource==='amiga' && files.length!==5)throw Error('Select exactly five ADF fixtures');
  for (const f of files) if (!fs.existsSync(f)) throw new Error('Missing private fixture: ' + f);
  const playwright = require(path.join(root, 'build/web-release/test-deps/node_modules/playwright-core'));
  // Vivaldi's first-run window can expose an uninitialized blank page target.
  // Initialize it before Playwright's automatic attachment waits on that target.
  if (option('--cdp', '')) {
    const targets = await (await fetch(option('--cdp', '') + '/json/list')).json();
    const blank = targets.find(t => t.type === 'page' && !t.url);
    if (blank) {
      const socket = new WebSocket(blank.webSocketDebuggerUrl);
      await new Promise((resolve, reject) => {
        socket.onopen = () => socket.send(JSON.stringify({id: 1, method: 'Page.navigate', params: {url: pathToFileURL(html).href}}));
        socket.onerror = reject;
        socket.onmessage = () => { socket.close(); resolve(); };
      });
    }
  }
  browser = option('--cdp', '') ? await playwright.chromium.connectOverCDP(option('--cdp', '')) : await playwright.chromium.launch({executablePath: option('--chromium', '/usr/bin/chromium'), headless: !args.includes('--headed'),
    args: ['--no-sandbox', '--enable-unsafe-swiftshader']});
  const context = option('--cdp', '') ? browser.contexts()[0] : await browser.newContext({viewport: {width: 1280, height: 900}, offline: true});
  await context.setOffline(true);
  await context.route(/^(?:https?|wss?):/i, route => route.abort('internetdisconnected'));
  const page = await context.newPage();
  page.setDefaultTimeout(120000);
  page.on('request', r => { if (/^(https?|wss?):/i.test(r.url())) report.network_requests.push(r.url()); });
  page.on('pageerror', e => report.errors.push(String(e.stack || e)));
  page.on('console', m => { report.console.push({type: m.type(), text: m.text()}); });
  async function ready() {
    await page.waitForFunction(() => window.rebornTest && document.querySelectorAll('#tables button').length === 4);
  }
  async function healthy() {
    const state = await page.evaluate(() => ({status: document.querySelector('#status').textContent,
      error: document.querySelector('#status').classList.contains('error'), stage: getComputedStyle(document.querySelector('#stage')).display,
      available: Array.from({length: 4}, (_, i) => window.rebornTest.api('web_has_table', [i], ['number']))}));
    if (state.error || report.errors.length || report.console.some(x => /(?:Aborted\(|RuntimeError:|unreachable|memory access out of bounds)/i.test(x.text)))
      throw new Error('Runtime failure: ' + JSON.stringify({state, errors: report.errors, console: report.console.slice(-10)}));
    return state;
  }
  await page.goto(pathToFileURL(html).href, {waitUntil: 'load', timeout: 180000});
  await ready();
  const initial = await healthy();
  if (initial.available.some(Boolean)) throw new Error('Fresh browser context unexpectedly contains imported tables');
  check('single-file offline file URL loads', initial.status);
  // Exercise the actual file input onchange handler; do not call importFiles directly.
  await page.locator('input#files').setInputFiles(files);
  await page.waitForFunction(() => [...document.querySelectorAll('#tables button')].length === 4 &&
    [...document.querySelectorAll('#tables button')].every(b => !b.disabled) || document.querySelector('#status').classList.contains('error'));
  let state = await healthy();
  if (state.available.some(v => v !== 1)) throw new Error('Import did not enable all four native tables: ' + JSON.stringify(state));
  const imported = await page.evaluate(() => {
    const j = JSON.parse(Module.FS.readFile('/user/data.json', {encoding: 'utf8'}));
    return {source: j.source, root: j.root, entries: Module.FS.readdir(j.root)};
  });
  if (imported.source !== assetSource || !['mean', 'pirate', 'space', 'demon'].every(id => imported.entries.includes(id)))
    throw new Error('Import manifest missing actual table data: ' + JSON.stringify(imported));
  check(assetSource==='amiga'?'actual file-input imports five ADFs and all four tables':'actual file-input imports all four DAT tables without EXE', imported);
  const previews = await page.evaluate(() => [...document.querySelectorAll('#tables article canvas')].map(canvas => {
    const rgba = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
    const colors = new Set(); for (let i = 0; i < rgba.length; i += 4 * 71) colors.add([rgba[i], rgba[i + 1], rgba[i + 2], rgba[i + 3]].join(','));
    return colors.size;
  }));
  if (previews.length !== 4 || previews.some(n => n < 8)) throw new Error('Missing rendered table previews: ' + previews);
  check('all four previews contain decoded artwork', previews);
  const menuShot = path.join(output, 'menu-imported.png');
  await page.screenshot({path: menuShot}); report.screenshots.push(menuShot);
  const ids = ['mean', 'pirate', 'space', 'demon'];
  const selectedTables = option('--tables', ids.join(',')).split(',');
  report.selected_tables = selectedTables;
  for (let i = 0; i < ids.length; ++i) {
    if (!selectedTables.includes(ids[i])) continue;
    await page.evaluate(async index => { await window.rebornTest.play(index, 40); }, i);
    state = await healthy();
    if (state.stage !== 'none') throw new Error('Table failed to return to menu: ' + ids[i]);
    check('finite native play returns to menu: ' + ids[i], {steps: 40, state});
    const trace = await page.evaluate(() => JSON.parse(Module.FS.readFile('/user/web-last-play.json', {encoding: 'utf8'})));
    fs.writeFileSync(path.join(output, 'native-' + ids[i] + '-40.json'), JSON.stringify(trace) + '\n');
    if ((trace.table && trace.table !== ids[i]) || !(trace.tick_count > 0) || !trace.states?.length || trace.failure || trace.error)
      throw new Error('Finite session lacks real native progress: ' + ids[i] + ' ' + JSON.stringify({table: trace.table, ticks: trace.tick_count, states: trace.states?.length, error: trace.failure || trace.error}));
    check('native trace confirms stepped simulation: ' + ids[i], {ticks: trace.tick_count, states: trace.states.length});
  }
  // Real browser key events and compositor captures exercise interactive play.
  await page.evaluate(() => { window.rebornTest.trace=true; window.__acceptancePlay = window.rebornTest.play(0, 0); });
  await page.locator('#stage').waitFor({state: 'visible'});
  await page.locator('#canvas').focus();
  await page.waitForTimeout(200);
  const canvasSize = await page.locator('#canvas').boundingBox();
  if (!canvasSize || canvasSize.width < 200 || canvasSize.height < 200)
    throw new Error('Collapsed gameplay canvas: ' + JSON.stringify(canvasSize));
  check('gameplay canvas has usable display dimensions', canvasSize);
  const playShots = [0, 1, 2].map(i => path.join(output, 'mean-play-' + i + '.png'));
  await page.locator('#canvas').screenshot({path: playShots[0]});
  await page.keyboard.down('Enter'); await page.waitForTimeout(300); await page.keyboard.up('Enter');
  await page.waitForTimeout(400);
  await page.locator('#canvas').screenshot({path: playShots[1]});
  await page.keyboard.down('ShiftLeft'); await page.waitForTimeout(300); await page.keyboard.up('ShiftLeft');
  await page.keyboard.down('ShiftRight'); await page.waitForTimeout(300); await page.keyboard.up('ShiftRight');
  await page.waitForTimeout(400);
  await page.locator('#canvas').screenshot({path: playShots[2]});
  report.screenshots.push(...playShots);
  const diff = spawnSync('python3', ['-c', `from PIL import Image,ImageChops
import sys,json
images=[Image.open(p).convert('RGB') for p in sys.argv[1:]]
result=[]
for a,b in zip(images,images[1:]):
 d=ImageChops.difference(a,b)
 result.append(sum(any(p) for p in d.getdata()))
print(json.dumps(result))`, ...playShots], {encoding: 'utf8'});
  if (diff.status !== 0) throw new Error('Screenshot comparison failed: ' + diff.stderr);
  const changed = JSON.parse(diff.stdout);
  if (changed.some(n => n < 20)) throw new Error('Interactive canvas did not visibly change: ' + changed);
  check('rendered canvas changes during real Enter and both Shift key inputs', {changed_pixels: changed, caveat: 'Visual change alone does not identify ball state.'});
  await page.keyboard.press('Escape'); await page.waitForTimeout(100);
  const optionShot = path.join(output, 'mean-options.png');
  await page.screenshot({path: optionShot}); report.screenshots.push(optionShot);
  await page.keyboard.press('Escape');
  await page.keyboard.press('F10');
  await page.evaluate(async () => { await window.__acceptancePlay; });
  await healthy();
  check('real interactive session returns with F10', {controls: 'Enter, left/right Shift, Escape, F10'});
  const interactiveTrace = await page.evaluate(() => JSON.parse(Module.FS.readFile('/user/web-last-play.json', {encoding: 'utf8'})));
  fs.writeFileSync(path.join(output, 'native-mean-interactive.json'), JSON.stringify(interactiveTrace) + '\n');
  const xy = interactiveTrace.states.map(state => { const bytes = Uint8Array.from(state.balls[0]); const view = new DataView(bytes.buffer); return [view.getInt32(0, true) / 65536, view.getInt32(4, true) / 65536]; });
  const uniquePositions = new Set(xy.map(p => p.map(v => v.toFixed(2)).join(','))).size;
  const xRange = Math.max(...xy.map(p => p[0])) - Math.min(...xy.map(p => p[0]));
  const yRange = Math.max(...xy.map(p => p[1])) - Math.min(...xy.map(p => p[1]));
  if (uniquePositions < 10 || Math.max(xRange, yRange) < 10) throw new Error('Native ball did not move after real Enter: ' + JSON.stringify({uniquePositions, xRange, yRange}));
  if (!interactiveTrace.ui_frames.some(frame => frame.menu)) throw new Error('Escape did not open native options in trace');
  check('native trace confirms ball movement and Escape options', {unique_positions: uniquePositions, x_range: xRange, y_range: yRange, ticks: interactiveTrace.tick_count});
  await page.evaluate(() => new Promise((resolve, reject) => Module.FS.syncfs(false, e => e ? reject(String(e)) : resolve())));
  await page.reload({waitUntil: 'load'});
  await ready(); state = await healthy();
  if (state.available.some(v => v !== 1)) throw new Error('IDBFS reload lost imported tables: ' + JSON.stringify(state));
  check('IDBFS persistence survives reload', state);
  await page.evaluate(async () => { await window.rebornTest.play(3, 40); });
  await healthy(); check('persisted table plays after reload', 'demon');
  await page.locator('#fullscreen').click();
  await page.waitForFunction(()=>!!document.fullscreenElement);
  await page.evaluate(()=>{window.__fullscreenPlay=window.rebornTest.play(1,0)});
  await page.locator('#stage').waitFor({state:'visible'});
  await page.waitForTimeout(200);
  await page.locator('#game-fullscreen').click();
  await page.waitForFunction(()=>!document.fullscreenElement);
  await page.locator('#game-fullscreen').click();
  await page.waitForFunction(()=>!!document.fullscreenElement);
  await page.keyboard.press('F10');
  await page.evaluate(()=>window.__fullscreenPlay);
  await page.evaluate(async()=>{if(document.fullscreenElement)await document.exitFullscreen()});
  await page.waitForTimeout(200);
  await healthy();
  check('page fullscreen toggles during real Pirate play and exits cleanly', true);
  report.browser={version:browser.version(),jspi:await page.evaluate(()=>typeof WebAssembly.Suspending==='function'&&typeof WebAssembly.promising==='function')};
  if (report.network_requests.length) throw new Error('External network request from single-file build');
  check('zero external network requests while offline', 0);
  report.passed = true;
}
run().catch(e => { report.passed = false; report.failure = String(e.stack || e); process.exitCode = 1; })
  .finally(async () => { clearTimeout(watchdog); if (browser) await browser.close(); fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({passed: report.passed, checks: report.checks.length, report: path.join(output, 'report.json'), failure: report.failure}, null, 2)); });
