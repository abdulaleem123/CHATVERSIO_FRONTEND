import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, stdio: 'inherit' });
  if (result.error || result.status !== 0) throw result.error || new Error(`${command} failed (${result.status})`);
}
const python = process.env.PYTHON || (process.platform === 'win32' ? 'py' : 'python3');
const prefix = !process.env.PYTHON && process.platform === 'win32' ? ['-3'] : [];
run(python, [...prefix, 'build.py']);
run(python, [...prefix, 'scripts/export-components.py']);
if (!process.argv.includes('--pages-only')) {
  const require = createRequire(import.meta.url);
  const { build } = require('esbuild');
  await build({ entryPoints: [resolve(root, 'scene/hero.js')], bundle: true, minify: true, format: 'esm', target: 'es2022', outfile: resolve(root, 'dist/hero-3d.js') });
}
run(process.execPath, ['scripts/check.mjs']);
