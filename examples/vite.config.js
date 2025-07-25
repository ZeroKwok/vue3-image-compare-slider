import { defineConfig } from 'vite'
import { resolve } from 'path'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  build: {
    sourcemap: true,
  },
  resolve: {
    alias: {
      'vue3-image-compare-slider': resolve(__dirname, '../src'),
    },
  },
})
