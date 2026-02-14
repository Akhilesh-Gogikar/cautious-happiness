import React, { useState } from 'react';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python'; // Add python support since it is for strategy
import { cn } from '@/lib/utils'; // Assuming cn utility exists, checking imports

interface CodeEditorProps {
    code: string;
    onChange: (value: string) => void;
    language?: string;
}

export function CodeEditor({ code, onChange, language = 'javascript' }: CodeEditorProps) {
    const [focused, setFocused] = useState(false);

    // Simple line number generation
    const lineNumbers = code.split('\n').map((_, i) => i + 1);

    return (
        <div
            className={cn(
                "relative w-full h-full flex flex-row overflow-hidden rounded-md border text-sm font-mono transition-colors",
                focused ? "border-primary/50 bg-black/40" : "border-white/10 bg-black/20"
            )}
        >
            {/* Line Numbers */}
            <div className="flex-none w-12 py-4 text-right pr-3 select-none bg-black/30 text-white/30 border-r border-white/5">
                {lineNumbers.map((num) => (
                    <div key={num} className="leading-relaxed h-[24px]">{num}</div> // 24px matches 1.5 line-height of 16px font or similar
                ))}
            </div>

            {/* Editor Area */}
            <div className="flex-1 relative overflow-auto custom-scrollbar">
                <Editor
                    value={code}
                    onValueChange={onChange}
                    highlight={code => highlight(code, languages.js, 'javascript')} // Defaulting to JS for now, can be dynamic
                    padding={16}
                    className="font-mono text-[13px] leading-relaxed"
                    style={{
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: 13,
                        backgroundColor: 'transparent',
                        minHeight: '100%',
                    }}
                    textareaClassName="focus:outline-none"
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                />
            </div>

            {/* Syntax language indicator */}
            <div className="absolute top-2 right-4 text-[10px] text-white/20 uppercase tracking-wider pointer-events-none">
                {language}
            </div>
        </div>
    );
}
