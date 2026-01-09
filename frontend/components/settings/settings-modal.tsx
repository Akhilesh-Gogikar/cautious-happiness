"use client";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings } from "lucide-react";
import { useState } from "react";

export function SettingsModal() {
    const [model, setModel] = useState("openforecaster");
    const [geminiKey, setGeminiKey] = useState("");

    const handleSave = () => {
        localStorage.setItem("POLY_MODEL", model);
        if (geminiKey) localStorage.setItem("POLY_GEMINI_KEY", geminiKey);
    };

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors">
                    <Settings className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] bg-black/90 backdrop-blur-xl border-primary/20 text-white font-mono shadow-[0_0_50px_rgba(16,185,129,0.1)]">
                <DialogHeader>
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                        <DialogTitle className="text-sm font-black tracking-[0.2em] text-primary uppercase">SYSTEM_CONFIG</DialogTitle>
                    </div>
                    <DialogDescription className="text-muted-foreground text-xs">
                        Configure Neural Engine parameters.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-6 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="model" className="text-xs font-bold text-white/50 uppercase tracking-wider">
                            Inference Model
                        </Label>
                        <Input
                            id="model"
                            value={model}
                            onChange={(e) => setModel(e.target.value)}
                            className="bg-white/5 border-white/10 text-primary font-mono text-xs focus-visible:ring-primary/50 focus-visible:border-primary/50 h-10"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="gemini" className="text-xs font-bold text-white/50 uppercase tracking-wider">
                            Gemini API Key (Critic)
                        </Label>
                        <Input
                            id="gemini"
                            type="password"
                            value={geminiKey}
                            onChange={(e) => setGeminiKey(e.target.value)}
                            placeholder="Ex: AIzaSy..."
                            className="bg-white/5 border-white/10 text-primary font-mono text-xs focus-visible:ring-primary/50 focus-visible:border-primary/50 h-10"
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button onClick={handleSave} className="w-full bg-primary text-black hover:bg-emerald-400 font-bold tracking-widest uppercase">
                        SAVE CONFIGURATION
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
