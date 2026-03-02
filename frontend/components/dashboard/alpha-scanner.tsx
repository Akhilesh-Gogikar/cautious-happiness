"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Zap, Target, Activity, Loader2, Filter } from 'lucide-react';
import { toast } from 'sonner';

interface ScanResult {
    symbol: string;
    name: string;
    asset_class: string;
    sector: string;
    price: number;
    physical_premium: number;
    mirror_accuracy: number;
    algo_noise: string;
    signal: string;
}

export function AlphaScanner() {
    const [assets, setAssets] = useState<ScanResult[]>([]);
    const [loading, setLoading] = useState(false);

    // Filters state
    const [minPremium, setMinPremium] = useState<number[]>([2]);
    const [minAccuracy, setMinAccuracy] = useState<number[]>([90]);
    const [assetClass, setAssetClass] = useState<string>('all');
    const [sector, setSector] = useState<string>('all');

    const handleScan = async () => {
        setLoading(true);
        try {
            // Build query params
            const params = new URLSearchParams();
            if (minPremium[0] > 0) params.append('min_physical_premium', minPremium[0].toString());
            if (minAccuracy[0] > 0) params.append('min_mirror_accuracy', minAccuracy[0].toString());
            if (assetClass !== 'all') params.append('asset_class', assetClass);
            if (sector !== 'all') params.append('sector', sector);

            // Need an absolute API call since this might run in a different frontend port than the backend
            // typically the frontend sets a proxy or we can just call it (assuming backend runs on 8000)
            const response = await fetch(`http://localhost:8000/api/v1/scanner/assets?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to fetch data');
            const data = await response.json();
            setAssets(data);
            toast.success(`Scan complete. Found ${data.length} matching assets.`);
        } catch (error) {
            console.error(error);
            toast.error('Garrison system overloaded. Failed to fetch scanner data.');
        } finally {
            setLoading(false);
        }
    };

    // Auto-scan on component mount
    useEffect(() => {
        handleScan();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <div className="space-y-6 animate-fade-in pb-10">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-black text-white flex items-center gap-2">
                        <Zap className="w-6 h-6 text-primary" />
                        ALPHA SCANNER
                        <Badge variant="outline" className="ml-2 bg-primary/20 text-primary border-primary/30">
                            HIGH-SPEED SCREENING
                        </Badge>
                    </h2>
                    <p className="text-muted-foreground text-sm font-mono mt-1">
                        Filter global assets instantaneously using proprietary Neural Engine AI Metrics.
                    </p>
                </div>
                <Button
                    onClick={handleScan}
                    disabled={loading}
                    className="bg-primary/20 hover:bg-primary/30 text-primary border border-primary/50 shadow-[0_0_15px_rgba(16,185,129,0.2)] transition-all"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Filter className="w-4 h-4 mr-2" />}
                    EXECUTE SCAN
                </Button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {/* Advanced Filtering Panel */}
                <Card className="p-5 bg-card/40 backdrop-blur-xl border-white/5 shadow-2xl space-y-8 md:col-span-1 border-r border-r-primary/10">
                    <div className="space-y-4">
                        <div className="flex justify-between items-center text-sm">
                            <label className="font-mono text-white/80 flex items-center gap-2">
                                <Activity className="w-4 h-4 text-emerald-400" />
                                Physical Premium &gt; ${minPremium[0]}
                            </label>
                        </div>
                        <Slider
                            value={minPremium}
                            onValueChange={setMinPremium}
                            max={10}
                            step={0.5}
                            min={-2}
                            className="w-full"
                        />
                        <p className="text-[10px] text-muted-foreground font-mono">
                            Filters out assets trading below their physical derivative spot premium.
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="flex justify-between items-center text-sm">
                            <label className="font-mono text-white/80 flex items-center gap-2">
                                <Target className="w-4 h-4 text-cyan-400" />
                                Mirror Accuracy &gt; {minAccuracy[0]}%
                            </label>
                        </div>
                        <Slider
                            value={minAccuracy}
                            onValueChange={setMinAccuracy}
                            max={100}
                            step={1}
                            min={50}
                            className="w-full text-cyan-500"
                        />
                        <p className="text-[10px] text-muted-foreground font-mono">
                            Required AI confidence correlation with expected algorithmic trajectories.
                        </p>
                    </div>

                    <div className="space-y-4">
                        <label className="font-mono text-sm text-white/80 block">Asset Class</label>
                        <select
                            value={assetClass}
                            onChange={(e) => setAssetClass(e.target.value)}
                            className="w-full bg-black/40 border border-white/10 rounded-md p-2 text-sm text-white focus:border-primary/50 transition-colors"
                        >
                            <option value="all">All Classes</option>
                            <option value="commodity">Commodity</option>
                            <option value="equity">Equity</option>
                            <option value="crypto">Crypto</option>
                        </select>
                    </div>

                    <div className="space-y-4">
                        <label className="font-mono text-sm text-white/80 block">Sector</label>
                        <select
                            value={sector}
                            onChange={(e) => setSector(e.target.value)}
                            className="w-full bg-black/40 border border-white/10 rounded-md p-2 text-sm text-white focus:border-primary/50 transition-colors"
                        >
                            <option value="all">All Sectors</option>
                            <option value="energy">Energy</option>
                            <option value="metals">Metals</option>
                            <option value="technology">Technology</option>
                        </select>
                    </div>
                </Card>

                {/* Results Table */}
                <Card className="p-0 bg-card/60 backdrop-blur-xl border-white/5 shadow-2xl md:col-span-3 overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-white/5 bg-black/40 flex justify-between items-center">
                        <h3 className="font-mono text-sm text-white/80 tracking-widest uppercase">Scanner Results</h3>
                        <div className="text-xs font-mono text-muted-foreground bg-white/5 px-2 py-1 rounded">
                            {assets.length} ASSETS IDENTIFIED
                        </div>
                    </div>

                    <div className="overflow-x-auto flex-1 custom-scrollbar max-h-[600px]">
                        <Table>
                            <TableHeader className="bg-black/40 sticky top-0 z-10">
                                <TableRow className="border-white/5 hover:bg-transparent">
                                    <TableHead className="font-mono text-white/60">SYMBOL</TableHead>
                                    <TableHead className="font-mono text-white/60">SECTOR</TableHead>
                                    <TableHead className="font-mono text-white/60">PRICE</TableHead>
                                    <TableHead className="font-mono text-white/60">PHY_PREMIUM</TableHead>
                                    <TableHead className="font-mono text-white/60">MIRROR_ACC</TableHead>
                                    <TableHead className="font-mono text-white/60 text-right">NEURAL_SIGNAL</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {assets.length === 0 && !loading && (
                                    <TableRow className="border-none">
                                        <TableCell colSpan={6} className="h-48 text-center text-muted-foreground font-mono">
                                            No assets matched the current AI metric criteria.
                                        </TableCell>
                                    </TableRow>
                                )}
                                {assets.map((asset) => (
                                    <TableRow key={asset.symbol} className="border-white/5 hover:bg-white/[0.02] cursor-pointer group transition-colors">
                                        <TableCell>
                                            <div className="flex flex-col">
                                                <span className="font-black text-white group-hover:text-primary transition-colors">{asset.symbol}</span>
                                                <span className="text-[10px] text-muted-foreground">{asset.name.substring(0, 20)}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className="bg-white/5 border-white/10 uppercase text-[10px]">
                                                {asset.sector}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="font-mono text-white">${asset.price.toFixed(2)}</TableCell>
                                        <TableCell>
                                            <span className={`font-mono font-bold ${asset.physical_premium > 2 ? 'text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'text-white/70'}`}>
                                                +${asset.physical_premium.toFixed(2)}
                                            </span>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex items-center gap-2">
                                                <span className={`font-mono ${asset.mirror_accuracy > 90 ? 'text-cyan-400 text-glow-neon' : 'text-white/70'}`}>
                                                    {asset.mirror_accuracy.toFixed(1)}%
                                                </span>
                                                <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full ${asset.mirror_accuracy > 90 ? 'bg-cyan-400' : 'bg-white/40'}`}
                                                        style={{ width: `${asset.mirror_accuracy}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Badge className={`
                                                uppercase font-black text-[10px] tracking-wider
                                                ${asset.signal.includes('BUY') ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50' : ''}
                                                ${asset.signal.includes('SELL') ? 'bg-red-500/20 text-red-400 border border-red-500/50' : ''}
                                                ${asset.signal === 'NEUTRAL' ? 'bg-white/10 text-white/50 border border-white/20' : ''}
                                            `}>
                                                {asset.signal}
                                            </Badge>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </Card>
            </div>
        </div>
    );
}
