/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './{components,pages,contexts,services,store}/**/*.{tsx,ts,jsx,js}',
    './*.{tsx,ts}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ilma: {
          // Vibrant West Africa — primary (amber)
          primary: '#D97706',          // AA-safe on white (text)
          'primary-bright': '#F59E0B', // fills/backgrounds only
          'primary-light': '#FEF3C7',
          'primary-dark': '#92400E',

          // Semantic accents
          green: '#22C55E',
          'green-dark': '#15803D',
          'green-light': '#DCFCE7',
          red: '#DC2626',
          orange: '#F97316',
          'orange-dark': '#C2410C',
          'orange-light': '#FFF7ED',

          // Subject differentiation (semantic — unchanged)
          purple: '#7C3AED',
          'purple-light': '#EDE9FE',
          teal: '#0D9488',
          'teal-light': '#CCFBF1',
          pink: '#EC4899',
          'pink-light': '#FCE7F3',
          coral: '#F97316',
          lime: '#65A30D',
          sky: '#0EA5E9',
          gold: '#EAB308',
          'gold-light': '#FEF9C3',

          // Neutrals
          text: '#1F2937',
          surface: '#F9FAFB',
          border: '#E5E7EB',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Nunito', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        // Existing utility shadows (migrated to warm tones)
        card: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
        float: '0 10px 15px -3px rgba(217, 119, 6, 0.15), 0 4px 6px -2px rgba(245, 158, 11, 0.1)',
        fun: '0 10px 25px -5px rgba(217, 119, 6, 0.15), 0 8px 10px -6px rgba(249, 115, 22, 0.1)',
        'glow-amber': '0 0 20px rgba(217, 119, 6, 0.3)',
        'glow-green': '0 0 20px rgba(34, 197, 94, 0.3)',
        'glow-purple': '0 0 20px rgba(124, 58, 237, 0.3)',
        'glow-orange': '0 0 20px rgba(249, 115, 22, 0.3)',

        // Claymorphism shadows
        clay: '0 6px 16px rgba(217, 119, 6, 0.10), 0 2px 4px rgba(0, 0, 0, 0.04), inset 0 2px 0 rgba(255, 255, 255, 0.6)',
        'clay-sm': '0 3px 8px rgba(217, 119, 6, 0.08), 0 1px 2px rgba(0, 0, 0, 0.03), inset 0 1px 0 rgba(255, 255, 255, 0.5)',
        'clay-pressed': 'inset 0 2px 6px rgba(217, 119, 6, 0.15), inset 0 1px 2px rgba(0, 0, 0, 0.06)',
        'clay-hover': '0 8px 24px rgba(217, 119, 6, 0.16), 0 4px 8px rgba(0, 0, 0, 0.05), inset 0 2px 0 rgba(255, 255, 255, 0.7)',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
};
