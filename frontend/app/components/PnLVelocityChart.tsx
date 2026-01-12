"use client";

import React, { useEffect, useState, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

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
            timeDisplay: new Date(s.timestamp).toLocaleTimeString(),
            rawTime: new Date(s.timestamp).getTime()
          }));

          setData(prev => {
            // Keep last 100 points effectively
            // If it's a bulk update (history), just take it. 
            // If it's single update, append.
            if (payload.snapshots.length > 1) {
              return newPoints;
            } else {
              const newData = [...prev, ...newPoints];
              if (newData.length > 100) return newData.slice(newData.length - 100);
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
        // Reconnect logic could go here
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
    <Card className="w-full bg-slate-950 border-slate-800 text-slate-100">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-400">
          PnL Velocity (real-time)
        </CardTitle>
        <div className="flex items-center space-x-2">
           <Badge variant={connectionStatus === "connected" ? "default" : "destructive"}>
             {connectionStatus}
           </Badge>
           <span className={`text-xl font-bold ${currentPnL >= 0 ? "text-green-500" : "text-red-500"}`}>
             {currentPnL >= 0 ? "+" : ""}${currentPnL.toFixed(2)}
           </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis 
                dataKey="timeDisplay" 
                stroke="#94a3b8" 
                fontSize={12} 
                tickLine={false}
                axisLine={false}
                minTickGap={30}
              />
              <YAxis 
                stroke="#94a3b8" 
                fontSize={12} 
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
              <Line 
                type="monotone" 
                dataKey="pnl" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#60a5fa' }}
                isAnimationActive={false} // Disable animation for smoother streaming
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
