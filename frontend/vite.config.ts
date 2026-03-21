import { fileURLToPath, URL } from "node:url";
import { VitePWA } from "vite-plugin-pwa";
import tailwindcss from "@tailwindcss/vite";
import vueDevTools from "vite-plugin-vue-devtools";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  server: {
    allowedHosts: ["sholkallan.vinlaro.com", "colonypm.xxx"],
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  plugins: [
    vue(),
    //vueDevTools(),
    tailwindcss(),
    VitePWA({
      strategies: "injectManifest",
      srcDir: "src",
      filename: "sw.ts",

      registerType: "autoUpdate",

      includeAssets: ["favicon.ico", "apple-touch-icon-180x180-v2.png", "maskable-icon-512x512-v2.png"],
      manifest: {
        name: "kallan",
        short_name: "kallan",
        description: "kallan",
        theme_color: "#110d0d",
        background_color: "#110d0d",
        icons: [
          { src: "pwa-64x64-v2.png", sizes: "64x64", type: "image/png" },
          { src: "pwa-192x192-v2.png", sizes: "192x192", type: "image/png" },
          { src: "pwa-512x512-v2.png", sizes: "512x512", type: "image/png", purpose: "any" },
          {
            src: "maskable-icon-512x512-v2.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      devOptions: {
        enabled: true,
        type: "module",
      },
    }),
  ],
});
