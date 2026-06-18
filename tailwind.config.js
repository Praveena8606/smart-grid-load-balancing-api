/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: '#0B1220',
        panel: '#121B2E',
        raised: '#182438',
        line: '#233047',
        muted: '#8B97AC',
        ink: '#E7ECF5',
        normal: '#2DD4BF',
        info: '#38BDF8',
        warn: '#F59E0B',
        crit: '#F8717A'
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace']
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(45,212,191,0.15), 0 0 24px -4px rgba(45,212,191,0.25)'
      }
    }
  },
  plugins: []
}
