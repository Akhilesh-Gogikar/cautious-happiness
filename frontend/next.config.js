/** @type {import('next').NextConfig} */
const nextConfig = {
    // next dev serves its dev resources (HMR, chunks) only to these origins and
    // localhost; without them a page opened at 127.0.0.1 never becomes interactive.
    allowedDevOrigins: ['127.0.0.1'],
    // Agent guidance lives in docs/AGENTS.md; don't let next dev write frontend/AGENTS.md.
    agentRules: false,
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
