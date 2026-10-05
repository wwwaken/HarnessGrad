import path from "node:path";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// The SPA is served by the (future) read API under `/`, so asset paths stay relative.
// `base: "./"` lets the built `dist/` be opened from any mount point, which is what the
// `dsh web`-style host will want; the dev server is unaffected.
export default defineConfig({
  base: "./",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // No asset inlining. The fixture JSON is fetched through `new URL(...)` exactly as the
    // eventual API responses will be, and Vite's default 4 KB `assetsInlineLimit` turned the
    // smallest fixture (`launch-options.json`, 3.9 KB) into a base64 `data:` URL in production
    // while the dev server served it as a file — a difference between the two modes in the one
    // layer whose whole job is to behave like the network it is standing in for.
    assetsInlineLimit: 0,
    // Monaco is by far the heaviest dependency and is only needed on the compare and
    // run-detail screens, so it is split out instead of inflating the entry chunk. Matching
    // on the module id (rather than the package name) also covers the deep ESM imports in
    // `src/lib/monaco.ts`, which pull in only two language grammars.
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("monaco-editor")) return "monaco";
          return undefined;
        },
      },
    },
    chunkSizeWarningLimit: 3500,
  },
  server: {
    // Not the Vite default (5173): on this machine another project's Vite dev server already
    // holds 5173, and `strictPort` makes the collision a startup error rather than a silent
    // move to a port the README does not name.
    port: 5273,
    strictPort: true,
    // In production `web/server/serve.py` serves the built SPA *and* `/api` from one origin,
    // so no proxy is needed. In development the SPA is on 5273 and the read API on 8791:
    // this forwards `/api/...` so `resolveBackend()`'s `/api/health` probe and every data
    // request are same-origin and need no CORS. The API also sets
    // `Access-Control-Allow-Origin: *`, but a proxy is what makes the dev URLs match the
    // production ones exactly.
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8791",
        changeOrigin: false,
      },
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.{ts,tsx}"],
    globals: false,
  },
});
