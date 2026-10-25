// For: Vite build configuration and local dev server setup
// Must never: Bundle sensitive production credentials into client assets

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    host: "127.0.0.1"
  },
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});
