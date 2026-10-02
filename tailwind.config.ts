import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}', './lib/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        navy: '#10233F',
        mustard: '#D5A021',
        mustardDark: '#9A6D0B',
        ivory: '#F6F4EF',
        slateLight: '#E8EAF0',
        textMuted: '#667085',
        navySecondary: '#26364F',
        white: '#FFFFFF',
      },
      boxShadow: {
        soft: '0 8px 24px rgba(16, 35, 63, 0.08)',
      },
      borderRadius: {
        xl: '1rem',
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
