import { PnLVelocityChart } from "@/components/PnLVelocityChart";
import { Sidebar } from "@/components/ui/sidebar";

export default function PnLPage() {
    return (
        <div className="flex min-h-screen bg-[#020617]">
            <div className="flex-1 p-8 overflow-y-auto">
                <div className="max-w-6xl mx-auto space-y-12">
                    <header className="flex justify-between items-end">
                        <div>
                            <h1 className="text-4xl font-extrabold text-white tracking-tight">
                                Execution <span className="text-blue-500">Analytics</span>
                            </h1>
                            <p className="text-slate-400 mt-2 text-lg">
                                High-frequency PnL velocity tracking for active market orders.
                            </p>
                        </div>
                        <div className="text-right hidden md:block">
                            <div className="text-xs text-slate-500 uppercase font-bold tracking-widest">Election Night Mode</div>
                            <div className="text-blue-500 font-mono text-sm">VOLATILITY: HIGH</div>
                        </div>
                    </header>

                    <div className="grid grid-cols-1 gap-8">
                        <PnLVelocityChart marketId="simulated-election-2024" />

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-xl hover:bg-slate-900/60 transition-colors">
                                <div className="text-xs text-slate-500 uppercase font-bold mb-1">Max Drawdown</div>
                                <div className="text-2xl font-mono text-white">$420.69</div>
                            </div>
                            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-xl hover:bg-slate-900/60 transition-colors">
                                <div className="text-xs text-slate-500 uppercase font-bold mb-1">Sharpe Ratio</div>
                                <div className="text-2xl font-mono text-white">3.14</div>
                            </div>
                            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-xl hover:bg-slate-900/60 transition-colors">
                                <div className="text-xs text-slate-500 uppercase font-bold mb-1">Alpha Source</div>
                                <div className="text-2xl font-mono text-blue-400 font-semibold tracking-tighter">LLM-W3-ADJ</div>
                            </div>
                        </div>
                    </div>

                    <footer className="pt-12 border-t border-slate-900 flex justify-between items-center text-slate-600 text-xs">
                        <p>© 2026 Antigravity Executive Terminal</p>
                        <div className="flex gap-4">
                            <span>LATENCY: 12ms</span>
                            <span>FEED: POLYMARKET CLOB</span>
                        </div>
                    </footer>
                </div>
            </div>
        </div>
    );
}
