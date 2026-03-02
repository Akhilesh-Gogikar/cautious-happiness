/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                // In docker, backend is accessible at http://backend:8000
                // In local dev without docker, it might be http://localhost:8000
                destination: process.env.BACKEND_URL ? `${process.env.BACKEND_URL}/:path*` : 'http://localhost:8000/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
