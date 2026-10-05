/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ['"Plus Jakarta Sans"', "ui-sans-serif", "system-ui", "Segoe UI", "sans-serif"] },
      colors: {
        brand: { 50: "#ecfdf5", 100: "#d1fae5", 200: "#a7f3d0", 500: "#14b8a6", 600: "#0f9488", 700: "#0f766e", 800: "#115e59", 900: "#134e4a" },
        ink: "#0f1b2d",
      },
    },
  },
  plugins: [],
};
