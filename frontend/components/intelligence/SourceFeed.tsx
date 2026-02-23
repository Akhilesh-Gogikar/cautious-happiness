"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Source } from "./types";
import { ExternalLink, Clock } from "lucide-react";

export function SourceFeed({ sources }: { sources: Source[] }) {
    if (!sources || sources.length === 0) {
        return (
            <div className="text-center text-muted-foreground py-8 text-sm font-mono">
                AWAITING INTELLIGENCE STREAMS...
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {sources.map((source) => (
                <Card key={source.id} className="bg-background/50 border-input">
                    <CardContent className="p-3">
                        <div className="flex justify-between items-start mb-1">
                            <Badge variant="secondary" className="text-[10px] h-5 mb-1 opacity-70">
                                {source.domain}
                            </Badge>
                            <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors">
                                <ExternalLink className="h-3 w-3" />
                            </a>
                        </div>
                        <h4 className="text-sm font-semibold mb-1 line-clamp-1 group-hover:text-primary transition-colors">
                            {source.title}
                        </h4>
                        <p className="text-xs text-muted-foreground line-clamp-2 font-mono leading-relaxed opacity-80">
                            {source.snippet}
                        </p>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
