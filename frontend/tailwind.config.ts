import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: '#2B5EA7',
        accent: '#E8533A',
        surface: '#F9F8F5',
        'surface-2': '#EEECE8',
        'text-primary': '#1A1A2E',
        'text-secondary': '#555566',
        'text-tertiary': '#8888AA',
        'agent-sre': '#E8533A',
        'agent-arch': '#2B5EA7',
        'agent-cloud': '#1D9E75',
        'agent-java': '#BA7517',
        'agent-ui': '#7F77DD',
        'agent-human': '#2A7A2A',
      },
    },
  },
  plugins: [],
} satisfies Config
