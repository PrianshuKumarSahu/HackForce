/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        km: {
          teal: '#009999',       // Official KMRL Primary Teal
          tealDark: '#007A7A',   // Deep Teal
          tealLight: '#02B0AF',  // Bright Teal
          cyan: '#16DDDD',       // Accent Cyan
          aqua: '#E0F7F6',       // Soft Aqua Light Background
          aquaSoft: '#F0FDFB',   // Ultra soft aqua
          navy: '#0F172A',       // Hero Navy Dark
          slateDark: '#1E293B',  // Container border / text dark
          gold: '#F59E0B',       // Standby / Caution
          emerald: '#10B981',    // Certified Fit / Active
          coral: '#EF4444',      // Maintenance / Critical
          indigo: '#6366F1',     // Branding / Commercial
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'system-ui', 'sans-serif'],
        heading: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'km-glow': '0 0 20px rgba(0, 153, 153, 0.25)',
        'km-card': '0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(0, 153, 153, 0.04)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
}
