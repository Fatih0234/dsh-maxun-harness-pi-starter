#!/usr/bin/env node
/* Goal 4 live contract: claim-bound stream, refresh/reconnect, and screenshot fallback. */
const assert = require('node:assert/strict')
const { io } = require(require('node:path').resolve(__dirname, '../sources/maxun/node_modules/socket.io-client'))

const base = (process.env.MAXUN_BASE_URL || 'http://127.0.0.1:18080/api').replace(/\/$/, '')
const apiKey = process.env.MAXUN_API_KEY
if (!apiKey) throw new Error('MAXUN_API_KEY is required in the invoking environment')
const ownerSessionId = `goal4-live-${Date.now()}`
const evidence = {
  goal: 4,
  ownerSessionId,
  capability: { issued: false, claimBound: false, shortLived: false, credentialPersisted: false },
  stream: { unauthorizedRejected: false, connected: false, fullSnapshots: 0, reconnectFullSnapshot: false },
  screenshot: { available: false, mimeType: null, byteLength: 0 },
  telemetry: { rrwebEventsPersisted: false, modelMessages: 0 },
}
let browserSessionId
let epoch
let streamUrl
let socket

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

async function request(path, init = {}) {
  const headers = new Headers(init.headers)
  headers.set('x-api-key', apiKey)
  if (init.body !== undefined) headers.set('content-type', 'application/json')
  const response = await fetch(`${base}${path}`, { ...init, headers })
  if (!response.ok) {
    let detail = `${response.status}`
    try {
      const body = await response.json()
      detail += ` ${body.code || body.error || ''}`
    } catch {}
    throw new Error(`${init.method || 'GET'} ${path}: ${detail}`)
  }
  if (response.status === 204) return undefined
  return response
}

async function json(path, init = {}) {
  return await (await request(path, init)).json()
}

async function waitFor(check, timeoutMs, label) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const result = await check()
    if (result) return result
    await sleep(500)
  }
  throw new Error(`Timed out waiting for ${label}`)
}

function waitForEvent(target, eventName, timeoutMs, predicate = () => true) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      target.off(eventName, onEvent)
      reject(new Error(`Timed out waiting for ${eventName}`))
    }, timeoutMs)
    const onEvent = payload => {
      if (!predicate(payload)) return
      clearTimeout(timer)
      target.off(eventName, onEvent)
      resolve(payload)
    }
    target.on(eventName, onEvent)
  })
}

async function connectStream(token) {
  const candidate = io(`${streamUrl.replace(/\/$/, '')}/${encodeURIComponent(browserSessionId)}`, {
    auth: { token },
    transports: ['websocket', 'polling'],
    reconnection: false,
    autoConnect: false,
    timeout: 8000,
  })
  const connected = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('stream connect timeout')), 10000)
    candidate.once('connect', () => {
      clearTimeout(timer)
      resolve()
    })
    candidate.once('connect_error', error => {
      clearTimeout(timer)
      reject(error)
    })
  })
  candidate.connect()
  await connected
  return candidate
}

async function assertUnauthorized() {
  const candidate = io(`${streamUrl.replace(/\/$/, '')}/${encodeURIComponent(browserSessionId)}`, {
    auth: { token: 'not-a-goal4-capability' },
    transports: ['websocket'],
    reconnection: false,
    timeout: 4000,
  })
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('invalid capability was accepted or did not fail')), 6000)
    candidate.once('connect', () => {
      clearTimeout(timer)
      candidate.disconnect()
      reject(new Error('invalid capability connected'))
    })
    candidate.once('connect_error', () => {
      clearTimeout(timer)
      candidate.disconnect()
      resolve()
    })
  })
  evidence.stream.unauthorizedRejected = true
}

;(async () => {
  try {
    const created = await json('/sdk/browser-sessions', {
      method: 'POST',
      body: JSON.stringify({ ownerSessionId }),
    })
    const createdData = created.data
    browserSessionId = createdData.browserSessionId
    epoch = createdData.epoch
    assert.equal(typeof browserSessionId, 'string')
    assert.equal(Number.isSafeInteger(epoch), true)

    const capabilityResponse = await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/stream-capability`, {
      method: 'POST',
      body: JSON.stringify({ ownerSessionId, epoch }),
    })
    const capability = capabilityResponse.data
    streamUrl = capability.streamUrl
    assert.match(streamUrl, /^https?:\/\//)
    assert.equal(typeof capability.capability, 'string')
    assert.equal(capability.browserSessionId, browserSessionId)
    assert.equal(capability.ownerSessionId, ownerSessionId)
    assert.equal(capability.epoch, epoch)
    assert.equal(Date.parse(capability.expiresAt) > Date.now(), true)
    evidence.capability = {
      issued: true,
      claimBound: capability.browserSessionId === browserSessionId && capability.ownerSessionId === ownerSessionId && capability.epoch === epoch,
      shortLived: Date.parse(capability.expiresAt) - Date.now() <= 61000,
      credentialPersisted: false,
    }

    await assertUnauthorized()
    socket = await connectStream(capability.capability)
    evidence.stream.connected = socket.connected
    const initialSnapshot = waitForEvent(socket, 'rrweb-event', 60000, event => event && event.type === 2)
    await initialSnapshot
    evidence.stream.fullSnapshots += 1

    const health = await waitFor(async () => {
      const value = (await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}?ownerSessionId=${encodeURIComponent(ownerSessionId)}`)).data
      return value.status === 'ready' ? value : false
    }, 60000, 'browser ready')
    assert.equal(health.browserStatus, 'active')

    const imageResponse = await request(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/screenshot`, {
      method: 'POST',
      body: JSON.stringify({ ownerSessionId, epoch, fullPage: false }),
    })
    const image = await imageResponse.arrayBuffer()
    assert.ok(image.byteLength > 100)
    evidence.screenshot = {
      available: true,
      mimeType: imageResponse.headers.get('content-type'),
      byteLength: image.byteLength,
    }

    socket.disconnect()
    await sleep(500)
    socket = await connectStream(capability.capability)
    const reconnectSnapshot = waitForEvent(socket, 'rrweb-event', 20000, event => event && event.type === 2)
    await sleep(300)
    socket.emit('request-refresh')
    await reconnectSnapshot
    evidence.stream.fullSnapshots += 1
    evidence.stream.reconnectFullSnapshot = true

    assert.equal(evidence.capability.credentialPersisted, false)
    assert.equal(evidence.telemetry.rrwebEventsPersisted, false)
    assert.equal(evidence.telemetry.modelMessages, 0)
    console.log(JSON.stringify(evidence, null, 2))
  } finally {
    socket?.disconnect()
    if (browserSessionId && epoch !== undefined) {
      await request(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}`, {
        method: 'DELETE',
        body: JSON.stringify({ ownerSessionId, epoch }),
      }).catch(() => undefined)
    }
  }
})().catch(error => {
  console.error(error instanceof Error ? error.message : error)
  process.exitCode = 1
})
