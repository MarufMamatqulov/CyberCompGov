/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: "#1B365D", 50: "#EEF2F8", 100: "#D6E0EE", 700: "#16304F", 900: "#0E1F38" },
        slate2: "#2B547E",
        emerald: { DEFAULT: "#10B981" },
        amber: { DEFAULT: "#F59E0B" },
        crimson: { DEFAULT: "#EF4444" },
        before: "#D9822B",
        after: "#3A6FB0",
      },
      fontFamily: { sans: ["Inter", "system-ui", "Segoe UI", "Roboto", "sans-serif"] },
    },
  },
  plugins: [],
};
