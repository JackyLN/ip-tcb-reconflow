/* Read-only controlled-v2 QA. Never creates jobs or calls a model. */
import {chromium,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
const base=process.env.V2_BASE_URL || 'http://localhost:18080';
const line=readFileSync(process.env.V2_CREDENTIALS || 'artifacts/v2-qa.credentials','utf8').split('\n').find(line=>line.startsWith('analyst@reconflow.demo'));
if (!line) throw Error('Private analyst credential missing');
const [email,password]=line.trim().split(/\s+/);
const browser=await chromium.launch();
const context=await browser.newContext({viewport:{width:1440,height:1080}});
const page=await context.newPage();
const errors=[];
page.on('pageerror',error=>errors.push(error.message));
try {
 await page.goto(base+'/login');
 const token=await page.locator('[name="csrf_value"]').inputValue();
 expect((await context.request.post(base+'/login',{form:{csrf_value:token,email,password},maxRedirects:0})).status()).toBe(303);
 await page.goto(base+'/ai/evaluation');
 const run=page.locator('.controlled-evaluation').first();
 await expect(run).toContainText('LIVE V2 QUALITY NOT MEASURED');
 const link=await run.getByRole('link',{name:'Download evaluation JSON',exact:true}).getAttribute('href');
 const result=await (await context.request.get(base+link)).json();
 expect(result.track).toBe('controlled-v2');
 expect(result.offline_contract_valid).toBe(72);
 expect(result.model_accuracy).toBeNull();
 expect(result.usage.requests).toBe(0);
 await expect(page.getByRole('heading',{name:'Human review outcomes',exact:true})).toBeVisible();
 mkdirSync('artifacts',{recursive:true});
 await page.screenshot({path:'artifacts/controlled-dashboard-desktop.png'});
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 await page.screenshot({path:'artifacts/controlled-dashboard-mobile.png'});
 if (process.env.V2_CHECK_CASE === '1') {
   await page.setViewportSize({width:1440,height:1080});
   await page.goto(base+'/exceptions');
   const links=await page.locator('tbody tr').evaluateAll(rows=>rows.filter(row=>row.innerText.includes('FEE_MISMATCH')).map(row=>row.querySelector('a').getAttribute('href')));
   let selected;
   for (const link of links) {
     if ((await (await context.request.get(base+link)).text()).includes('class="panel controlled-report"')) {selected=link;break;}
   }
   if (!selected) throw Error('No recorded v2 synthetic case found');
   await page.goto(base+selected);
   await expect(page.locator('.controlled-report')).toContainText('SIMULATED');
   await expect(page.locator('.controlled-report')).toContainText('CONSISTENT');
   await page.locator('.controlled-report').evaluate(node=>node.scrollIntoView({block:'start'}));
   await page.screenshot({path:'artifacts/controlled-case-desktop.png'});
   await page.setViewportSize({width:390,height:844});
   expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 }
 expect(errors).toEqual([]);
 console.log('PASS: controlled offline dashboard, scoped/no-live metrics, exports, review outcomes, desktop/mobile and optional simulated case; no inference queued');
} finally {await browser.close();}
