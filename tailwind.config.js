module.exports = {
  future: {
    hoverOnlyWhenSupported: true
  },
  plugins: [
    require('daisyui')
  ],
  daisyui: {
    themes: [
      {
        docuseal: {
          'color-scheme': 'light',
          primary: '#e3eaf3',
          secondary: '#2280dc',
          accent: '#3de2ff',
          neutral: '#132741',
          'base-100': '#f7f9fc',
          'base-200': '#edf1f7',
          'base-300': '#e1e7f0',
          'base-content': '#132741',
          '--rounded-btn': '1.9rem',
          '--btn-text-case': 'none',
          '--tab-border': '2px',
          '--tab-radius': '.5rem'
        }
      }
    ]
  }
}
