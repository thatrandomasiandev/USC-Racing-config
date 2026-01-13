import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0078D4', // Microsoft blue
          dark: '#005A9E',
          light: '#40A6FF',
        },
        ribbon: {
          DEFAULT: '#F3F3F3',
          hover: '#E1E1E1',
          active: '#C8E6F5',
        },
        word: {
          bg: '#FFFFFF',
          surface: '#F8F8F8',
          border: '#D4D4D4',
          text: '#323130',
          textSecondary: '#605E5C',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'Calibri', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'word': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        'word-lg': '0 2px 6px rgba(0,0,0,0.15), 0 1px 3px rgba(0,0,0,0.12)',
      },
    },
  },
  plugins: [],
}
export default config
