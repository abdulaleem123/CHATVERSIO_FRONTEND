import http from 'node:http';
import { createReadStream } from 'node:fs';
import { mkdir, readFile, realpath, rename, stat, writeFile } from 'node:fs/promises';
import { resolve, dirname, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';
import { RequestError, validate } from './validation.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff': 'font/woff', '.woff2': 'font/woff2', '.mp3': 'audio/mpeg', '.mp4': 'video/mp4', '.webm': 'video/webm', '.vtt': 'text/vtt', '.glb': 'model/gltf-binary', '.txt': 'text/plain; charset=utf-8' };
function json(res, code, data) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(data));
}
async function readJSON(req) {
  if (!/^application\/json(?:;|$)/i.test(req.headers['content-type'] || '')) throw new RequestError('Send application/json.', 415);
  let size = 0;
  const chunks = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 20000) throw new RequestError('Request too large.', 413);
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { throw new RequestError('Invalid JSON.', 400); }
}
export function createApp(options = {}) {
  const publicDir = resolve(options.publicDir || resolve(ROOT, 'dist'));
  const dataDir = resolve(options.dataDir || process.env.DATA_DIRECTORY || resolve(ROOT, 'data'));
  if (dataDir === publicDir || dataDir.startsWith(publicDir + sep)) throw new Error('DATA_DIRECTORY must be outside the public dist folder.');
  const allowedOrigin = options.allowedOrigin ?? process.env.ALLOWED_ORIGIN ?? '';
  const maxRequests = options.maxRequests ?? 10;
  const buckets = new Map();
  const inFlight = new Map();
  function rateLimit(req) {
    const key = req.socket.remoteAddress;
    const now = Date.now();
    for (const [ip, bucket] of buckets) if (bucket.until < now) buckets.delete(ip);
    const bucket = buckets.get(key) || { count: 0, until: now + 60000 };
    bucket.count++; buckets.set(key, bucket);
    if (bucket.count > maxRequests) throw new RequestError('Too many requests. Please wait a minute and retry.', 429);
  }
  async function save(kind, data, key) {
    await mkdir(dataDir, { recursive: true, mode: 0o700 });
    const file = resolve(dataDir, createHash('sha256').update(`${kind}:${key}`).digest('hex') + '.json');
    const fingerprint = createHash('sha256').update(JSON.stringify(data)).digest('hex');
    try {
      const existing = JSON.parse(await readFile(file, 'utf8'));
      if (existing.fingerprint !== fingerprint) throw new RequestError('This request key was already used for different details.', 409);
      return existing;
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
    const record = { id: randomUUID(), kind, status: kind === 'booking' ? 'requested' : 'received', createdAt: new Date().toISOString(), fingerprint, data, delivery: { status: 'pending', attempts: 0 } };
    const temp = `${file}.${randomUUID()}.tmp`;
    await writeFile(temp, JSON.stringify(record, null, 2) + '\n', { mode: 0o600 });
    await rename(temp, file);
    return record;
  }
  return http.createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    try {
      const url = new URL(req.url, 'http://localhost');
      if (url.pathname.startsWith('/api/')) {
        const kind = { '/api/contact': 'enquiry', '/api/schedule': 'booking', '/api/enquiries': 'enquiry', '/api/booking-requests': 'booking' }[url.pathname];
        if (!kind) throw new RequestError('Not found.', 404);
        if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); throw new RequestError('Use POST.', 405); }
        const origin = req.headers.origin;
        const expected = allowedOrigin || `http://${req.headers.host}`;
        if (origin && origin !== expected) throw new RequestError('Origin not allowed.', 403);
        rateLimit(req);
        const key = req.headers['x-idempotency-key'];
        if (typeof key !== 'string' || !/^[a-zA-Z0-9_-]{16,100}$/.test(key)) throw new RequestError('A valid X-Idempotency-Key is required.', 400);
        const data = validate(kind, await readJSON(req));
        const lock = `${kind}:${key}`;
        // Serialize identical keys so simultaneous retries cannot create duplicate records.
        const previous = inFlight.get(lock) || Promise.resolve();
        const operation = previous.catch(() => {}).then(() => save(kind, data, key));
        inFlight.set(lock, operation);
        let record;
        try { record = await operation; } finally { if (inFlight.get(lock) === operation) inFlight.delete(lock); }
        json(res, 201, { ok: true, id: record.id, status: record.status });
        return;
      }
      if (!['GET', 'HEAD'].includes(req.method)) throw new RequestError('Method not allowed.', 405);
      let pathname;
      try { pathname = decodeURIComponent(url.pathname); } catch { throw new RequestError('Invalid path.', 400); }
      if (pathname.includes('\0') || pathname.split('/').some(part => part.startsWith('.'))) throw new RequestError('Not found.', 404);
      let file = resolve(publicDir, '.' + pathname);
      if (!file.startsWith(publicDir + sep) && file !== publicDir) throw new RequestError('Not found.', 404);
      let info = await stat(file).catch(() => null);
      if (info?.isDirectory()) {
        if (!url.pathname.endsWith('/')) { res.writeHead(308, { Location: url.pathname + '/' + url.search }); res.end(); return; }
        file = resolve(file, 'index.html'); info = await stat(file).catch(() => null);
      }
      if (!info?.isFile()) throw new RequestError('Not found.', 404);
      if (!(await realpath(file)).startsWith((await realpath(publicDir)) + sep)) throw new RequestError('Not found.', 404);
      res.setHeader('Content-Type', MIME[extname(file)] || 'application/octet-stream');
      res.setHeader('Cache-Control', extname(file) === '.html' ? 'no-cache' : 'public, max-age=3600');
      res.setHeader('Accept-Ranges', 'bytes');
      let start = 0, end = info.size - 1, status = 200;
      if (req.headers.range) {
        const match = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
        if (!match || (!match[1] && !match[2])) throw new RequestError('Invalid range.', 416);
        start = match[1] ? Number(match[1]) : Math.max(0, info.size - Number(match[2]));
        end = match[1] && match[2] ? Math.min(Number(match[2]), end) : end;
        if (start > end || start >= info.size) { res.setHeader('Content-Range', `bytes */${info.size}`); throw new RequestError('Invalid range.', 416); }
        status = 206; res.setHeader('Content-Range', `bytes ${start}-${end}/${info.size}`);
      }
      res.writeHead(status, { 'Content-Length': Math.max(0, end - start + 1) });
      if (req.method === 'HEAD' || info.size === 0) { res.end(); return; }
      const stream = createReadStream(file, { start, end });
      stream.on('error', () => res.destroy());
      stream.pipe(res);
    } catch (error) {
      if (res.headersSent) { res.destroy(); return; }
      if (!(error instanceof RequestError)) console.error('Request failed:', error.code || error.name);
      json(res, error.status || 500, { ok: false, error: error.status ? error.message : 'Unable to save your request. Please try again.' });
    }
  });
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const option = name => { const index = process.argv.indexOf(name); return index >= 0 ? process.argv[index + 1] : undefined; };
  const port = Number(option('--port') || process.env.PORT || 3000);
  const host = option('--host') || process.env.HOST || '127.0.0.1';
  createApp().listen(port, host, () => console.log(`Chatversio is ready at http://${host}:${port}`));
}
