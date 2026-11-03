'use strict';

const http = require('node:http');
const { EventEmitter } = require('node:events');

function sendJson(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}

async function readJson(req) {
  let body = '';
  for await (const chunk of req) {
    body += chunk.toString();
    if (body.length > 10_000) {
      const err = new Error('Request is too large');
      err.status = 413;
      throw err;
    }
  }
  try {
    return JSON.parse(body || '{}');
  } catch {
    const err = new Error('Invalid JSON');
    err.status = 400;
    throw err;
  }
}

// Each server has its own in-memory data. This is a teaching demo, NOT a database.
function createApp({ logger = console.log } = {}) {
  const events = new EventEmitter();
  events.on('listing.created', (item) => logger(`EVENT listing.created id=${item.id}`));
  events.on('listing.reserved', (item) => logger(`EVENT listing.reserved id=${item.id}`));

  let nextId = 2;
  const listings = [{
    id: 1,
    title: 'Surplus bread',
    quantity: 8,
    pickupLocation: 'Campus Cafe',
    status: 'available'
  }];

  const handler = async (req, res) => {
    const path = new URL(req.url, 'http://localhost').pathname;

    if (req.method === 'GET' && path === '/') {
      return sendJson(res, 200, { app: 'LocalLoop demo', version: '1.0.0' });
    }
    if (req.method === 'GET' && path === '/health') {
      return sendJson(res, 200, { status: 'ok', service: 'localloop-api' });
    }
    if (req.method === 'GET' && path === '/api/listings') {
      return sendJson(res, 200, listings);
    }
    if (req.method === 'GET' && path === '/api/stats') {
      return sendJson(res, 200, {
        total: listings.length,
        available: listings.filter((item) => item.status === 'available').length,
        reserved: listings.filter((item) => item.status === 'reserved').length
      });
    }
    if (req.method === 'POST' && path === '/api/listings') {
      try {
        const data = await readJson(req);
        if (typeof data.title !== 'string' || !data.title.trim() ||
            !Number.isInteger(data.quantity) || data.quantity <= 0 ||
            typeof data.pickupLocation !== 'string' || !data.pickupLocation.trim()) {
          return sendJson(res, 400, {
            error: 'title, positive integer quantity and pickupLocation are required'
          });
        }
        const item = {
          id: nextId++,
          title: data.title.trim(),
          quantity: data.quantity,
          pickupLocation: data.pickupLocation.trim(),
          status: 'available'
        };
        listings.push(item);
        events.emit('listing.created', item);
        return sendJson(res, 201, item);
      } catch (err) {
        return sendJson(res, err.status || 500, { error: err.message });
      }
    }

    const match = path.match(/^\/api\/listings\/(\d+)\/reserve$/);
    if (req.method === 'POST' && match) {
      const item = listings.find((listing) => listing.id === Number(match[1]));
      if (!item) return sendJson(res, 404, { error: 'Listing not found' });
      if (item.status !== 'available') {
        return sendJson(res, 409, { error: 'Listing already reserved' });
      }
      item.status = 'reserved';
      events.emit('listing.reserved', item);
      return sendJson(res, 200, item);
    }

    return sendJson(res, 404, { error: 'Route not found' });
  };

  return http.createServer((req, res) => {
    handler(req, res).catch((err) => {
      logger(`ERROR ${err.message}`);
      if (!res.headersSent) sendJson(res, 500, { error: 'Internal server error' });
      else res.end();
    });
  });
}

module.exports = { createApp };
