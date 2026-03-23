import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.ascendion.forgechamber',
  appName: 'Forge Chamber',
  webDir: '../frontend/dist',
  plugins: {
    Microphone: { permissions: ['microphone'] },
  },
}

export default config
