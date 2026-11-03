'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { createApp } = require('../src/app');

async function withServer(run) {
  const server = createApp({ logger: () => {} });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  try { await run(base); }
  finally { await new Promise((resolve) => server.close(resolve)); }
}

test('health returns 200', async () => withServer(async (base) => {
  const response = await fetch(`${base}/health`);
  assert.equal(response.status, 200);
  assert.equal((await response.json()).status, 'ok');
}));

test('create -> list -> reserve -> prevent duplicate reservation', async () =>
  withServer(async (base) => {
    const created = await fetch(`${base}/api/listings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'Fruit box', quantity: 4, pickupLocation: 'Library' })
    });
    assert.equal(created.status, 201);
    const item = await created.json();
    assert.equal(item.status, 'available');

    const listed = await (await fetch(`${base}/api/listings`)).json();
    assert.equal(listed.some((entry) => entry.id === item.id), true);

    const reserved = await fetch(`${base}/api/listings/${item.id}/reserve`, { method: 'POST' });
    assert.equal(reserved.status, 200);
    assert.equal((await reserved.json()).status, 'reserved');

    const duplicate = await fetch(`${base}/api/listings/${item.id}/reserve`, { method: 'POST' });
    assert.equal(duplicate.status, 409);
  }));

test('rejects invalid data and missing listings', async () => withServer(async (base) => {
  const invalid = await fetch(`${base}/api/listings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: '', quantity: -5, pickupLocation: '' })
  });
  assert.equal(invalid.status, 400);
  const missing = await fetch(`${base}/api/listings/999/reserve`, { method: 'POST' });
  assert.equal(missing.status, 404);
}));
