/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dvmcp: {
          bg: '#0a0e17',
          card: '#111827',
          border: '#1f2937',
          accent: '#ef4444',
          green: '#22c55e',
          yellow: '#eab308',
          blue: '#3b82f6',
          purple: '#a855f7',
        },
      },
    },
  },
  plugins: [],
}
