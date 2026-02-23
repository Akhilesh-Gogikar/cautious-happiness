"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface SentimentGaugeProps {
    score: number; // -1.0 to 1.0
    conviction: number; // 0.0 to 1.0
}

export function SentimentGauge({ score, conviction }: SentimentGaugeProps) {
    // Navigate from Red (-1) to Green (1). 0 is Grey.
    const percentage = ((score + 1) / 2) * 100;

    let colorClass = "bg-gray-500";
    let textClass = "text-gray-400";
    let label = "NEUTRAL";

    if (score > 0.2) {
        colorClass = "bg-emerald-500";
        textClass = "text-emerald-500";
        label = "BULLISH";
    } else if (score < -0.2) {
        colorClass = "bg-red-500";
        textClass = "text-red-500";
        label = "BEARISH";
    }

    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">CROWD SENTIMENT</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="relative w-full h-4 bg-secondary rounded-full overflow-hidden">
                        <div
                            className={cn("absolute top-0 bottom-0 transition-all duration-1000 ease-out", colorClass)}
                            style={{ left: `${percentage}%`, width: '4px', transform: 'translateX(-2px)' }}
                        />
                        {/* Center Marker */}
                        <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-white/20" />
                    </div>

                    <div className="flex justify-between w-full text-xs font-mono text-muted-foreground">
                        <span>BEARISH</span>
                        <span>NEUTRAL</span>
                        <span>BULLISH</span>
                    </div>

                    <div className="text-center">
                        <div className={cn("text-3xl font-bold font-mono tracking-tighter", textClass)}>
                            {label}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                            CONVICTION: <span className="text-foreground">{(conviction * 100).toFixed(0)}%</span>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
