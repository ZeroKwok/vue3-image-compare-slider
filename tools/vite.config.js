import { defineConfig } from 'vite'
import { resolve } from 'path'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  publicDir: '../examples/public',
  build: {
    sourcemap: true,
    outDir: 'templet',
  },
  resolve: {
    alias: {
      'vue3-image-compare-slider': resolve(__dirname, '../src'),
    },
  },
})
