/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        surface: 'var(--color-surface)',
        'surface-2': 'var(--color-surface-2)',
        'surface-3': 'var(--color-surface-3)',
        border: 'var(--color-border)',
        'border-hover': 'var(--color-border-hover)',
        primary: 'var(--color-primary)',
        'primary-dim': 'var(--color-primary-dim)',
        secondary: 'var(--color-secondary)',
        'secondary-dim': 'var(--color-secondary-dim)',
        tertiary: 'var(--color-tertiary)',
        'tertiary-dim': 'var(--color-tertiary-dim)',
        accent: 'var(--color-accent)',
        'accent-dim': 'var(--color-accent-dim)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-tertiary': 'var(--color-text-tertiary)',
        'text-muted': 'var(--color-text-muted)',
      },
      fontFamily: {
        sans: ['Inter', 'DM Sans', 'sans-serif'],
        heading: ['Bricolage Grotesque', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'sm': 'var(--radius-sm)',
        'md': 'var(--radius-md)',
        'lg': 'var(--radius-lg)',
        'xl': 'var(--radius-xl)',
      },
      boxShadow: {
        'glow-primary': '0 0 30px var(--color-primary-glow), 0 0 60px rgba(0,122,255,0.08)',
        'glow-sm': '0 0 15px rgba(0,122,255,0.15)',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #007AFF 0%, #5AC8FA 100%)',
        'gradient-purple': 'linear-gradient(135deg, #AF52DE 0%, #DA8FFF 100%)',
        'gradient-green': 'linear-gradient(135deg, #34C759 0%, #30D158 100%)',
        'gradient-dark': 'linear-gradient(180deg, #111520 0%, #0B0E14 100%)',
      },
    },
  },
  plugins: [],
}
