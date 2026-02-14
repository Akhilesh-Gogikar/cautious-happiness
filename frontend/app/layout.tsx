"use client";

import './globals.css';
import './prism-theme.css';
import '@rainbow-me/rainbowkit/styles.css';
import { RainbowKitProvider, darkTheme } from '@rainbow-me/rainbowkit';
import { WagmiConfig } from 'wagmi';
import { wagmiConfig, chains } from '@/lib/wagmi';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { Toaster } from "@/components/ui/sonner";

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

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
                <WagmiConfig config={wagmiConfig}>
                    <RainbowKitProvider
                        chains={chains}
                        theme={darkTheme({
                            accentColor: '#10B981', // Emerald Primary
                            accentColorForeground: 'white',
                            borderRadius: 'small',
                            fontStack: 'system',
                            overlayBlur: 'small',
                        })}
                    >
                        <div className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-primary-foreground">
                            {children}
                        </div>
                        <Toaster />
                    </RainbowKitProvider>
                </WagmiConfig>
            </body>
        </html>
    );
}
