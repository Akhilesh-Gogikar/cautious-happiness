"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, Lock, Terminal, Activity, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { Button } from "@/components/ui/button";

interface RiskStatus {
    name: string;
    status: string;
    level: "NORMAL" | "WARNING" | "CRITICAL";
    latency?: string;
    details?: string;
}

interface RiskReport {
    overall_health: string;
    components: RiskStatus[];
    last_updated: number;
}

export function SecurityView() {
    const [riskReport, setRiskReport] = useState<RiskReport | null>(null);

    useEffect(() => {
        const fetchRisk = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '/api'}/risk/status`);
                const data = await res.json();
                setRiskReport(data);
            } catch (err) {
                console.error("Failed to fetch risk status:", err);
            }
        };

        fetchRisk();
        const interval = setInterval(fetchRisk, 10000); // Update every 10s
        return () => clearInterval(interval);
    }, []);

    const getLevelColor = (level: string) => {
        switch (level) {
            case 'CRITICAL': return 'red-500';
            case 'WARNING': return 'amber-500';
            default: return 'primary';
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <div className="space-y-1">
                    <h2 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                        <ShieldCheck className="w-5 h-5 text-primary animate-pulse" /> SYSTEM_SECURITY
                    </h2>
                    <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">Protocol & Counterparty Risk Audit</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="destructive" size="sm" className="h-8 text-[10px] font-mono border-white/10 uppercase tracking-wider bg-red-500/10 hover:bg-red-500/20 text-red-500 border-red-500/20">
                        <Lock className="w-3 h-3 mr-1" /> LOCKDOWN_MODE
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Risk Status Indicators */}
                <div className="lg:col-span-1 space-y-4">
                    {riskReport?.components?.map((risk, i) => (
                        <Card key={i} className={`glass-panel border-white/10 bg-black/40 p-3 group hover:border-${getLevelColor(risk.level)}/40 transition-all`}>
                            <div className="flex items-center justify-between mb-1">
                                <div className="flex items-center gap-2">
                                    {risk.level === 'CRITICAL' ? <XCircle className="w-3 h-3 text-red-500" /> :
                                        risk.level === 'WARNING' ? <AlertTriangle className="w-3 h-3 text-amber-500" /> :
                                            <Activity className="w-3 h-3 text-primary" />}
                                    <span className="text-[10px] font-bold font-mono text-white tracking-wider">{risk.name}</span>
                                </div>
                                <div className="text-[10px] font-mono text-muted-foreground">{risk.latency || '-'}</div>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className={`text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-${getLevelColor(risk.level)}/10 text-${getLevelColor(risk.level)}`}>
                                    {risk.status}
                                </span>
                                <span className="text-[8px] font-mono text-white/40">v4.0.2</span>
                            </div>
                            {risk.details && (
                                <p className="text-[9px] text-muted-foreground mt-2 font-mono leading-tight">{risk.details}</p>
                            )}
                        </Card>
                    ))}

                    <Card className="glass-panel border-white/10 bg-primary/5 p-4 mt-6">
                        <div className="flex items-center gap-2 mb-2">
                            <CheckCircle2 className="w-4 h-4 text-primary" />
                            <span className="text-xs font-black text-white uppercase">Risk Integrity</span>
                        </div>
                        <p className="text-[10px] text-muted-foreground font-mono">
                            Counterparty monitoring active. Overall health:
                            <span className={`ml-1 font-bold text-${getLevelColor(riskReport?.overall_health || 'NORMAL')}`}>
                                {riskReport?.overall_health || 'FETCHING...'}
                            </span>
                        </p>
                    </Card>
                </div>

                {/* Audit Terminal */}
                <Card className="lg:col-span-3 glass-panel border-white/10 bg-black/80 flex flex-col h-[500px]">
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-2 min-h-[40px] flex justify-center">
                        <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground uppercase">
                            <Terminal className="w-3 h-3" /> SECURITY_AUDIT_LOG_V4.2
                        </div>
                    </CardHeader>
                    <CardContent className="flex-1 p-0 overflow-hidden relative font-mono text-xs">
                        <div className="absolute inset-0 p-4 overflow-y-auto custom-scrollbar space-y-2">
                            {[
                                { time: "16:20:45", level: "INFO", src: "RISK_MON", msg: "Stablecoin peg verification: USDC = $1.0001" },
                                { time: "16:18:12", level: "INFO", src: "BRIDGE_SVC", msg: "Polygon Bridge pulse detected. Latency: 42ms" },
                                { time: "16:15:00", level: "SUCCESS", src: "CONTRACTS", msg: "AlphaSignals Clob contract verified. No deviations." },
                                { time: "16:14:55", level: "INFO", src: "MARKET_DATA", msg: "Websocket connection re-established. Syncing risk feeds." },
                                { time: "16:10:22", level: "SUCCESS", src: "RISK_ENGINE", msg: "Pre-trade check passed. Slippage within 0.5% tolerance." },
                                { time: "16:05:01", level: "INFO", src: "SYSTEM", msg: "Scheduled Risk Scan started." },
                                { time: "16:05:05", level: "SUCCESS", src: "SYSTEM", msg: "Scheduled Risk Scan completed. No threats found." },
                            ].map((log, i) => (
                                <div key={i} className="flex gap-4 hover:bg-white/5 p-1 rounded transition-colors group">
                                    <span className="text-muted-foreground/50 w-16 shrink-0">{log.time}</span>
                                    <span className={`w-16 shrink-0 font-bold ${log.level === 'INFO' ? 'text-blue-400' : log.level === 'WARN' ? 'text-gold' : 'text-primary'}`}>[{log.level}]</span>
                                    <span className="text-purple-400 w-24 shrink-0">{log.src}</span>
                                    <span className="text-gray-300 group-hover:text-white transition-colors">{log.msg}</span>
                                </div>
                            ))}
                            <div className="animate-pulse flex gap-4 p-1">
                                <span className="text-primary w-full">_</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
