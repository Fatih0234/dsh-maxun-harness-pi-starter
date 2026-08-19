#!/usr/bin/env node
/* Measure the pinned rrweb browser bundle's sensitive-input behavior. */
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const { chromium } = require(path.resolve(__dirname, '../sources/maxun/node_modules/playwright-core'))

const rrwebPath = path.resolve(__dirname, '../sources/maxun/node_modules/rrweb/umd/rrweb.min.js')
const rrwebScript = fs.readFileSync(rrwebPath, 'utf8')
const secrets = [
  'password-secret-goal4',
  'ordinary-input-secret-goal4',
  'sensitive-copy-goal4',
  'contenteditable-secret-goal4',
  'iframe-sensitive-secret-goal4',
  'canvas-secret-goal4',
]

;(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome' })
  try {
    const context = await browser.newContext()
    await context.addInitScript({ content: rrwebScript })
    const page = await context.newPage()
    await page.setContent(`<!doctype html><html><body>
      <input id="password" type="password">
      <input id="ordinary" type="text">
      <div id="sensitive" data-sensitive>${secrets[2]}</div>
      <div id="editable" contenteditable="true" data-sensitive>${secrets[3]}</div>
      <div id="editable-public" contenteditable="true">public-editable-goal4</div>
      <iframe id="same-origin-frame" srcdoc="<!doctype html><body><input id='frame-input' type='text'><div data-sensitive>${secrets[4]}</div></body>"></iframe>
      <canvas id="canvas" width="320" height="80"></canvas>
      <div id="public">public-observation-goal4</div>
    </body></html>`)
    await page.waitForFunction(() => document.querySelector('#same-origin-frame')?.contentDocument?.readyState === 'complete')
    await page.evaluate(() => {
      window.__goal4Events = []
      window.__goal4Stop = window.rrweb.record({
        emit: event => window.__goal4Events.push(event),
        maskAllInputs: true,
        maskTextSelector: '[data-sensitive], [data-private], .rr-mask',
        blockSelector: 'iframe',
        recordCanvas: false,
        sampling: { mousemove: false, mouseInteraction: true, scroll: 75, input: 'last' },
        input: true,
      })
    })
    await page.locator('#password').fill(secrets[0])
    await page.locator('#ordinary').fill(secrets[1])
    await page.locator('#editable').fill(secrets[3])
    await page.locator('#editable-public').fill('public-editable-goal4')
    await page.frameLocator('#same-origin-frame').locator('#frame-input').fill(secrets[4])
    await page.evaluate((canvasSecret) => {
      const canvas = document.querySelector('#canvas')
      const context = canvas?.getContext('2d')
      if (!context) throw new Error('canvas context unavailable')
      context.font = '20px sans-serif'
      context.fillText(canvasSecret, 4, 30)
    }, secrets[5])
    await page.waitForTimeout(150)
    const events = await page.evaluate(() => window.__goal4Events)
    const serialized = JSON.stringify(events)
    for (const secret of secrets) assert.equal(serialized.includes(secret), false, `rrweb leaked ${secret}`)
    assert.equal(serialized.includes('public-observation-goal4'), true, 'public text was unexpectedly removed')
    assert.equal(serialized.includes('public-editable-goal4'), true, 'public contenteditable text was unexpectedly removed')
    assert.equal(serialized.includes('*'), true, 'masked rrweb output did not contain masking markers')
    console.log(JSON.stringify({
      rrwebBundle: 'umd/rrweb.min.js',
      eventCount: events.length,
      sensitiveValuesLeaked: false,
      covered: {
        password: true,
        ordinaryInput: true,
        markedSensitiveText: true,
        contenteditable: true,
        iframe: { blocked: true, nestedInputNotLeaked: true },
        canvas: { recordingDisabled: true, bitmapTextNotLeaked: true },
      },
      publicTextPreserved: true,
      maskedOutputObserved: true,
    }, null, 2))
  } finally {
    await browser.close()
  }
})().catch(error => {
  console.error(error)
  process.exitCode = 1
})
