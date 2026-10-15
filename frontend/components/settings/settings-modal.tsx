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
import { DEFAULT_LLM_MODEL, DEFAULT_LLM_PROVIDER, DEFAULT_LLAMA_CPP_URL } from "@/lib/llm-config";
import { useRouter } from "next/navigation";

export function SettingsModal() {
    const [model, setModel] = useState(DEFAULT_LLM_MODEL);
    const [llamaCppUrl, setLlamaCppUrl] = useState(DEFAULT_LLAMA_CPP_URL);
    const { user, logout } = useAuth();
    const router = useRouter();

    useEffect(() => {
        // Credentials live on the server now; drop copies earlier versions kept here.
        localStorage.removeItem("ALPACA_API_KEY");
        localStorage.removeItem("ALPACA_SECRET_KEY");

        const storedModel = localStorage.getItem("POLY_MODEL");
        const storedLlamaCppUrl = localStorage.getItem("LLAMA_CPP_URL");
        if (storedModel) setModel(storedModel);
        if (storedLlamaCppUrl) setLlamaCppUrl(storedLlamaCppUrl);
        // Earlier versions kept a Gemini key here that nothing used; drop it.
        localStorage.removeItem("POLY_GEMINI_KEY");
    }, []);

    const handleSave = () => {
        localStorage.setItem("POLY_MODEL", model || DEFAULT_LLM_MODEL);
        localStorage.setItem("LLAMA_CPP_URL", llamaCppUrl || DEFAULT_LLAMA_CPP_URL);

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
                    {user && (
                        <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                            <Label className="text-[10px] font-bold text-primary uppercase tracking-widest flex items-center justify-between">
                                <span>Signed In</span>
                                <span className="text-white/50 lowercase tracking-normal bg-black/50 px-2 py-0.5 rounded border border-white/10">{user.serverRole}</span>
                            </Label>
                            <p className="mt-2 text-xs text-white font-mono">{user.username}</p>
                        </div>
                    )}

                    <div className="space-y-4">
                        <Label className="text-[10px] font-bold text-primary uppercase tracking-widest block border-b border-primary/20 pb-1">Provider Config</Label>

                        <div className="space-y-1">
                            <p className="text-xs font-bold text-white/50 uppercase tracking-wider">Alpaca</p>
                            <p className="text-[10px] text-muted-foreground">
                                Set on the server with <span className="text-white">ALPACA_API_KEY</span> and <span className="text-white">ALPACA_SECRET_KEY</span> in <span className="text-white">.env</span>. Paper trading unless <span className="text-white">ALPACA_BASE_URL</span> points at the live API.
                            </p>
                        </div>

                        <Label className="text-[10px] font-bold text-primary uppercase tracking-widest block border-b border-primary/20 pb-1 mt-4">Model Config</Label>

                        <div className="space-y-2">
                            <Label htmlFor="model" className="text-xs font-bold text-white/50 uppercase tracking-wider">
                                Inference Model (default llama.cpp)
                            </Label>
                            <Input
                                id="model"
                                value={model}
                                onChange={(e) => setModel(e.target.value)}
                                className="bg-white/5 border-white/10 text-primary font-mono text-xs focus-visible:ring-primary/50 focus-visible:border-primary/50 h-10"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="llama-cpp-url" className="text-xs font-bold text-white/50 uppercase tracking-wider">
                                llama.cpp Service URL
                            </Label>
                            <Input
                                id="llama-cpp-url"
                                value={llamaCppUrl}
                                onChange={(e) => setLlamaCppUrl(e.target.value)}
                                placeholder="http://localhost:8080"
                                className="bg-white/5 border-white/10 text-primary font-mono text-xs focus-visible:ring-primary/50 focus-visible:border-primary/50 h-10"
                            />
                            <p className="text-[10px] text-muted-foreground">Provider: <span className="text-white">{DEFAULT_LLM_PROVIDER}</span> (fallback for all local model requests)</p>
                        </div>

                        <div className="space-y-1">
                            <p className="text-xs font-bold text-white/50 uppercase tracking-wider">Gemini (Critic)</p>
                            <p className="text-[10px] text-muted-foreground">
                                Set on the server with <span className="text-white">GEMINI_API_KEY</span> in <span className="text-white">.env</span>. Without it the critic uses the local model.
                            </p>
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
