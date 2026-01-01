/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4A90E2',
          hover: '#3A7BC8',
          light: '#E3F2FD'
        },
        success: '#66BB6A',
        warning: '#FF9800',
        danger: '#E53935',
        bg: {
          DEFAULT: '#F5F7FA',
          dark: '#1A1A2E'
        },
        card: {
          DEFAULT: '#FFFFFF',
          dark: '#16213E'
        },
        text: {
          primary: '#333333',
          secondary: '#666666',
          tertiary: '#999999',
          dark: '#F5F5F5'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.08)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.12)',
      }
    },
  },
  plugins: [],
}
