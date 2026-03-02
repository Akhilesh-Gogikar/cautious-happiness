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
import { useAuth } from "@/lib/auth";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export function SettingsModal() {
    const [model, setModel] = useState("lfm-thinking");
    const [geminiKey, setGeminiKey] = useState("");
    const [alpacaKey, setAlpacaKey] = useState("");
    const [alpacaSecret, setAlpacaSecret] = useState("");
    const { user, toggleRole, logout } = useAuth();
    const router = useRouter();

    useEffect(() => {
        const storedAlpacaKey = localStorage.getItem("ALPACA_API_KEY");
        const storedAlpacaSecret = localStorage.getItem("ALPACA_SECRET_KEY");
        if (storedAlpacaKey) setAlpacaKey(storedAlpacaKey);
        if (storedAlpacaSecret) setAlpacaSecret(storedAlpacaSecret);

        const storedModel = localStorage.getItem("POLY_MODEL");
        const storedGeminiKey = localStorage.getItem("POLY_GEMINI_KEY");
        if (storedModel) setModel(storedModel);
        if (storedGeminiKey) setGeminiKey(storedGeminiKey);
    }, []);

    const handleSave = () => {
        localStorage.setItem("POLY_MODEL", model);
        if (geminiKey) localStorage.setItem("POLY_GEMINI_KEY", geminiKey);

        if (alpacaKey) localStorage.setItem("ALPACA_API_KEY", alpacaKey);
        if (alpacaSecret) localStorage.setItem("ALPACA_SECRET_KEY", alpacaSecret);
    };

    const handleLogout = () => {
        logout();
        router.push("/login"); // Need to import useRouter
    }

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
                        Configure Neural Engine parameters and Access Control.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-6 py-4 max-h-[60vh] overflow-y-auto">
                    {/* Role Switcher for Admin Only */}
                    {user?.email.toLowerCase() === 'aki@onenew.ai' && (
                        <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg space-y-3">
                            <Label className="text-[10px] font-bold text-primary uppercase tracking-widest flex items-center justify-between">
                                <span>Demo Controls</span>
                                <span className="text-white/50 lowercase tracking-normal bg-black/50 px-2 py-0.5 rounded border border-white/10">Active: {user.role}</span>
                            </Label>
                            <Button
                                variant="outline"
                                onClick={toggleRole}
                                className="w-full text-xs font-mono border-primary/30 hover:bg-primary hover:text-black transition-colors"
                            >
                                Switch to {user.role === 'Admin' ? 'User' : 'Admin'} Role
                            </Button>
                        </div>
                    )}

                    <div className="space-y-4">
                        <Label className="text-[10px] font-bold text-primary uppercase tracking-widest block border-b border-primary/20 pb-1">Provider Config</Label>

                        <div className="space-y-2">
                            <Label htmlFor="alpaca-key" className="text-xs font-bold text-white/50 uppercase tracking-wider">
                                Alpaca API Key
                            </Label>
                            <Input
                                id="alpaca-key"
                                type="password"
                                value={alpacaKey}
                                onChange={(e) => setAlpacaKey(e.target.value)}
                                placeholder="PK..."
                                className="bg-white/5 border-white/10 text-primary font-mono text-xs focus-visible:ring-primary/50 focus-visible:border-primary/50 h-10"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="alpaca-secret" className="text-xs font-bold text-white/50 uppercase tracking-wider">
                                Alpaca Secret Key
                            </Label>
                            <Input
                                id="alpaca-secret"
                                type="password"
                                value={alpacaSecret}
                                onChange={(e) => setAlpacaSecret(e.target.value)}
                                placeholder="..."
                                className="bg-white/5 border-white/10 text-primary font-mono text-xs focus-visible:ring-primary/50 focus-visible:border-primary/50 h-10"
                            />
                        </div>

                        <Label className="text-[10px] font-bold text-primary uppercase tracking-widest block border-b border-primary/20 pb-1 mt-4">Model Config</Label>

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
                </div>
                <DialogFooter className="flex-col sm:flex-col gap-2 mt-4">
                    <Button onClick={handleSave} className="w-full bg-primary text-black hover:bg-emerald-400 font-bold tracking-widest uppercase">
                        SAVE CONFIGURATION
                    </Button>
                    {user && (
                        <Button onClick={handleLogout} variant="outline" className="w-full text-red-500 border-red-500/30 hover:bg-red-500/10 font-bold tracking-widest uppercase mt-2 sm:mt-0">
                            LOGOUT OPERATOR
                        </Button>
                    )}
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
