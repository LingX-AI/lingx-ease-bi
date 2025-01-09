/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#1766E1',
        'primary-1': '#BC141B',
        'success': '#3bb143',
        'info': '#4e5969',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'text-1': '#212328',
        'text-2': '#696974',
        'text-3': '#9898A3',
        'bg-1': '#04346114',
        'bg-2': '#f2f3f5',
        'border-1': '#0000001e',
      },
    },
  },
  plugins: [],
}
