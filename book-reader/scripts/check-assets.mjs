import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = path.resolve(import.meta.dirname, '..');
const sourceFiles = [
  path.join(root, 'index.html'),
  path.join(root, 'src', 'reader-app.jsx'),
  path.join(root, 'src', 'reader.css'),
];

const source = (
  await Promise.all(sourceFiles.map((file) => readFile(file, 'utf8')))
).join('\n');

const assetDirectories = ['pages', 'media', 'fonts'];
const publicAssets = [];

for (const directory of assetDirectories) {
  const entries = await readdir(path.join(root, 'public', directory), {
    withFileTypes: true,
  });

  for (const entry of entries) {
    if (entry.isFile()) {
      publicAssets.push(`${directory}/${entry.name}`);
    }
  }
}

const referencedAssets = new Set(
  [...source.matchAll(/(?:pages|media|fonts)\/[^'"`)\s]+/g)].map((match) => match[0]),
);

const missing = [...referencedAssets].filter(
  (asset) => !publicAssets.includes(asset),
);
const unused = publicAssets.filter((asset) => !referencedAssets.has(asset));

if (missing.length || unused.length) {
  if (missing.length) {
    console.error(`Missing public assets:\n${missing.join('\n')}`);
  }
  if (unused.length) {
    console.error(`Unused public assets:\n${unused.join('\n')}`);
  }
  process.exit(1);
}

console.log(`Asset check passed: ${publicAssets.length} referenced files.`);
