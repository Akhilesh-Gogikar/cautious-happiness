'use client';

import { RainbowKitProvider, darkTheme } from '@rainbow-me/rainbowkit';
import { WagmiConfig } from 'wagmi';
import { wagmiConfig, chains } from '@/lib/wagmi';
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from '@/components/providers/auth-context';

export function Providers({ children }: { children: React.ReactNode }) {
    return (
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
                <AuthProvider>
                    {children}
                    <Toaster />
                </AuthProvider>
            </RainbowKitProvider>
        </WagmiConfig>
    );
}
