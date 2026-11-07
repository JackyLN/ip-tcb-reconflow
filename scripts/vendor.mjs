import {copyFileSync, rmSync} from 'node:fs';
copyFileSync('node_modules/htmx.org/dist/htmx.min.js', 'reconflow/static/htmx.min.js');
copyFileSync('node_modules/chart.js/dist/chart.umd.js', 'reconflow/static/chart.umd.js');

import { build } from 'esbuild';
rmSync('reconflow/static/docs-chunks', {recursive: true, force: true});
await build({
  entryPoints: ['frontend/docs.js'],
  outdir: 'reconflow/static',
  splitting: true,
  chunkNames: 'docs-chunks/[name]-[hash]',
  bundle: true,
  minify: true,
  format: 'esm',
  target: ['es2022'],
  legalComments: 'linked',
});
