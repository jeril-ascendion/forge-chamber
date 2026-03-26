const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // File system
  pickFiles: () => ipcRenderer.invoke('pick-files'),
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  getDataDir: () => ipcRenderer.invoke('get-data-dir'),

  // API key storage (safeStorage)
  saveApiKeys: (keys) => ipcRenderer.invoke('save-api-keys', keys),
  getApiKeys: () => ipcRenderer.invoke('get-api-keys'),
  hasApiKeys: () => ipcRenderer.invoke('has-api-keys'),

  // App updates
  onUpdateReady: (callback) => ipcRenderer.on('update-ready', callback),
  installUpdate: () => ipcRenderer.invoke('install-update'),

  // Sidecar
  getSidecarPort: () => ipcRenderer.invoke('get-sidecar-port'),

  // Sidecar status events
  onSidecarRestarted: (callback) => ipcRenderer.on('sidecar-restarted', callback),
  onSidecarFailed: (callback) => ipcRenderer.on('sidecar-failed', callback),
})
