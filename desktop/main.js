// Electron main process:
//   1. picks a free port and starts the Flask backend on it
//   2. shows loading.html until the backend answers
//   3. loads the Angular build (renderer/) and gives it the API url (preload.js)
//   4. stops the backend when the app closes

const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('node:child_process');
const net = require('node:net');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const isWindows = process.platform === 'win32';

// how long to wait for the backend (PyInstaller can take a few seconds on the first run)
const BACKEND_TIMEOUT_MS = 30000;

let backend = null;
let mainWindow = null;
let quitting = false;

// Packaged: the PyInstaller executable in resources/backend.
// Development (npm start): main.py with the venv of backend/
function backendCommand() {
  if (app.isPackaged) {
    const dir = path.join(process.resourcesPath, 'backend');
    const exe = isWindows ? 'supermarket-backend.exe' : 'supermarket-backend';
    return { command: path.join(dir, exe), args: [], cwd: dir };
  }
  const python = isWindows
    ? path.join(ROOT, 'backend', '.venv', 'Scripts', 'python.exe')
    : path.join(ROOT, 'backend', '.venv', 'bin', 'python');
  return { command: python, args: ['main.py'], cwd: path.join(ROOT, 'backend') };
}

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
  });
}

function startBackend(port) {
  const { command, args, cwd } = backendCommand();
  backend = spawn(command, args, {
    cwd,
    env: { ...process.env, PORT: String(port), DESKTOP: '1', PYTHONUNBUFFERED: '1' },
    // no console window on Windows
    windowsHide: true,
  });
  backend.stdout.on('data', (data) => process.stdout.write(`[backend] ${data}`));
  backend.stderr.on('data', (data) => process.stderr.write(`[backend] ${data}`));
  return backend;
}

function stopBackend() {
  if (backend && backend.exitCode === null) {
    backend.kill();
  }
  backend = null;
}

// resolves when /api/v1/stores answers, rejects if the backend exits or takes too long
function waitForBackend(apiUrl, child) {
  return new Promise((resolve, reject) => {
    const started = Date.now();
    let done = false;

    child.once('error', (error) => finish(new Error(`No se pudo iniciar el backend: ${error.message}`)));
    child.once('exit', (code) => finish(new Error(`El backend se cerró al iniciar (código ${code})`)));

    function finish(error) {
      if (done) return;
      done = true;
      error ? reject(error) : resolve();
    }

    async function check() {
      if (done) return;
      try {
        const response = await fetch(`${apiUrl}/stores`);
        if (response.ok) return finish();
      } catch {
        // not listening yet
      }
      if (Date.now() - started > BACKEND_TIMEOUT_MS) {
        return finish(new Error('El backend tardó demasiado en iniciar'));
      }
      setTimeout(check, 250);
    }
    check();
  });
}

function createWindow(apiUrl) {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    title: 'Supermarket Scrapper',
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      // preload.js reads it and gives it to Angular as window.desktop.apiUrl
      additionalArguments: [`--api-url=${apiUrl}`],
    },
  });
  mainWindow.once('ready-to-show', () => mainWindow.show());

  // "Ver en tienda" and any other link: open in the user's browser, not inside the app
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:\/\//.test(url)) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith('file://')) {
      event.preventDefault();
      if (/^https?:\/\//.test(url)) {
        shell.openExternal(url);
      }
    }
  });

  return mainWindow;
}

function showError(message) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.loadFile(path.join(__dirname, 'loading.html'), { query: { error: message } });
  }
}

async function start() {
  const port = await getFreePort();
  const apiUrl = `http://127.0.0.1:${port}/api/v1`;

  const window = createWindow(apiUrl);
  await window.loadFile(path.join(__dirname, 'loading.html'));

  const child = startBackend(port);
  child.on('exit', (code) => {
    // the backend died while the app is open: tell the user instead of failing silently
    if (!quitting && mainWindow && !mainWindow.isDestroyed()) {
      showError(`El backend se detuvo (código ${code}). Vuelve a abrir la aplicación.`);
    }
  });

  try {
    await waitForBackend(apiUrl, child);
  } catch (error) {
    showError(error.message);
    return;
  }

  await window.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

// only one copy of the app (each one would start its own backend)
if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  app.whenReady().then(start);

  app.on('before-quit', () => {
    quitting = true;
    stopBackend();
  });
  app.on('window-all-closed', () => app.quit());
}
