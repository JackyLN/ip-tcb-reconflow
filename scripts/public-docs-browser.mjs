/* Read-only anonymous docs QA. Safe to run against the public deployment. */
import { chromium, expect } from '@playwright/test';
import { mkdirSync } from 'node:fs';
const base = (process.env.DOCS_BASE_URL || 'http://localhost:8080').replace(/\/$/, '');
const browser = await chromium.launch();
const page = await browser.newPage({viewport: {width: 1440, height: 1080}});
const errors = [];
const foreignRequests = [];
const chunks = [];
page.on('pageerror', error => errors.push(error.message));
page.on('console', message => {
  if (message.type() === 'error') errors.push(message.text());
});
page.on('request', request => {
  if (request.url().startsWith('http') && new URL(request.url()).origin !== new URL(base).origin) {
    foreignRequests.push(request.url());
  }
  if (request.url().includes('/docs-chunks/')) chunks.push(request.url());
});
mkdirSync('artifacts', {recursive: true});
try {
  const response = await page.goto(base + '/docs/');
  expect(response.status()).toBe(200);
  await expect(page.getByRole('heading', {name: 'ReconFlow handbook', exact: true})).toBeVisible();
  expect(chunks.length).toBe(0); // Mermaid loads only when the document contains a diagram.
  await page.screenshot({path: 'artifacts/public-docs-desktop.png', fullPage: true});
  await page.getByLabel('Find a document').fill('architecture');
  await page.locator('#docs-search-results').getByRole('link', {name: 'Architecture', exact: true}).click();
  await expect(page.locator('.docs-diagram[data-rendered="true"]')).toHaveCount(2, {timeout: 30000});
  await expect(page.locator('.docs-diagram svg')).toHaveCount(2);
  await page.locator('.docs-toc').getByRole('link', {name: 'Runtime boundaries', exact: true}).click();
  expect(page.url()).toContain('#runtime-boundaries');
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({path: 'artifacts/public-docs-architecture.png', fullPage: true});
  await page.locator('.docs-sidebar').getByRole('link', {name: 'ADR 004: GPT-5.4 mini for demo investigations', exact: true}).click();
  await expect(page.locator('.markdown-body h1')).toContainText('ADR 004');
  await page.locator('.docs-pager a').last().click();
  await expect(page.locator('.markdown-body h1')).toHaveText('ADR 005: Controlled findings and a separate investigation contract');
  await page.locator('.docs-pager a').last().click();
  await expect(page.locator('.markdown-body h1')).toHaveText('Advisory AI');
  await page.goto(base + '/docs/authoring/');
  await expect(page.locator('.docs-diagram[data-rendered="true"]')).toHaveCount(1, {timeout: 30000});
  await expect(page.locator('.footnotes')).toBeVisible();
  await expect(page.locator('table')).toBeVisible();
  await page.setViewportSize({width: 390, height: 844});
  await page.goto(base + '/docs/');
  await expect(page.getByLabel('Find a document')).toBeHidden();
  await page.locator('.docs-menu > summary').click();
  await expect(page.getByLabel('Find a document')).toBeVisible();
  await page.locator('.docs-sidebar').getByRole('link', {name: 'Architecture', exact: true}).click();
  await expect(page.locator('.docs-diagram[data-rendered="true"]')).toHaveCount(2, {timeout: 30000});
  await page.screenshot({path: 'artifacts/public-docs-mobile.png', fullPage: true});
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  const noJS = await browser.newContext({javaScriptEnabled: false});
  const fallback = await noJS.newPage();
  await fallback.goto(base + '/docs/engineering/');
  await expect(fallback.locator('code.language-mermaid')).toHaveCount(2);
  await noJS.close();
  await page.setViewportSize({width:1440, height:1080});
  await page.goto(base + '/docs/product/recorded-demo/');
  const videos=page.locator('video');
  await expect(videos).toHaveCount(2);
  for (let index=0; index<2; index++) {
    const video=videos.nth(index);
    await video.scrollIntoViewIfNeeded();
    await expect(video).toBeVisible();
    await expect.poll(()=>video.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(1);
    const duration=await video.evaluate(v=>v.duration);
    expect(duration).toBeGreaterThan(index===0 ? 86 : 150);
    expect(duration).toBeLessThan(index===0 ? 89 : 300);
    await video.evaluate(v=>v.play());
    await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(0);
    await video.evaluate(v=>{v.pause();v.currentTime=v.duration/2;});
    await expect.poll(()=>video.evaluate(v=>!v.seeking && v.readyState>=2)).toBe(true);
  }
  await page.screenshot({path:'artifacts/public-demo-video-desktop.png', fullPage:true});
  await page.setViewportSize({width:390, height:844});
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.screenshot({path:'artifacts/public-demo-video-mobile.png', fullPage:true});
  expect(errors).toEqual([]);
  expect(foreignRequests).toEqual([]);
  console.log('PASS: anonymous public docs, title search, nested/adjacent links, TOC, 3 diagram types, rich Markdown, both video playback/seeking, mobile/no-JS reading, no page/CSP errors or external asset requests');
} finally {
  await browser.close();
}
