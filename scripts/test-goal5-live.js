#!/usr/bin/env node
/* Goal 5 live contract: control lease, epoch fencing, human socket input, replay rejection, and cancellation. */
const assert = require('node:assert/strict')
const { io } = require(require('node:path').resolve(__dirname, '../sources/maxun/node_modules/socket.io-client'))

const base = (process.env.MAXUN_BASE_URL || 'http://127.0.0.1:18082/api').replace(/\/$/, '')
const apiKey = process.env.MAXUN_API_KEY
if (!apiKey) throw new Error('MAXUN_API_KEY is required in the invoking environment')
const fixtureUrl = process.env.GOAL5_FIXTURE_URL || 'http://127.0.0.1:4173/page1.html'
const handoffUrl = process.env.GOAL5_HANDOFF_URL || 'http://127.0.0.1:4173/handoff.html'
const slowUrl = process.env.GOAL5_SLOW_URL || 'http://127.0.0.1:4173/slow.html'
const ownerSessionId = `goal5-live-${Date.now()}`
const foreignSessionId = `${ownerSessionId}-foreign`
const secretSentinel = 'goal5-human-secret-sentinel'
const evidence = {
  goal: 5,
  ownerSessionId,
  criteria: {
    serverControlOwnership: false,
    epochFence: false,
    cancellationBridge: false,
    pauseResumeAbortPath: false,
    assistVsRecord: false,
    freshObservation: false,
    slowRace: false,
    credentialBoundary: false,
  },
  control: { agentEpoch: 0, humanEpoch: 0, returnedAgentEpoch: 0, foreignRejected: false, staleRejected: false, replayRejected: false },
  commands: { humanAssist: false, handoffNavigated: false, recordedEdit: false, humanSecretApplied: false, humanSecretPersisted: false, cancellationStatus: null },
  telemetry: { rawTextInEvidence: false, rawTextInControlResult: false, rrwebContainsSecret: false },
}
let browserSessionId
let resourceEpoch
let socket
let controlSocket

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

async function request(path, init = {}, expected = []) {
  const headers = new Headers(init.headers)
  headers.set('x-api-key', apiKey)
  if (init.body !== undefined) headers.set('content-type', 'application/json')
  const response = await fetch(`${base}${path}`, { ...init, headers })
  if (!response.ok && !expected.includes(response.status)) {
    let detail = `${response.status}`
    try { const body = await response.json(); detail += ` ${body.code || body.error || ''}` } catch {}
    throw new Error(`${init.method || 'GET'} ${path}: ${detail}`)
  }
  return response
}

async function json(path, init = {}, expected = []) {
  const response = await request(path, init, expected)
  if (response.status === 204) return undefined
  return await response.json()
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

async function connect(token, url, label) {
  const candidate = io(`${url.replace(/\/$/, '')}/${encodeURIComponent(browserSessionId)}`, {
    auth: { token }, transports: ['websocket', 'polling'], reconnection: false, timeout: 8000,
  })
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`${label} connect timeout`)), 10000)
    candidate.once('connect', () => { clearTimeout(timer); resolve() })
    candidate.once('connect_error', error => { clearTimeout(timer); reject(error) })
  })
  return candidate
}

async function controlAcquire(actor) {
  const response = await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/control/acquire`, {
    method: 'POST', body: JSON.stringify({ ownerSessionId, actor }),
  })
  return response.data
}

async function controlCommand(body, expected = []) {
  return json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/control/command`, {
    method: 'POST', body: JSON.stringify(body),
  }, expected)
}

