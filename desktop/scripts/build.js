// Builds the pieces of the desktop app (works on Linux and Windows):
//   node scripts/build.js frontend   Angular build -> desktop/renderer/
//   node scripts/build.js backend    PyInstaller   -> desktop/dist-backend/supermarket-backend/
//   node scripts/build.js all        both
// "npm run dist" runs "all" and then electron-builder (installer in desktop/dist/)

const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const DESKTOP = path.resolve(__dirname, '..');
const ROOT = path.resolve(DESKTOP, '..');
const FRONTEND = path.join(ROOT, 'frontend');
const BACKEND = path.join(ROOT, 'backend');
const isWindows = process.platform === 'win32';

function run(command, args, cwd) {
  console.log(`\n> ${command} ${args.join(' ')}  (${path.relative(ROOT, cwd) || '.'})`);
  // shell on Windows so "npx" (npx.cmd) is found
  const result = spawnSync(command, args, { cwd, stdio: 'inherit', shell: isWindows });
  if (result.status !== 0) {
    console.error(`\nFailed: ${command} ${args.join(' ')}`);
    process.exit(result.status ?? 1);
  }
}

function buildFrontend() {
  // relative base so index.html finds its js / css when it's opened from file://.
  // "./index.html" and not "./": the hash urls become index.html#/products, with "./"
  // they become renderer/#/products and reloading the window (Ctrl+R) shows a folder
  run('npx', ['ng', 'build', '--base-href', './index.html'], FRONTEND);

  const source = path.join(FRONTEND, 'dist', 'supermarket-scrappers', 'browser');
  const target = path.join(DESKTOP, 'renderer');
  fs.rmSync(target, { recursive: true, force: true });
  fs.cpSync(source, target, { recursive: true });
  console.log(`Frontend copied to ${path.relative(ROOT, target)}`);
}

function buildBackend() {
  const python = isWindows
    ? path.join(BACKEND, '.venv', 'Scripts', 'python.exe')
    : path.join(BACKEND, '.venv', 'bin', 'python');
  if (!fs.existsSync(python)) {
    console.error(`Python venv not found: ${python}\nCreate it in backend/ (python -m venv .venv) and install requirements.txt + pyinstaller`);
    process.exit(1);
  }

  run(python, [
    '-m', 'PyInstaller', 'supermarket-backend.spec',
    '--noconfirm',
    '--distpath', path.join(DESKTOP, 'dist-backend'),
    '--workpath', path.join(BACKEND, 'build'),
  ], BACKEND);
}

const step = process.argv[2] ?? 'all';
if (!['frontend', 'backend', 'all'].includes(step)) {
  console.error('Usage: node scripts/build.js [frontend|backend|all]');
  process.exit(1);
}
if (step === 'frontend' || step === 'all') buildFrontend();
if (step === 'backend' || step === 'all') buildBackend();
