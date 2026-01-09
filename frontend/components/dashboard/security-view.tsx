"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, Lock, Terminal, Activity, CheckCircle2 } from 'lucide-react';
import { Button } from "@/components/ui/button";

export function SecurityView() {
    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <div className="space-y-1">
                    <h2 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                        <ShieldCheck className="w-5 h-5 text-primary animate-pulse" /> SYSTEM_SECURITY
                    </h2>
                    <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">Audit Logs & Integrity Checks</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="destructive" size="sm" className="h-8 text-[10px] font-mono border-white/10 uppercase tracking-wider bg-red-500/10 hover:bg-red-500/20 text-red-500 border-red-500/20">
                        <Lock className="w-3 h-3 mr-1" /> LOCKDOWN_MODE
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* System Status Indicators */}
                <div className="lg:col-span-1 space-y-4">
                    {[
                        { name: "API_GATEWAY", status: "ONLINE", latency: "12ms", color: "primary" },
                        { name: "EXECUTION_ENGINE", status: "ONLINE", latency: "4ms", color: "primary" },
                        { name: "REDIS_CACHE", status: "ONLINE", latency: "1ms", color: "primary" },
                        { name: "OLLAMA_INFERENCE", status: "PROCESSING", latency: "240ms", color: "gold" },
                        { name: "OLLAMA_FORECASTER_LLM", status: "ONLINE", latency: "15ms", color: "primary" },
                        { name: "SIGNING_MODULE", status: "SECURE", latency: "-", color: "primary" },
                    ].map((service, i) => (
                        <Card key={i} className="glass-panel border-white/10 bg-black/40 p-3 flex items-center justify-between group hover:border-white/20 transition-colors">
                            <div className="flex items-center gap-3">
                                <div className={`w-2 h-2 rounded-full bg-${service.color} shadow-[0_0_8px_currentColor] text-${service.color}`} />
                                <span className="text-[10px] font-bold font-mono text-white tracking-wider">{service.name}</span>
                            </div>
                            <div className="text-[10px] font-mono text-muted-foreground">{service.latency}</div>
                        </Card>
                    ))}

                    <Card className="glass-panel border-white/10 bg-primary/5 p-4 mt-6">
                        <div className="flex items-center gap-2 mb-2">
                            <CheckCircle2 className="w-4 h-4 text-primary" />
                            <span className="text-xs font-black text-white uppercase">System Integrity</span>
                        </div>
                        <p className="text-[10px] text-muted-foreground font-mono">All checksums match. No unauthorized access attempts detected in last 24h.</p>
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
                                { time: "16:20:45", level: "INFO", src: "AUTH_SVC", msg: "Admin session validated for user: 0x8f...2a" },
                                { time: "16:18:12", level: "INFO", src: "EXEC_ENGINE", msg: "Strategy 'MeanRev' updated parameters. Signed by key 2." },
                                { time: "16:15:00", level: "WARN", src: "OLLAMA", msg: "Inference latency spike > 500ms detected. Auto-scaling..." },
                                { time: "16:14:55", level: "INFO", src: "MARKET_DATA", msg: "Websocket connection re-established. Syncing orderbook." },
                                { time: "16:10:22", level: "SUCCESS", src: "RISK_ENGINE", msg: "Pre-trade check passed. Slippage within 0.5% tolerance." },
                                { time: "16:05:01", level: "INFO", src: "SYSTEM", msg: "ScheduledDBBackup started." },
                                { time: "16:05:05", level: "SUCCESS", src: "SYSTEM", msg: "ScheduledDBBackup completed. Size: 4.2GB." },
                                { time: "15:58:30", level: "INFO", src: "AUTH_SVC", msg: "New API key generated for service: ALPHA_SCANNER." },
                                { time: "15:45:12", level: "WARN", src: "NET_MESH", msg: "Packet loss 0.01% on node us-east-4." },
                                { time: "15:30:00", level: "INFO", src: "OLLAMA", msg: "Model 'openforecaster' loaded into VRAM." },
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
