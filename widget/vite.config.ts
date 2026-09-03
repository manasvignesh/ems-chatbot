import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  build: {
    lib: {
      entry: path.resolve(__dirname, "src/index.ts"),
      name: "EMSAssistant",
      fileName: () => "widget.js",
      formats: ["iife"],
    },
    rollupOptions: {
      // Bundle React and ReactDOM directly inside widget.js so host site needs nothing
      external: [],
      output: {
        extend: true,
      },
    },
    cssCodeSplit: false,
    minify: "esbuild",
  },
});
