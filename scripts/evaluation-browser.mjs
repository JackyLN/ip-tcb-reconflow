/* Read-only evaluation verification; never queues inference. */
import {chromium, expect} from '@playwright/test';
import {readFileSync, mkdirSync} from 'node:fs';
const base = process.env.EVAL_BASE_URL || 'https://tcb.jackylenghia.com';
const credentials = readFileSync(process.env.EVAL_CREDENTIALS || 'artifacts/vps-demo-credentials.txt', 'utf8');
const line = credentials.split('\n').find(line => line.startsWith('analyst@reconflow.demo'));
if (!line) throw Error('Private analyst credential missing');
const [email,password] = line.trim().split(/\s+/);
const browser = await chromium.launch();
const context = await browser.newContext({viewport:{width:1440,height:1080}});
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(error.message));
try {
  await page.goto(base + '/login');
  const token = await page.locator('[name="csrf_value"]').inputValue();
  const login = await context.request.post(base + '/login', {form:{csrf_value:token,email,password},maxRedirects:0});
  expect(login.status()).toBe(303);
  await page.goto(base + '/ai/evaluation');
  const run = page.locator('.evaluation-run').filter({has:page.locator('h2').filter({hasText:/· LIVE$/})}).first();
  await expect(run).toBeVisible();
  const href = await run.getByRole('link',{name:'Download evaluation JSON',exact:true}).getAttribute('href');
  const exported = await context.request.get(base + href);
  expect(exported.status()).toBe(200);
  const result = await exported.json();
  expect(result.status).toBe('COMPLETED');
  expect(result.cases_run).toBe(48);
  expect(result.cases.length).toBe(48);
  await expect(run).toContainText(`${result.model_correct}/48`);
  expect(await run.locator('.evaluation-failure').count()).toBe(result.failures.length);
  mkdirSync('artifacts', {recursive:true});
  await page.screenshot({path:'artifacts/holdout-dashboard-summary.png'});
  await page.screenshot({path:'artifacts/holdout-dashboard-desktop.png',fullPage:true});
  if (result.failures.length) {
    await run.locator('.evaluation-failure summary').first().click();
    await run.locator('.evaluation-failure').first().scrollIntoViewIfNeeded();
    await page.screenshot({path:'artifacts/holdout-dashboard-failure.png'});
  }
  await page.setViewportSize({width:390,height:844});
  await page.goto(base + '/ai/evaluation');
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.screenshot({path:'artifacts/holdout-dashboard-mobile-summary.png'});
  await page.screenshot({path:'artifacts/holdout-dashboard-mobile.png',fullPage:true});
  expect(errors).toEqual([]);
  console.log(`PASS: authenticated 48-case LIVE dashboard/export, ${result.failures.length} failures, desktop/mobile without overflow or page errors; no inference queued`);
} finally {
  await browser.close();
}
