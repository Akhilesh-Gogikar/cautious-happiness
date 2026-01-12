import './globals.css';
import '@rainbow-me/rainbowkit/styles.css';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { Providers } from './providers';
import { Metadata, Viewport } from 'next';

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
    display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
    subsets: ['latin'],
    variable: '--font-jetbrains',
    display: 'swap',
});

export const metadata: Metadata = {
    title: "AlphaSignals Dashboard",
    description: "Institutional-grade AI-enabled trading platform",
    manifest: "/manifest.json",
};

export const viewport: Viewport = {
    themeColor: "#000000",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
                <Providers>
                    <div className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-primary-foreground">
                        {children}
                    </div>
                </Providers>
            </body>
        </html>
    );
}
