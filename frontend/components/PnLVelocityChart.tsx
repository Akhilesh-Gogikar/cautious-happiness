"use client";

import React, { useEffect, useState, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity } from "lucide-react";

interface PnLSnapshot {
    timestamp: string; // ISO string from backend
    pnl: number;
}

interface PnLVelocityResponse {
    market_id: string;
    snapshots: PnLSnapshot[];
}

interface PnLVelocityChartProps {
    marketId: string;
    wsUrl?: string; // Optional override
}

export function PnLVelocityChart({ marketId, wsUrl }: PnLVelocityChartProps) {
    const [data, setData] = useState<any[]>([]);
    const [currentPnL, setCurrentPnL] = useState<number>(0);
    const [connectionStatus, setConnectionStatus] = useState<"connected" | "disconnected" | "connecting">("connecting");
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Construct WebSocket URL
        // Defaulting to localhost:8000 for this demo context
        const url = wsUrl || `ws://localhost:8000/ws/pnl/${marketId}`;

        const connect = () => {
            setConnectionStatus("connecting");
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => {
                setConnectionStatus("connected");
                console.log("Connected to PnL Stream");
            };

            ws.onmessage = (event) => {
                try {
                    const payload: PnLVelocityResponse = JSON.parse(event.data);

                    // Format timestamps for chart
                    const newPoints = payload.snapshots.map(s => ({
                        ...s,
                        timeDisplay: new Date(s.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                        rawTime: new Date(s.timestamp).getTime()
                    }));

                    setData(prev => {
                        // If it's a bulk update (history), just take it. 
                        // If it's single update, append.
                        if (payload.snapshots.length > 1) {
                            return newPoints;
                        } else {
                            const newData = [...prev, ...newPoints];
                            // Keep last 60 points for 1-second interval
                            if (newData.length > 60) return newData.slice(newData.length - 60);
                            return newData;
                        }
                    });

                    // Update current PnL from latest snapshot
                    if (payload.snapshots.length > 0) {
                        setCurrentPnL(payload.snapshots[payload.snapshots.length - 1].pnl);
                    }

                } catch (e) {
                    console.error("Error parsing PnL data", e);
                }
            };

            ws.onclose = () => {
                setConnectionStatus("disconnected");
                // Simple retry after 5 seconds
                setTimeout(() => {
                    if (wsRef.current?.readyState === WebSocket.CLOSED) {
                        connect();
                    }
                }, 5000);
            };

            ws.onerror = (err) => {
                console.error("WebSocket error", err);
                ws.close();
            };
        };

        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [marketId, wsUrl]);

    return (
        <Card className="w-full bg-slate-950/50 border-slate-800 backdrop-blur-md text-slate-100 shadow-2xl">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 border-b border-slate-800/50 mb-4">
                <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-500 animate-pulse" />
                    <CardTitle className="text-lg font-semibold tracking-tight">
                        PnL Velocity
                    </CardTitle>
                </div>
                <div className="flex items-center space-x-3">
                    <div className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider ${connectionStatus === "connected" ? "bg-green-500/10 text-green-500 border border-green-500/20" :
                            connectionStatus === "connecting" ? "bg-yellow-500/10 text-yellow-500 border border-yellow-500/20" :
                                "bg-red-500/10 text-red-500 border border-red-500/20"
                        }`}>
                        {connectionStatus}
                    </div>
                    <div className={`text-2xl font-mono font-bold ${currentPnL >= 0 ? "text-green-400" : "text-red-400"}`}>
                        {currentPnL >= 0 ? "+" : ""}{currentPnL.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="h-[350px] w-full mt-2">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data}>
                            <defs>
                                <linearGradient id="colorPnL" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                            <XAxis
                                dataKey="timeDisplay"
                                stroke="#64748b"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                minTickGap={40}
                            />
                            <YAxis
                                stroke="#64748b"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => `$${value}`}
                                domain={['auto', 'auto']}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#020617',
                                    borderColor: '#1e293b',
                                    borderRadius: '8px',
                                    fontSize: '12px',
                                    color: '#f8fafc'
                                }}
                                itemStyle={{ color: '#60a5fa' }}
                                labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
                                cursor={{ stroke: '#334155', strokeWidth: 1 }}
                            />
                            <ReferenceLine y={0} stroke="#475569" strokeDasharray="5 5" />
                            <Line
                                type="monotone"
                                dataKey="pnl"
                                stroke="#3b82f6"
                                strokeWidth={3}
                                dot={false}
                                activeDot={{ r: 6, fill: '#3b82f6', stroke: '#020617', strokeWidth: 2 }}
                                isAnimationActive={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
                <div className="mt-4 flex justify-between text-[10px] text-slate-500 uppercase tracking-widest font-semibold">
                    <span>Market Live Correlation</span>
                    <span>Update interval: 1s</span>
                </div>
            </CardContent>
        </Card>
    );
}
