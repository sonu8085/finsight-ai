/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0B1220",
          surface: "#121B2E",
          raised: "#182238",
          border: "#232F47",
        },
        paper: {
          DEFAULT: "#E8ECF3",
          muted: "#8B96AB",
          faint: "#5C6883",
        },
        emerald: {
          DEFAULT: "#3DD68C",
          dim: "#245C41",
        },
        coral: {
          DEFAULT: "#FF6B5D",
          dim: "#5C2E28",
        },
        gold: {
          DEFAULT: "#E8B85C",
          dim: "#4A3B1E",
        },
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
