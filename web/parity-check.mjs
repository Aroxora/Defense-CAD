/**
 * Parity check: confirm the browser TypeScript engine reproduces the Python source of truth.
 *
 * Bundles web/src/app/engine.ts with esbuild (already a dependency of the Angular toolchain),
 * imports its PARITY dispatch, and compares every case in public/data/parity.json to the
 * value the Python calculators emitted (scripts/export_parity.py).
 *
 * Run from web/:  node parity-check.mjs
 */
import { build } from 'esbuild';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const REL = 1e-6;
const ABS = 1e-9;

const out = join(tmpdir(), `engine-${process.pid}.mjs`);
await build({
  entryPoints: ['src/app/engine.ts'],
  outfile: out,
  bundle: true,
  format: 'esm',
  platform: 'node',
  logLevel: 'error',
});

const { PARITY } = await import(pathToFileURL(out).href);
const { cases } = JSON.parse(readFileSync('public/data/parity.json', 'utf8'));

let failures = 0;
for (const { fn, args, expected } of cases) {
  const f = PARITY[fn];
  if (!f) {
    console.error(`MISSING engine fn: ${fn}`);
    failures++;
    continue;
  }
  const got = f(...args);
  const tol = Math.max(ABS, Math.abs(expected) * REL);
  if (!(Math.abs(got - expected) <= tol)) {
    console.error(`MISMATCH ${fn}(${args.join(', ')}): TS=${got} vs PY=${expected}`);
    failures++;
  }
}

if (failures) {
  console.error(`\nPARITY FAILED: ${failures}/${cases.length} cases`);
  process.exit(1);
}
console.log(`PARITY OK: ${cases.length} cases match Python within ${REL} rel.`);
