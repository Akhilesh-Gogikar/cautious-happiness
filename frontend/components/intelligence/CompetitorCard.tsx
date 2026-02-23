"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Competitor } from "./types";
import { Activity, ExternalLink } from "lucide-react";

export function CompetitorCard({ competitor, onAnalyze }: { competitor: Competitor, onAnalyze: (id: string) => void }) {
    return (
        <Card className="bg-background border-border border hover:border-primary/50 transition-colors group cursor-pointer" onClick={() => onAnalyze(competitor.id)}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium font-mono text-muted-foreground group-hover:text-primary">
                    {competitor.name}
                </CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground group-hover:text-primary animate-pulse" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold font-mono text-foreground mb-1">TRACKING</div>
                <p className="text-xs text-muted-foreground mb-4">{competitor.description}</p>
                <div className="flex flex-wrap gap-2">
                    {competitor.tracked_urls.map((url, i) => (
                        <Badge key={i} variant="outline" className="text-[10px] font-mono border-primary/20 text-primary/80">
                            {url}
                        </Badge>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
