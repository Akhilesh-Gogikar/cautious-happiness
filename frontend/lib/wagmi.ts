import { getDefaultWallets } from '@rainbow-me/rainbowkit';
import { configureChains, createConfig } from 'wagmi';
import { polygon, mainnet } from 'wagmi/chains';
import { publicProvider } from 'wagmi/providers/public';

const { chains, publicClient } = configureChains(
    [polygon, mainnet],
    [publicProvider()]
);

const { connectors } = getDefaultWallets({
    appName: 'AlphaSignals Hedge Fund',
    projectId: 'YOUR_PROJECT_ID', // Replace with environment variable
    chains
});

export const wagmiConfig = createConfig({
    autoConnect: true,
    connectors,
    publicClient
});

export { chains };
