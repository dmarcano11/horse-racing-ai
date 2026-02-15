/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: '#080B10',
        deep: '#0D1117',
        surface: '#121820',
        card: '#171F2A',
        'card-hi': '#1D2535',
        gold: '#C49E42',
        'gold-light': '#E3C068',
        cream: '#EDE4CC',
        slate: '#8A98AE',
        muted: '#4D5B70',
        live: '#E04B35',
        atb: {
          green: '#3CB87A',
          blue: '#4A8FE8',
        }
      },
      fontFamily: {
        display: ['"Cormorant Garamond"', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        body: ['"Nunito Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
