const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron')
const { autoUpdater } = require('electron-updater')
const keytar = require('electron-keytar')
const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')
const http = require('http')

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PORT = 8765
const KEYTAR_SERVICE = 'ForgeChamber'
const API_KEY_NAMES = [
  'LIVEKIT_URL',
  'LIVEKIT_API_KEY',
  'LIVEKIT_API_SECRET',
  'ANTHROPIC_API_KEY',
  'DEEPGRAM_API_KEY',
  'CARTESIA_API_KEY',
]

const DATA_DIR = path.join(app.getPath('userData'), 'ForgeChamber')
const LOG_DIR = path.join(DATA_DIR, 'logs')

const SIDECAR_PATH = app.isPackaged
  ? path.join(process.resourcesPath, 'backend', 'forge_chamber.exe')
  : path.join(__dirname, '..', 'backend', 'dist', 'forge_chamber.exe')

const RENDERER_URL = process.env.RENDERER_URL
  || (app.isPackaged
    ? `file://${path.join(__dirname, '..', 'frontend', 'dist', 'index.html')}`
    : 'http://localhost:5173')

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let mainWindow = null
let sidecarProcess = null
let sidecarRestartCount = 0
let isQuitting = false
let logStream = null

// ---------------------------------------------------------------------------
// Filesystem helpers
// ---------------------------------------------------------------------------

function ensureDataDir() {
  fs.mkdirSync(DATA_DIR, { recursive: true })
  fs.mkdirSync(LOG_DIR, { recursive: true })
}

function openLogStream() {
  const logPath = path.join(LOG_DIR, 'sidecar.log')
  logStream = fs.createWriteStream(logPath, { flags: 'a' })
  logStream.write(`\n--- Sidecar started at ${new Date().toISOString()} ---\n`)
}

// ---------------------------------------------------------------------------
// Sidecar management
// ---------------------------------------------------------------------------

function startSidecar() {
  openLogStream()

  sidecarProcess = spawn(SIDECAR_PATH, [], {
    env: {
      ...process.env,
      FORGE_DATA_DIR: DATA_DIR,
      FORGE_PORT: String(PORT),
    },
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  })

  sidecarProcess.stdout.on('data', (data) => {
    if (logStream) logStream.write(data)
  })

  sidecarProcess.stderr.on('data', (data) => {
    if (logStream) logStream.write(data)
  })

  sidecarProcess.on('exit', (code, signal) => {
    if (logStream) {
      logStream.write(`\n--- Sidecar exited: code=${code} signal=${signal} ---\n`)
      logStream.end()
      logStream = null
    }
    sidecarProcess = null

    if (isQuitting) return

    // Auto-restart once on unexpected exit
    if (sidecarRestartCount < 1) {
      sidecarRestartCount++
      console.log('Sidecar exited unexpectedly, restarting...')
      startSidecar()
      waitForSidecar()
        .then(() => {
          if (mainWindow) mainWindow.webContents.send('sidecar-restarted')
        })
        .catch(() => {
          if (mainWindow) mainWindow.webContents.send('sidecar-failed')
        })
    } else {
      console.error('Sidecar failed twice, not restarting.')
      if (mainWindow) mainWindow.webContents.send('sidecar-failed')
    }
  })
}

function waitForSidecar(retries = 30) {
  return new Promise((resolve, reject) => {
    const check = (n) => {
      http.get(`http://127.0.0.1:${PORT}/health`, (res) => {
        if (res.statusCode === 200) {
          res.resume()
          resolve()
        } else {
          res.resume()
          if (n > 0) setTimeout(() => check(n - 1), 500)
          else reject(new Error('Sidecar returned non-200'))
        }
      }).on('error', () => {
        if (n > 0) setTimeout(() => check(n - 1), 500)
        else reject(new Error('Sidecar not responding'))
      })
    }
    check(retries)
  })
}

function killSidecar() {
  if (sidecarProcess) {
    sidecarProcess.kill()
    sidecarProcess = null
  }
}

// ---------------------------------------------------------------------------
// Window creation
// ---------------------------------------------------------------------------

function createWindow() {
  Menu.setApplicationMenu(null)

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    show: false,
    icon: path.join(__dirname, 'assets', process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// ---------------------------------------------------------------------------
// Startup sequence
// ---------------------------------------------------------------------------

async function startup() {
  ensureDataDir()
  createWindow()

  // Show splash screen immediately
  mainWindow.loadFile(path.join(__dirname, 'splash.html'))
  mainWindow.show()

  // Start and wait for sidecar
  try {
    startSidecar()
    await waitForSidecar()
    sidecarRestartCount = 0
  } catch (err) {
    console.error('Sidecar startup failed:', err.message)
    // Show error in splash — renderer will handle it
  }

  // Load the renderer
  if (RENDERER_URL.startsWith('file://')) {
    mainWindow.loadFile(RENDERER_URL.replace('file://', ''))
  } else {
    mainWindow.loadURL(RENDERER_URL)
  }
}

// ---------------------------------------------------------------------------
// IPC handlers — File system
// ---------------------------------------------------------------------------

ipcMain.handle('pick-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Documents', extensions: ['pdf', 'docx', 'txt', 'md'] },
    ],
  })
  return result.canceled ? [] : result.filePaths
})

ipcMain.handle('read-file', async (_event, filePath) => {
  return fs.readFileSync(filePath)
})

ipcMain.handle('get-data-dir', () => {
  return DATA_DIR
})

// ---------------------------------------------------------------------------
// IPC handlers — API key storage (keytar)
// ---------------------------------------------------------------------------

ipcMain.handle('save-api-keys', async (_event, keys) => {
  for (const name of API_KEY_NAMES) {
    if (keys[name] !== undefined) {
      await keytar.setPassword(KEYTAR_SERVICE, name, keys[name])
    }
  }
})

ipcMain.handle('get-api-keys', async () => {
  const keys = {}
  for (const name of API_KEY_NAMES) {
    keys[name] = await keytar.getPassword(KEYTAR_SERVICE, name) || ''
  }
  return keys
})

ipcMain.handle('has-api-keys', async () => {
  const anthropicKey = await keytar.getPassword(KEYTAR_SERVICE, 'ANTHROPIC_API_KEY')
  return !!anthropicKey
})

// ---------------------------------------------------------------------------
// IPC handlers — App updates
// ---------------------------------------------------------------------------

ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall()
})

// ---------------------------------------------------------------------------
// IPC handlers — Sidecar port
// ---------------------------------------------------------------------------

ipcMain.handle('get-sidecar-port', () => {
  return PORT
})

// ---------------------------------------------------------------------------
// Auto-updater configuration
// ---------------------------------------------------------------------------

function setupAutoUpdater() {
  if (!app.isPackaged) return

  autoUpdater.autoDownload = true
  autoUpdater.autoInstallOnAppQuit = true

  autoUpdater.on('update-downloaded', () => {
    if (mainWindow) {
      mainWindow.webContents.send('update-ready')
    }
  })

  autoUpdater.on('error', (err) => {
    console.error('Auto-updater error:', err.message)
  })

  // Check for updates 10 seconds after ready
  setTimeout(() => {
    autoUpdater.checkForUpdates().catch((err) => {
      console.error('Update check failed:', err.message)
    })
  }, 10_000)
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.on('ready', async () => {
  await startup()
  setupAutoUpdater()
})

app.on('before-quit', () => {
  isQuitting = true
  killSidecar()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    startup()
  }
})