;(async () => {
  try {
    const created = await json('/sdk/browser-sessions', { method: 'POST', body: JSON.stringify({ ownerSessionId }) })
    browserSessionId = created.data.browserSessionId
    resourceEpoch = created.data.epoch

    const stream = await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/stream-capability`, {
      method: 'POST', body: JSON.stringify({ ownerSessionId, epoch: resourceEpoch }),
    })
    socket = await connect(stream.data.capability, stream.data.streamUrl, 'stream')
    await waitForEvent(socket, 'rrweb-event', 60000, event => event?.type === 2)

    const readyDeadline = Date.now() + 60000
    while (Date.now() < readyDeadline) {
      const health = (await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}?ownerSessionId=${encodeURIComponent(ownerSessionId)}`)).data
      if (health.status === 'ready') break
      await sleep(400)
    }

    const agent = await controlAcquire('agent')
    evidence.control.agentEpoch = agent.controlEpoch
    assert.equal(agent.actor, 'agent')
    evidence.criteria.serverControlOwnership = true

    const foreign = await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/control/acquire`, {
      method: 'POST', body: JSON.stringify({ ownerSessionId: foreignSessionId, actor: 'human' }),
    }, [409])
    assert.equal(foreign.code, 'claim_conflict')
    evidence.control.foreignRejected = true

    const human = await controlAcquire('human')
    evidence.control.humanEpoch = human.controlEpoch
    assert.equal(human.controlEpoch, agent.controlEpoch + 1)
    evidence.criteria.epochFence = true

    controlSocket = await connect(human.capability, human.streamUrl, 'control')
    const rrwebEvents = []
    socket.on('rrweb-event', event => rrwebEvents.push(event))
    const humanAssistPromise = waitForEvent(controlSocket, 'control-result', 15000, result => result?.commandId === 'human-assist')
    controlSocket.emit('control-command', { commandId: 'human-assist', kind: 'refresh', mode: 'assist' })
    const humanAssist = await humanAssistPromise
    assert.equal(humanAssist.success, true)
    evidence.commands.humanAssist = true

    const handoffPromise = waitForEvent(controlSocket, 'control-result', 15000, result => result?.commandId === 'human-handoff-page')
    controlSocket.emit('control-command', { commandId: 'human-handoff-page', kind: 'navigate', mode: 'assist', url: handoffUrl })
    const handoffResult = await handoffPromise
    assert.equal(handoffResult.success, true)
    evidence.commands.handoffNavigated = true

    const focusPromise = waitForEvent(controlSocket, 'control-result', 15000, result => result?.commandId === 'human-focus-password')
    controlSocket.emit('control-command', { commandId: 'human-focus-password', kind: 'click', mode: 'assist', coordinates: { x: 100, y: 145 } })
    assert.equal((await focusPromise).success, true)

    const secretPromise = waitForEvent(controlSocket, 'control-result', 15000, result => result?.commandId === 'human-secret')
    controlSocket.emit('control-command', { commandId: 'human-secret', kind: 'type', mode: 'assist', text: secretSentinel })
    const secretResult = await secretPromise
    assert.equal(secretResult.success, true)
    evidence.commands.humanSecretApplied = true
    evidence.commands.humanSecretPersisted = JSON.stringify(secretResult).includes(secretSentinel)
    evidence.telemetry.rawTextInControlResult = evidence.commands.humanSecretPersisted
    await sleep(700)
    evidence.telemetry.rrwebContainsSecret = JSON.stringify(rrwebEvents).includes(secretSentinel)
    assert.equal(evidence.telemetry.rrwebContainsSecret, false)

    const recordedPromise = waitForEvent(controlSocket, 'control-result', 15000, result => result?.commandId === 'human-recorded')
    controlSocket.emit('control-command', { commandId: 'human-recorded', kind: 'navigate', mode: 'record', url: fixtureUrl })
    const recorded = await recordedPromise
    assert.equal(recorded.success, true)
    assert.equal(recorded.data.recorded, true)
    evidence.commands.recordedEdit = true
    evidence.criteria.assistVsRecord = true

    const returned = await controlAcquire('agent')
    evidence.control.returnedAgentEpoch = returned.controlEpoch
    assert.equal(returned.controlEpoch, human.controlEpoch + 1)
    evidence.criteria.freshObservation = Number.isInteger(returned.controlEpoch) && typeof returned.currentUrl === 'string'

    const stale = await controlCommand({ ownerSessionId, actor: 'agent', controlEpoch: human.controlEpoch, commandId: 'stale-after-return', kind: 'refresh', mode: 'assist' }, [409])
    assert.equal(stale.code, 'stale_control')
    evidence.control.staleRejected = true

    const current = await controlCommand({ ownerSessionId, actor: 'agent', controlEpoch: returned.controlEpoch, commandId: 'replay-me', kind: 'refresh', mode: 'assist' })
    assert.equal(current.data.applied, true)
    const replay = await controlCommand({ ownerSessionId, actor: 'agent', controlEpoch: returned.controlEpoch, commandId: 'replay-me', kind: 'refresh', mode: 'assist' }, [409])
    assert.equal(replay.code, 'command_replay')
    evidence.control.replayRejected = true
    for (const [index, kind] of ['pause', 'resume', 'abort'].entries()) {
      const semantic = await controlCommand({ ownerSessionId, actor: 'agent', controlEpoch: returned.controlEpoch, commandId: `interpreter-${index}`, kind, mode: 'assist' })
      assert.equal(semantic.data.applied, true)
    }
    evidence.criteria.pauseResumeAbortPath = true

    const slowAbort = new AbortController()
    const slowRequest = fetch(`${base}/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/control/command`, {
      method: 'POST',
      headers: { 'x-api-key': apiKey, 'content-type': 'application/json' },
      body: JSON.stringify({ ownerSessionId, actor: 'agent', controlEpoch: returned.controlEpoch, commandId: 'slow-cancel', kind: 'navigate', mode: 'assist', url: slowUrl }),
      signal: slowAbort.signal,
    }).catch(error => error)
    setTimeout(() => slowAbort.abort(), 150)
    const slowOutcome = await slowRequest
    assert.equal(slowOutcome?.name, 'AbortError')
    const cancelAck = await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/control/command/slow-cancel/cancel`, {
      method: 'POST', body: JSON.stringify({ ownerSessionId, actor: 'agent', controlEpoch: returned.controlEpoch }),
    })
    assert.equal(cancelAck.data.cancelled, true)
    await sleep(4500)
    const cancelledStatus = await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/control/command/slow-cancel?ownerSessionId=${encodeURIComponent(ownerSessionId)}&actor=agent&controlEpoch=${returned.controlEpoch}`)
    assert.equal(cancelledStatus.data.status, 'unknown')
    evidence.commands.cancellationStatus = cancelledStatus.data.status
    evidence.criteria.cancellationBridge = true
    evidence.criteria.slowRace = true

    const serialized = JSON.stringify(evidence)
    assert.equal(serialized.includes(secretSentinel), false)
    evidence.criteria.credentialBoundary = !evidence.commands.humanSecretPersisted && !evidence.telemetry.rrwebContainsSecret
    evidence.telemetry.rawTextInEvidence = serialized.includes(secretSentinel)
    assert.equal(evidence.telemetry.rawTextInEvidence, false)
    assert.equal(evidence.telemetry.rawTextInControlResult, false)
    assert.equal(Object.values(evidence.criteria).every(Boolean), true)
    console.log(JSON.stringify(evidence, null, 2))
  } finally {
    controlSocket?.disconnect()
    socket?.disconnect()
    if (browserSessionId) {
      await json(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}/control/release`, {
        method: 'POST', body: JSON.stringify({ ownerSessionId, actor: 'agent', controlEpoch: evidence.control.returnedAgentEpoch || 1 }),
      }, [400, 409, 404]).catch(() => undefined)
      await request(`/sdk/browser-sessions/${encodeURIComponent(browserSessionId)}`, {
        method: 'DELETE', body: JSON.stringify({ ownerSessionId, epoch: resourceEpoch }),
      }, [400, 404, 409]).catch(() => undefined)
    }
  }
})().catch(error => {
  console.error(error instanceof Error ? error.stack || error.message : error)
  process.exitCode = 1
})
