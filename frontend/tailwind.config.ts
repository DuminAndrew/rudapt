import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: { DEFAULT: "#0B0F1F", deeper: "#070A16", surface: "#0F1530" },
        ink: { DEFAULT: "#E5E9F5", muted: "#9AA3BF", dim: "#64748B" },
        cyan: { brand: "#06B6D4" },
        blue: { brand: "#3B82F6" },
        violet: { brand: "#8B5CF6" },
        magenta: { brand: "#D946EF" },
        rose: { brand: "#F43F5E" },
        orange: { brand: "#F97316" },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "grad-cyan": "linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)",
        "grad-violet": "linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%)",
        "grad-rose": "linear-gradient(135deg, #F43F5E 0%, #F97316 100%)",
        "grad-brand": "linear-gradient(90deg, #8B5CF6 0%, #F43F5E 100%)",
        "grad-hero":
          "radial-gradient(60% 60% at 50% 0%, rgba(139,92,246,0.30) 0%, rgba(11,15,31,0) 70%), radial-gradient(40% 40% at 90% 30%, rgba(244,63,94,0.25) 0%, rgba(11,15,31,0) 70%), radial-gradient(40% 40% at 10% 70%, rgba(6,182,212,0.25) 0%, rgba(11,15,31,0) 70%)",
      },
      boxShadow: {
        glow: "0 10px 40px -10px rgba(139,92,246,0.55)",
        "glow-rose": "0 10px 40px -10px rgba(244,63,94,0.55)",
        "glow-cyan": "0 10px 40px -10px rgba(6,182,212,0.55)",
      },
      borderRadius: { xl: "1rem", "2xl": "1.25rem" },
      keyframes: {
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-8px)" } },
      },
      animation: { float: "float 6s ease-in-out infinite" },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
