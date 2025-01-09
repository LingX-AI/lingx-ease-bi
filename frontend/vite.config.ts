import path from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import viteCompression from 'vite-plugin-compression'
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'
import vueJsx from '@vitejs/plugin-vue-jsx'

export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia',
        'vue-i18n',
      ] as any,
      dirs: [
        './src/components/**',
        './src/composables/**',
      ],
    }),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false,
        }),
      ],
    }),
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10 * 1024,
      algorithm: 'gzip',
      ext: '.gz',
    }),
  ],
  server: {
    host: '0.0.0.0',
    port: 3333,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
