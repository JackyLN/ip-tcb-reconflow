/* Read-only production results walkthrough. No jobs, model calls, imports or decisions. */
import { chromium, expect } from '@playwright/test';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
if (process.env.RECORD_EVAL_DEMO !== '1') throw Error('Set RECORD_EVAL_DEMO=1 to record a read-only walkthrough.');
const base=(process.env.DEMO_BASE_URL || 'https://tcb.jackylenghia.com').replace(/\/$/,'');
const output=process.env.DEMO_OUTPUT || 'artifacts/controlled-v2-pilot-20261108/video';
const evaluationId=Number(process.env.DEMO_EVALUATION_ID || 4);
const line=readFileSync(process.env.DEMO_CREDENTIALS || 'artifacts/vps-demo-credentials.txt','utf8').split('\n').find(l=>l.startsWith('analyst@reconflow.demo'));
if(!line)throw Error('Private analyst credential missing');
const [email,password]=line.trim().split(/\s+/);mkdirSync(output,{recursive:true});
const browser=await chromium.launch({slowMo:150});
const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:output,size:{width:1440,height:1000}}});
// Only recording annotations are injected; all application content is real server output.
await context.addInitScript(()=>document.addEventListener('DOMContentLoaded',()=>{
 const banner=document.createElement('aside');banner.id='recording-caption';
 Object.assign(banner.style,{position:'fixed',bottom:'0',left:'0',right:'0',zIndex:'99999',padding:'16px 28px',color:'#fff',background:'#191919',borderTop:'4px solid #ed1c24',font:'16px/1.5 system-ui',pointerEvents:'none'});
 banner.textContent=sessionStorage.getItem('recording-caption') || 'RECORDED RESULTS REVIEW · Synthetic data · No model calls during recording';document.body.append(banner);document.body.style.paddingBottom='100px';
}));
await context.route('**/*',async route=>{
 const request=route.request();
 if(!['GET','HEAD'].includes(request.method())) return route.abort('blockedbyclient');
 return route.continue();
});
const page=await context.newPage();const video=page.video();const started=Date.now();const stages=[];const errors=[];
page.on('pageerror',e=>errors.push(e.message));
const result={base,recorded_at:new Date().toISOString(),data:'SYNTHETIC',evaluation_id:evaluationId,model_calls_during_recording:0,financial_mutations:0};
async function caption(title,detail,delay=9000){
 const text=`${title}  |  ${detail}`;
 await page.evaluate(text=>{
   sessionStorage.setItem('recording-caption',text);
   let banner=document.querySelector('#recording-caption');
   if(!banner){
     banner=document.createElement('aside');banner.id='recording-caption';
     Object.assign(banner.style,{position:'fixed',bottom:'0',left:'0',right:'0',zIndex:'99999',padding:'16px 28px',color:'#fff',background:'#191919',borderTop:'4px solid #ed1c24',font:'16px/1.5 system-ui',pointerEvents:'none'});
     document.body.append(banner);document.body.style.paddingBottom='100px';
   }
   banner.textContent=text;
 },text);
 stages.push({seconds:Math.round((Date.now()-started)/1000),title,detail,url:page.url()});console.log(title);await page.waitForTimeout(delay);
}
let run;
async function showCase(id){
 const all=run.locator(':scope > details').filter({has:page.locator('summary').filter({hasText:'All cases, original outputs, rule facts and tool traces'})}).first();
 if(!(await all.getAttribute('open')!==null))await all.locator(':scope > summary').click();
 const row=all.locator(':scope > details').filter({has:page.locator('summary').filter({hasText:new RegExp(`^${id} ·`)})}).first();
 if((await row.getAttribute('open'))===null)await row.locator(':scope > summary').click();
 const pre=row.locator('pre');await pre.scrollIntoViewIfNeeded();
 await pre.evaluate(el=>{const lines=el.textContent.split('\n');const index=lines.findIndex(line=>line.trim().startsWith('"raw_output":'));el.scrollTop=Math.max(0,index-2)*parseFloat(getComputedStyle(el).lineHeight);});
 return row;
}
try{
 await page.goto(base+'/login');const csrf=await page.locator('[name="csrf_value"]').inputValue();
 // API login stays outside the recorded DOM and never prints the password.
 expect((await context.request.post(base+'/login',{form:{email,password,csrf_value:csrf},maxRedirects:0})).status()).toBe(303);
 const measured=await(await context.request.get(`${base}/ai/evaluation/${evaluationId}/export`)).json();
 expect(measured.mode).toBe('V2_LIVE');expect(measured.split).toBe('development');expect(measured.status).toBe('COMPLETED');expect(measured.cases_run).toBe(12);
 result.measured_summary={accepted:measured.model_correct,cases:12,claims_supported:measured.claims_supported,claims_checked:measured.claims_checked,usage:measured.usage,p50_ms:measured.model_p50_ms,p95_ms:measured.model_p95_ms,source_revision:measured.source_revision};
 await page.goto(base+'/');
 await caption('01 · Production workspace','The live pilot finished before this recording. This walkthrough reads actual saved results; it queues no AI jobs.');
 await caption('02 · Grouped navigation','Banking operations, Reporting & assurance, Administration and Resources separate daily work from system tasks.');
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Sources & imports',exact:true}).click();
 await caption('03 · Synthetic intake','Only synthetic or public evidence belongs here. No import is submitted in this results walkthrough.');
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Transactions & payouts',exact:true}).click();
 await caption('04 · Payouts, not one-to-one payments','Payments are aggregated into payouts; Python integer arithmetic establishes financial findings.');
 await page.goto(base+'/exceptions/1');
 await page.getByRole('heading',{name:'Verified financial findings · Controlled v2',exact:true}).scrollIntoViewIfNeeded();
 await caption('05 · Financial evidence first','This stored operational case shows fee, net, currency and timing checks. It is separate from synthetic evaluation fixture IDs.',11000);
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'AI evaluation',exact:true}).click();
 run=page.locator(`#evaluation-${evaluationId}`);await run.scrollIntoViewIfNeeded();
 await expect(run).toContainText('development split');
 await caption('06 · Actual controlled-v2 pilot',`${measured.model_correct}/12 accepted; ${measured.claims_supported}/${measured.claims_checked} closed claims supported. One development example per family; this is not a holdout score.`,11000);
 await caption('07 · Measured usage and latency',`${measured.usage.requests} requests; ${measured.usage.input_tokens}/${measured.usage.output_tokens} input/output tokens; p50/p95 ${measured.model_p50_ms}/${measured.model_p95_ms} ms. Estimated USD ${measured.usage.estimated_usd}.`,11000);
 await run.locator('h3').filter({hasText:'Failure categories'}).scrollIntoViewIfNeeded();
 await caption('08 · No observed pilot failures','No provider, schema, unsupported-claim or policy failure appeared in these 12 cases. This does not establish a zero production failure rate.');
 await showCase(200101);
 await caption('09 · Original fee report','Fixture 200101: expected fee 94,593 USD minor units; observed 94,672; difference 79. The model cites payout and policy evidence.',11000);
 await showCase(200703);
 await caption('10 · Missing evidence means abstain','Fixture 200703 lacks payout.gross. The original model response says INSUFFICIENT_EVIDENCE, abstains and escalates.',11000);
 await showCase(200800);
 await caption('11 · Conflicting records stay visible','Fixture 200800 retains the stored-rule conflict and 731 VND difference. It abstains and escalates instead of choosing a convenient record.',11000);
 await showCase(200901);
 await caption('12 · Simultaneous findings','Fixture 200901 preserves late settlement, a 41-cent fee difference and a 127-cent amount difference; escalation is required.',11000);
 await run.scrollIntoViewIfNeeded();
 await caption('13 · Scope of the result','Both required abstentions and all four required escalations were correct. Six injected-note cases passed; broad prompt-injection safety is unmeasured.');
 const historical=page.locator('#evaluation-2');await historical.scrollIntoViewIfNeeded();
 await caption('14 · Historical benchmark preserved','Raw-v1 remains 18/48 (37.5%). It tests diagnosis from raw evidence; v2 is rule-guided compliance, so the scores are not directly comparable.',11000);
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Review queue',exact:true}).click();
 await caption('15 · Independent human review','Maker-checker remains enforced by the server. This read-only recording submits no recommendation, approval or financial change.');
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Audit trail',exact:true}).click();
 await caption('16 · Durable audit evidence','Evaluation start/completion events are persisted. The original workflow video separately records analyst and supervisor escalation.');
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Worker health',exact:true}).click();
 await caption('17 · Administration stays separate','Worker visibility and controls live outside banking tasks. No service control is changed for this recording.');
 await page.goto(base+'/docs/product/recorded-demo/');
 await caption('18 · Reviewer handoff','The earlier workflow video is retained. This results walkthrough, complete pilot JSON and measured report will be added alongside it.',11000);
 await expect(page.locator('h1')).toContainText('Recorded live demo');
 expect(errors).toEqual([]);result.status='completed';
}catch(error){result.status='failed';result.error=error.message;console.error(error.message);process.exitCode=1;}
finally{result.stages=stages;result.duration_seconds=Math.round((Date.now()-started)/1000);writeFileSync(`${output}/result.json`,JSON.stringify(result,null,2));await context.close();await video.saveAs(`${output}/walkthrough.webm`);await browser.close();console.log(`Saved ${output}/walkthrough.webm`);}
