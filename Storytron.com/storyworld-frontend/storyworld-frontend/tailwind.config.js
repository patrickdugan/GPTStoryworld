/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#070B12',
        surface: '#0E1624',
        accent: '#F97316',
        cyan: '#22D3EE'
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'ui-sans-serif', 'sans-serif'],
        body: ['Manrope', 'ui-sans-serif', 'sans-serif']
      },
      boxShadow: {
        card: '0 10px 30px rgba(0, 0, 0, 0.35)'
      },
      keyframes: {
        rise: {
          '0%': { opacity: 0, transform: 'translateY(24px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' }
        }
      },
      animation: {
        rise: 'rise 500ms ease-out both'
      }
    }
  },
  plugins: []
}
