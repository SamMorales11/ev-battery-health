import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons()
  ],
  theme: {
    colors: {
      brand: {
        dark: '#0f172a',
        card: '#1e293b',
        accent: '#38bdf8'
      }
    }
  }
})