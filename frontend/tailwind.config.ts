import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        navy:    '#0f2342',
        'navy-light': '#1a3a6b',
        slate:   '#f0f2f5',
        'slate-mid': '#e2e6ec',
        'slate-dark': '#c8cfd8',
        ink:     '#1a1f2e',
        'ink-mid': '#4a5568',
        'ink-light': '#8492a6',
        accent:  '#1d6fdb',
        'accent-light': '#e8f0fb',
        positive:'#0a7c42',
        'positive-bg': '#e8f5ee',
        warning: '#b45309',
        'warning-bg': '#fef3e2',
        danger:  '#c0392b',
        'danger-bg': '#fdecea',
        border:  '#dce1ea',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
