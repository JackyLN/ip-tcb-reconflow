/* Records real synthetic UI actions. Explicit opt-in: this queues ONE paid investigation. */
import { chromium, expect } from '@playwright/test';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';

if (process.env.RUN_LIVE_DEMO !== '1') throw Error('Set RUN_LIVE_DEMO=1 only with live demo authorization.');
const base = (process.env.DEMO_BASE_URL || 'https://tcb.jackylenghia.com').replace(/\/$/, '');
const output = process.env.DEMO_OUTPUT || 'artifacts/live-demo';
const credentials = Object.fromEntries(readFileSync(process.env.DEMO_CREDENTIALS || 'artifacts/vps-demo-credentials.txt', 'utf8')
  .split('\n').map(line => line.match(/^(\w+@reconflow\.demo)\s+(\S+)$/)).filter(Boolean).map(match => [match[1], match[2]]));
mkdirSync(output, {recursive: true});
const browser = await chromium.launch({slowMo: 200});
const context = await browser.newContext({viewport: {width: 1440, height: 1000}, recordVideo: {dir: output, size: {width: 1440, height: 1000}}});
// A clearly labelled recording annotation; underlying pages/actions/data are the real deployment.
await context.addInitScript(() => {
  document.addEventListener('DOMContentLoaded', () => {
    const banner = document.createElement('aside');
    banner.id = 'recording-caption';
    Object.assign(banner.style, {position:'fixed', bottom:'0', left:'0', right:'0', zIndex:'99999', padding:'16px 28px', color:'#fff', background:'#191919', borderTop:'4px solid #ed1c24', font:'16px/1.5 system-ui', pointerEvents:'none'});
    banner.textContent = sessionStorage.getItem('recording-caption') || 'RECORDED DEMO · Synthetic data · Real browser actions';
    document.body.append(banner);
    document.body.style.paddingBottom = '100px';
  });
});
const page = await context.newPage();
const video = page.video();
const stages = [];
const started = Date.now();
const pause = ms => page.waitForTimeout(ms);
async function caption(title, detail, delay = 3500) {
  const text = `${title}  |  ${detail}`;
  await page.evaluate(text => {
    sessionStorage.setItem('recording-caption', text);
    let banner = document.querySelector('#recording-caption');
    // HTMX replaces the body without another DOMContentLoaded event.
    if (!banner) {
      banner = document.createElement('aside');
      banner.id = 'recording-caption';
      Object.assign(banner.style, {position:'fixed', bottom:'0', left:'0', right:'0', zIndex:'99999', padding:'16px 28px', color:'#fff', background:'#191919', borderTop:'4px solid #ed1c24', font:'16px/1.5 system-ui', pointerEvents:'none'});
      document.body.append(banner);
      document.body.style.paddingBottom = '100px';
    }
    banner.textContent = text;
  }, text);
  stages.push({seconds: Math.round((Date.now() - started) / 1000), title, detail, url: page.url()});
  console.log(title);
  await pause(delay);
}
async function signIn(role) {
  const email = `${role}@reconflow.demo`;
  if (!credentials[email]) throw Error(`Missing private ${role} credential`);
  await page.goto(base + '/login');
  // Password is submitted outside the recorded DOM; no credential appears in the video.
  const csrf = await page.locator('[name="csrf_value"]').inputValue();
  const response = await context.request.post(base + '/login', {form: {csrf_value: csrf, email, password: credentials[email]}, maxRedirects: 0});
  if (response.status() !== 303) throw Error(`Sign-in rejected for ${role}; credentials are never logged`);
  await page.goto(base + '/');
  await expect(page.locator('.identity')).toContainText(email);
}
let result = {base, recorded_at: new Date().toISOString(), data: 'SYNTHETIC', paid_investigations_queued: 0};
try {
  await signIn('analyst');
  await caption('01 · Analyst workspace', 'Synthetic merchant settlements. The configured GPT model is advisory; no money can move.');
  await page.locator('nav').getByRole('link', {name:'Sources & imports', exact:true}).click();
  await page.locator('[name="scenario"]').selectOption('mismatch');
  await page.locator('[name="count"]').selectOption('1000');
  await caption('02 · Load the scenario', '1,000 payments, grouped into payouts. Existing identical source data is safely reused.');
  await page.getByRole('button', {name:'Launch reconciliation', exact:true}).click();
  await page.waitForURL(/\/imports\/\d+$/);
  result.import_url = page.url();
  for (let i=0; i<30 && !(await page.locator('main').innerText()).includes('COMPLETED'); i++) {await pause(1000); await page.reload();}
  await expect(page.locator('main')).toContainText('COMPLETED');
  await caption('03 · Deterministic reconciliation', 'Python calculates payout totals and compares bank credits. Replaying does not double-count.');
  await page.locator('main').getByRole('link', {name:/^Run #/}).click();
  result.run_url = page.url();
  await caption('04 · Inspect the findings', 'Matched, fee, timing, missing-credit and ambiguity findings come from rules, not the LLM.');
  const candidates = await page.locator('tbody tr').evaluateAll(rows => rows.filter(row => row.innerText.includes('FEE_MISMATCH')).map(row => row.querySelector('a').getAttribute('href')));
  let payoutPath, casePath;
  for (const path of candidates) {
    const html = await (await context.request.get(base + path)).text();
    const match = html.match(/href="(\/exceptions\/\d+)"/);
    if (!match) continue;
    const caseHTML = await (await context.request.get(base + match[1])).text();
    if (caseHTML.includes('<span class="badge">OPEN</span>') && !caseHTML.includes('<h2>Investigation #')) {payoutPath=path; casePath=match[1]; break;}
  }
  if (!casePath) throw Error('No uninvestigated OPEN fee case in this run; no paid call was queued.');
  await page.goto(base + payoutPath);
  await caption('05 · Read the payout evidence', 'Inspect currency, expected fee, declared net and candidate bank credit before drawing conclusions.', 5500);
  await page.getByRole('link', {name:/Investigate exception #/}).click();
  result.case_url = page.url();
  result.case_id = Number(casePath.split('/').pop());
  await caption('06 · Evidence before AI', 'Four scoped read-only tools expose the case, payout math, candidate credits and provider policy.', 5000);
  await page.getByRole('button', {name:'Queue bounded AI investigation', exact:true}).click();
  result.paid_investigations_queued = 1;
  await caption('07 · Live GPT investigation', 'Waiting for the real provider response. One investigation; at most four tools and five API requests.', 2000);
  let investigation;
  for (let i=0; i<75; i++) {
    investigation = page.locator('section.panel').filter({has: page.locator('h2').filter({hasText:/^Investigation #/})}).first();
    if (await investigation.count()) break;
    await pause(1000);
    await page.reload();
  }
  await expect(investigation).toBeVisible();
  result.mode = (await investigation.locator('.badge').innerText()).trim();
  result.investigation_title = await investigation.locator('h2').innerText();
  result.investigation_text = await investigation.innerText();
  await investigation.scrollIntoViewIfNeeded();
  await caption('08 · Actual AI result', `Provider result: ${result.mode}. Citations are validated; semantic accuracy still needs human review.`, 8000);
  await page.screenshot({path: `${output}/ai-result.png`, fullPage:true});
  if (result.mode !== 'LIVE') throw Error(`Actual result was ${result.mode}; keep recording as failure evidence and diagnose before another paid run.`);
  await investigation.locator('summary').filter({hasText:'Read-only tool trace'}).click();
  await investigation.locator('details').scrollIntoViewIfNeeded();
  await caption('09 · Inspect the tool trace', 'Only observed evidence IDs can be cited. The model cannot approve, write finance records or execute SQL.', 5000);
  await page.getByLabel('Evidence-based recommendation').fill(`Recorded synthetic demo: fee mismatch reviewed against payout and policy evidence for case #${result.case_id}. The live report is advisory. Independent provider confirmation is not available in this demo; escalate for a provider statement. Do not adjust balances or treat the discrepancy as financially settled.`);
  await caption('10 · Human recommendation', 'The analyst proposes escalation for independent provider evidence; AI submits no resolution itself.');
  await page.getByRole('button', {name:'Submit to independent reviewer', exact:true}).click();
  await caption('11 · Maker-checker boundary', 'The proposal is pending. The analyst cannot approve their own recommendation.');
  await page.getByRole('button', {name:'Sign out', exact:true}).click();
  await signIn('supervisor');
  await caption('12 · Independent supervisor', 'A separate supervisor account reviews the analyst proposal. Login secrets were excluded from the recording.');
  await page.locator('nav').getByRole('link', {name:'Review queue', exact:true}).click();
  const proposal = page.locator('section.panel').filter({has: page.getByRole('link', {name:`Case #${result.case_id}`, exact:true})}).first();
  await proposal.scrollIntoViewIfNeeded();
  await caption('13 · Review the recommendation', 'Evidence is insufficient for closure. Escalation preserves the unresolved discrepancy.', 5000);
  result.proposal_action = await proposal.locator('form').getAttribute('action');
  await proposal.getByRole('button', {name:'Escalate', exact:true}).click();
  await page.goto(base + casePath);
  await expect(page.locator('.case-banner')).toContainText('ESCALATED');
  result.final_state = 'ESCALATED';
  await caption('14 · Recorded outcome', 'Case escalated by an independent supervisor. No balances changed and no payment was executed.', 5000);
  await page.screenshot({path: `${output}/case-outcome.png`, fullPage:true});
  await page.locator('nav').getByRole('link', {name:'Audit trail', exact:true}).click();
  await caption('15 · Audit trail', 'The real application records investigation, analyst proposal and supervisor escalation with distinct actors.', 6500);
  await page.screenshot({path: `${output}/audit.png`, fullPage:true});
  result.status = 'completed';
} catch (error) {
  result.status = 'failed';
  result.error = error.message;
  console.error(error.message);
  process.exitCode = 1;
} finally {
  result.stages = stages;
  result.duration_seconds = Math.round((Date.now() - started) / 1000);
  writeFileSync(`${output}/result.json`, JSON.stringify(result, null, 2));
  await context.close();
  await video.saveAs(`${output}/walkthrough.webm`);
  await browser.close();
  console.log(`Recording saved: ${output}/walkthrough.webm`);
}
