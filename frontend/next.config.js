/** @type {import('next').NextConfig} */
const withPWA = require("@ducanh2912/next-pwa").default({
    dest: "public",
    register: true,
    skipWaiting: true,
    disable: process.env.NODE_ENV === "development",
});

const nextConfig = {
    reactStrictMode: true,
    output: "standalone",
    experimental: {
        serverActions: {
            allowedOrigins: ["localhost:3000", "0.0.0.0:3000", "127.0.0.1:3000"],
        },
    },
    // Add headers to potentially fix CSP/WalletConnect issues if needed, 
    // but usually default is fine.
    async headers() {
        return [
            {
                source: "/:path*",
                headers: [
                    {
                        key: "Content-Security-Policy",
                        // Permissive CSP for development to fix WalletConnect iframe issues
                        value: "frame-ancestors 'self' https://*.walletconnect.com https://*.walletconnect.org;",
                    },
                ],
            },
        ];
    },
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.BACKEND_URL ? `${process.env.BACKEND_URL}/:path*` : 'http://localhost:8000/:path*',
            },
        ];
    },
};

module.exports = withPWA(nextConfig);
