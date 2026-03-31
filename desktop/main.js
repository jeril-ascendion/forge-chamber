const { app, BrowserWindow, ipcMain, dialog, Menu, safeStorage } = require('electron')
const { autoUpdater } = require('electron-updater')
const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')
const http = require('http')

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PORT = 8765
const API_KEY_NAMES = [
  'LIVEKIT_URL',
  'LIVEKIT_API_KEY',
  'LIVEKIT_API_SECRET',
  'GROQ_API_KEY',
  'DEEPGRAM_API_KEY',
  'CARTESIA_API_KEY',
]

const DATA_DIR = path.join(app.getPath('userData'), 'ForgeChamber')
const LOG_DIR = path.join(DATA_DIR, 'logs')

const SIDECAR_PATH = app.isPackaged
  ? path.join(process.resourcesPath, 'backend', 'forge_chamber', 'forge_chamber.exe')
  : path.join(__dirname, '..', 'backend', 'dist', 'forge_chamber', 'forge_chamber.exe')

const RENDERER_URL = process.env.RENDERER_URL
  || (app.isPackaged
    ? `file://${path.join(process.resourcesPath, 'frontend', 'dist', 'index.html')}`
    : 'http://localhost:5173')

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let mainWindow = null
let sidecarProcess = null
let sidecarFailed = false
let isQuitting = false
let logStream = null

// ---------------------------------------------------------------------------
// Filesystem helpers
// ---------------------------------------------------------------------------

function ensureDataDir() {
  fs.mkdirSync(DATA_DIR, { recursive: true })
  fs.mkdirSync(LOG_DIR, { recursive: true })
}

function logToFile(msg) {
  const logPath = path.join(LOG_DIR, 'electron.log')
  fs.appendFileSync(logPath, `${new Date().toISOString()} ${msg}\n`)
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
  logToFile(`Starting sidecar: ${SIDECAR_PATH}`)
  logToFile(`Sidecar exists: ${fs.existsSync(SIDECAR_PATH)}`)

  if (!fs.existsSync(SIDECAR_PATH)) {
    logToFile(`ERROR: Sidecar not found at ${SIDECAR_PATH}`)
    logToFile(`Resources dir contents: ${fs.existsSync(path.dirname(SIDECAR_PATH)) ? fs.readdirSync(path.dirname(SIDECAR_PATH)).join(', ') : 'DIR NOT FOUND'}`)
    sidecarFailed = true
    return
  }

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

  sidecarProcess.on('error', (err) => {
    logToFile(`Sidecar spawn error: ${err.message}`)
    sidecarFailed = true
  })

  sidecarProcess.on('exit', (code, signal) => {
    logToFile(`Sidecar exited: code=${code} signal=${signal}`)
    if (logStream) {
      logStream.write(`\n--- Sidecar exited: code=${code} signal=${signal} ---\n`)
      logStream.end()
      logStream = null
    }
    sidecarProcess = null

    // Do NOT auto-restart — it causes process bombs.
    // Just mark as failed and let the UI handle it.
    if (!isQuitting) {
      sidecarFailed = true
      if (mainWindow) mainWindow.webContents.send('sidecar-failed')
    }
  })
}

function waitForSidecar(retries = 60) {
  return new Promise((resolve, reject) => {
    const check = (n) => {
      if (sidecarFailed) {
        reject(new Error('Sidecar failed to start'))
        return
      }
      http.get(`http://127.0.0.1:${PORT}/health`, (res) => {
        if (res.statusCode === 200) {
          res.resume()
          logToFile('Sidecar health check passed')
          resolve()
        } else {
          res.resume()
          if (n > 0) setTimeout(() => check(n - 1), 500)
          else reject(new Error('Sidecar returned non-200'))
        }
      }).on('error', () => {
        if (n > 0) setTimeout(() => check(n - 1), 500)
        else reject(new Error('Sidecar not responding after 30s'))
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

  logToFile('=== App starting ===')
  logToFile(`isPackaged: ${app.isPackaged}`)
  logToFile(`resourcesPath: ${process.resourcesPath}`)
  logToFile(`SIDECAR_PATH: ${SIDECAR_PATH}`)
  logToFile(`RENDERER_URL: ${RENDERER_URL}`)
  logToFile(`DATA_DIR: ${DATA_DIR}`)

  // Show splash screen immediately
  mainWindow.loadFile(path.join(__dirname, 'splash.html'))
  mainWindow.show()

  // Start and wait for sidecar
  try {
    startSidecar()
    if (!sidecarFailed) {
      await waitForSidecar()
    }
  } catch (err) {
    logToFile(`Sidecar startup failed: ${err.message}`)
  }

  if (sidecarFailed) {
    logToFile('Sidecar failed — showing error page')
    const errorHtml = `data:text/html,
      <html><body style="background:#0F0F14;color:#F0EFE8;font-family:sans-serif;padding:40px;text-align:center">
        <h1 style="color:#E8533A">Sidecar Failed to Start</h1>
        <p>The backend engine could not start.</p>
        <p style="color:#888">Check the log at:<br><code>${LOG_DIR.replace(/\\/g, '/')}</code></p>
        <p style="color:#888;margin-top:20px">Sidecar path: <code>${SIDECAR_PATH.replace(/\\/g, '/')}</code></p>
        <p style="color:#888">Exists: ${fs.existsSync(SIDECAR_PATH)}</p>
      </body></html>`
    mainWindow.loadURL(errorHtml)
    return
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
// IPC handlers — API key storage (Electron safeStorage + local file)
// ---------------------------------------------------------------------------

const KEYS_FILE = path.join(DATA_DIR, 'keys.enc')

function loadKeys() {
  try {
    if (!fs.existsSync(KEYS_FILE)) return {}
    const encrypted = fs.readFileSync(KEYS_FILE)
    const decrypted = safeStorage.decryptString(encrypted)
    return JSON.parse(decrypted)
  } catch {
    return {}
  }
}

function saveKeys(keys) {
  const encrypted = safeStorage.encryptString(JSON.stringify(keys))
  fs.writeFileSync(KEYS_FILE, encrypted)
}

ipcMain.handle('save-api-keys', async (_event, keys) => {
  const stored = loadKeys()
  for (const name of API_KEY_NAMES) {
    if (keys[name] !== undefined) {
      stored[name] = keys[name]
    }
  }
  saveKeys(stored)
})

ipcMain.handle('get-api-keys', async () => {
  const stored = loadKeys()
  const keys = {}
  for (const name of API_KEY_NAMES) {
    keys[name] = stored[name] || ''
  }
  return keys
})

ipcMain.handle('has-api-keys', async () => {
  const stored = loadKeys()
  return !!stored['GROQ_API_KEY']
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
    logToFile(`Auto-updater error: ${err.message}`)
  })

  // Check for updates 10 seconds after ready
  setTimeout(() => {
    autoUpdater.checkForUpdates().catch((err) => {
      logToFile(`Update check failed: ${err.message}`)
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
