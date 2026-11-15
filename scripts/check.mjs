import assert from 'node:assert/strict';
import { readFile, readdir, stat } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dist = resolve(root, 'dist');
async function walk(folder) {
  const result = [];
  for (const entry of await readdir(folder, { withFileTypes: true })) {
    const path = resolve(folder, entry.name);
    if (entry.isDirectory()) result.push(...await walk(path)); else result.push(path);
  }
  return result;
}
const files = await walk(dist);
const pages = files.filter(file => file.endsWith('/index.html'));
assert.equal(pages.length, 25, 'Expected all 25 pages');
let assetReferences = 0;
for (const file of pages) {
  const html = await readFile(file, 'utf8');
  assert.equal((html.match(/<main\b/g) || []).length, 1);
  assert.equal((html.match(/<footer\b/g) || []).length, 1);
  assert(html.includes('/site-config.js') && html.includes('/integration.js'));
  for (const [, , value] of html.matchAll(/\b(href|src|data-src)="([^"]+)"/g)) {
    if (!value.startsWith('/') || value.startsWith('//')) continue;
    const url = new URL(value.replaceAll('&amp;', '&'), 'http://local');
    const target = resolve(dist, '.' + decodeURIComponent(url.pathname));
    const info = await stat(target).catch(() => null);
    assert(info, `Missing local target ${value} in ${file}`);
    if (info.isDirectory()) assert(await stat(resolve(target, 'index.html')).catch(() => false));
    assetReferences++;
  }
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(ids.length, new Set(ids).size, `Duplicate IDs: ${file}`);
  for (const [, id] of html.matchAll(/href="#([^"]+)"/g)) assert(ids.includes(id), `Missing anchor #${id}`);
}
for (let i=0;i<40;i++) assert(files.includes(resolve(dist, `media/spin/spin-${String(i).padStart(2,'0')}.webp`)));
for (const role of ['chat','sales','voice']) assert(files.includes(resolve(dist, `media/agent-${role}.webp`)));
for (const model of ['speech-frame','headset','messenger','printer']) {
  const bytes = await readFile(resolve(dist, `media/3d/${model}.glb`));
  assert.equal(bytes.toString('utf8', 0, 4), 'glTF');
  assert.equal(bytes.readUInt32LE(8), bytes.length);
}
for (const industry of ['service','property','business','clinic']) for (const scene of [0,1]) assert(files.includes(resolve(dist, `media/sample-${industry}-${scene}.mp3`)));
console.log(`PASS: ${pages.length} pages, ${assetReferences} references, 40 turntable frames, 4 GLB models and 8 voice samples.`);
