import React, { useState } from 'react';
import { Send, Play, Save, Terminal } from 'lucide-react';
import { CodeEditor } from './CodeEditor';
import { Button } from '@/components/ui/button'; // Assuming shadcn/ui or similar
import { ScrollArea } from '@/components/ui/scroll-area';

interface Message {
    role: 'user' | 'ai';
    content: string;
}

export function StrategyBuilder() {
    const [prompt, setPrompt] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { role: 'ai', content: 'Describe a trading strategy Use natural language (e.g., "Buy Apple when RSI < 30").' }
    ]);
    const [code, setCode] = useState<string>('# Strategy code will appear here...');
    const [loading, setLoading] = useState(false);

    // Mock API Call for now - connected to backend later
    const handleGenerate = async () => {
        if (!prompt.trim()) return;

        const newMessages = [...messages, { role: 'user', content: prompt }];
        setMessages(newMessages);
        setPrompt('');
        setLoading(true);

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/strategy/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, model: 'lfm-40b' }),
            });

            const data = await res.json();

            setMessages([...newMessages, { role: 'ai', content: `Generated strategy based on "${data.logic_summary || prompt}".` }]);
            setCode(data.code || "# Error generating code");
        } catch (err) {
            setMessages([...newMessages, { role: 'ai', content: "Error connecting to Strategy Factory." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-[calc(100vh-80px)] gap-4 p-4 animate-fade-in">
            {/* Left Panel: Chat Interface */}
            <div className="w-1/3 flex flex-col glass-panel rounded-xl border border-white/10 overflow-hidden">
                <div className="p-4 border-b border-white/10 bg-black/40">
                    <h3 className="text-sm font-bold font-mono uppercase text-primary flex items-center gap-2">
                        <Terminal className="w-4 h-4" /> Strategy Architect
                    </h3>
                </div>

                <ScrollArea className="flex-1 p-4 space-y-4">
                    {messages.map((m, i) => (
                        <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg p-3 text-sm ${m.role === 'user'
                                    ? 'bg-primary/20 text-white border border-primary/20'
                                    : 'bg-white/5 text-muted-foreground border border-white/5'
                                }`}>
                                {m.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-white/5 text-xs text-primary p-2 rounded animate-pulse">
                                Thinking...
                            </div>
                        </div>
                    )}
                </ScrollArea>

                <div className="p-4 border-t border-white/10 bg-black/40">
                    <div className="relative">
                        <input
                            type="text"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                            placeholder="Describe your strategy..."
                            className="w-full bg-black/50 border border-white/10 rounded-lg pl-4 pr-10 py-3 text-sm focus:outline-none focus:border-primary/50 font-mono"
                        />
                        <button
                            onClick={() => handleGenerate()}
                            className="absolute right-2 top-2 p-1.5 rounded-md bg-primary/20 text-primary hover:bg-primary/30 transition-colors"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Right Panel: Code Editor */}
            <div className="flex-1 flex flex-col glass-panel rounded-xl border border-white/10 overflow-hidden">
                <div className="p-4 border-b border-white/10 bg-black/40 flex justify-between items-center">
                    <h3 className="text-sm font-bold font-mono uppercase text-muted-foreground">Generated_Code.py</h3>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="h-8 gap-2 border-white/10 hover:bg-white/5">
                            <Save className="w-3 h-3" /> Save
                        </Button>
                        <Button size="sm" className="h-8 gap-2 bg-emerald-500/20 text-emerald-500 hover:bg-emerald-500/30 border border-emerald-500/50">
                            <Play className="w-3 h-3" /> Backtest
                        </Button>
                    </div>
                </div>
                <div className="flex-1 bg-black/80 relative">
                    <CodeEditor code={code} onChange={setCode} />
                </div>
            </div>
        </div>
    );
}
