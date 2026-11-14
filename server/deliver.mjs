/* Optional outbox delivery. The receiver must deduplicate on record.id. */
import { readdir, readFile, writeFile, rename } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dir = resolve(process.env.DATA_DIRECTORY || resolve(root, 'data'));
const address = process.env.WEBHOOK_URL;
if (!address || new URL(address).protocol !== 'https:') throw new Error('Set WEBHOOK_URL to your HTTPS CRM/backend receiver.');
const names = await readdir(dir).catch(error => { if (error.code === 'ENOENT') return []; throw error; });
let failed = 0, delivered = 0;
for (const name of names.filter(name => /^[a-f0-9]{64}\.json$/.test(name))) {
  const path = resolve(dir, name);
  const record = JSON.parse(await readFile(path, 'utf8'));
  if (record.delivery.status === 'delivered') continue;
  record.delivery.attempts++;
  try {
    const headers = { 'Content-Type': 'application/json', 'X-Idempotency-Key': record.id };
    if (process.env.WEBHOOK_BEARER_TOKEN) headers.Authorization = `Bearer ${process.env.WEBHOOK_BEARER_TOKEN}`;
    const response = await fetch(address, { method: 'POST', headers, redirect: 'error', signal: AbortSignal.timeout(15000), body: JSON.stringify({ id: record.id, kind: record.kind, status: record.status, createdAt: record.createdAt, data: record.data }) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    record.delivery = { ...record.delivery, status: 'delivered', deliveredAt: new Date().toISOString() };
    delivered++;
  } catch (error) {
    record.delivery.status = 'pending'; record.delivery.lastFailureAt = new Date().toISOString();
    failed++;
    // Do not log credentials, payloads, names or email addresses.
    console.error(`Delivery pending for ${record.id}: ${error.name}`);
  }
  const temp = `${path}.${randomUUID()}.tmp`;
  await writeFile(temp, JSON.stringify(record, null, 2) + '\n', { mode: 0o600 });
  await rename(temp, path);
}
console.log(`${delivered} delivered; ${failed} pending.`);
if (failed) process.exitCode = 1;
