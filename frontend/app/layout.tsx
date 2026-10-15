"use client";

import './globals.css';
import './prism-theme.css';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { Toaster } from "@/components/ui/sonner";
import { SidebarChat } from '@/components/layout/sidebar-chat';

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

import { AuthProvider } from '@/lib/auth';

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
                <AuthProvider>
                    <div className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-primary-foreground">
                        {children}
                        <SidebarChat />
                    </div>
                    <Toaster />
                </AuthProvider>
            </body>
        </html>
    );
}
