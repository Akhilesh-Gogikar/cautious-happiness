import type { Config } from "tailwindcss"

const config = {
    darkMode: ["class"],
    content: [
        './pages/**/*.{ts,tsx}',
        './components/**/*.{ts,tsx}',
        './app/**/*.{ts,tsx}',
        './src/**/*.{ts,tsx}',
    ],
    prefix: "",
    theme: {
        container: {
            center: true,
            padding: "2rem",
            screens: {
                "2xl": "1400px",
            },
        },
        extend: {
            fontFamily: {
                sans: ["var(--font-inter)", "sans-serif"],
                mono: ["var(--font-jetbrains)", "monospace"],
            },
            colors: {
                border: "hsl(var(--border))",
                input: "hsl(var(--input))",
                ring: "hsl(var(--ring))",
                background: "hsl(var(--background))",
                foreground: "hsl(var(--foreground))",
                primary: {
                    DEFAULT: "hsl(var(--primary))",
                    foreground: "hsl(var(--primary-foreground))",
                },
                secondary: {
                    DEFAULT: "hsl(var(--secondary))",
                    foreground: "hsl(var(--secondary-foreground))",
                },
                destructive: {
                    DEFAULT: "hsl(var(--destructive))",
                    foreground: "hsl(var(--destructive-foreground))",
                },
                muted: {
                    DEFAULT: "hsl(var(--muted))",
                    foreground: "hsl(var(--muted-foreground))",
                },
                accent: {
                    DEFAULT: "hsl(var(--accent))",
                    foreground: "hsl(var(--accent-foreground))",
                },
                popover: {
                    DEFAULT: "hsl(var(--popover))",
                    foreground: "hsl(var(--popover-foreground))",
                },
                card: {
                    DEFAULT: "hsl(var(--card))",
                    foreground: "hsl(var(--card-foreground))",
                },
                // Financial / Signal Colors - BRIGHTER
                success: {
                    DEFAULT: "#10B981",
                    foreground: "#ECFDF5",
                },
                warning: {
                    DEFAULT: "#F59E0B",
                    foreground: "#FFFBEB",
                },
                danger: {
                    DEFAULT: "#EF4444",
                    foreground: "#FEF2F2",
                },
                // Cyber Accents
                indigo: "hsl(var(--indigo))",
                "cyber-blue": "hsl(var(--cyber-blue))",
                gold: "hsl(var(--gold))",
                neon: {
                    blue: "#00F0FF",
                    green: "#00FF94",
                    purple: "#BC13FE",
                    pink: "#FF007A",
                }
            },
            borderRadius: {
                lg: "var(--radius)",
                md: "calc(var(--radius) - 2px)",
                sm: "calc(var(--radius) - 4px)",
            },
            keyframes: {
                "accordion-down": {
                    from: { height: "0" },
                    to: { height: "var(--radix-accordion-content-height)" },
                },
                "accordion-up": {
                    from: { height: "var(--radix-accordion-content-height)" },
                    to: { height: "0" },
                },
                "fade-in": {
                    from: { opacity: "0", transform: "translateY(10px)" },
                    to: { opacity: "1", transform: "translateY(0)" }
                },
                "ticker": {
                    from: { transform: "translateX(0)" },
                    to: { transform: "translateX(-100%)" }
                },
                "scanline": {
                    "0%": { transform: "translateY(-100%)", opacity: "0" },
                    "10%": { opacity: "1" },
                    "90%": { opacity: "1" },
                    "100%": { transform: "translateY(100%)", opacity: "0" }
                },
                "pulse-glow": {
                    "0%, 100%": { opacity: "1", transform: "scale(1)", filter: "brightness(1)" },
                    "50%": { opacity: "0.8", transform: "scale(1.02)", filter: "brightness(1.2)" }
                }
            },
            animation: {
                "accordion-down": "accordion-down 0.2s ease-out",
                "accordion-up": "accordion-up 0.2s ease-out",
                "fade-in": "fade-in 0.5s ease-out forwards",
                "ticker": "ticker 20s linear infinite",
                "scanline": "scanline 8s linear infinite",
                "pulse-glow": "pulse-glow 2s ease-in-out infinite",
            },
        },
    },
    plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
