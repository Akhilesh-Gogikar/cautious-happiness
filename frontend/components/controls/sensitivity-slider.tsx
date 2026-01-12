'use client';

import React from 'react';
import * as Slider from '@radix-ui/react-slider';
import { cn } from '@/lib/utils';
import { ShieldAlert, ShieldCheck } from 'lucide-react';

interface SensitivitySliderProps {
    label: string;
    defaultValue?: number;
    onChange?: (value: number) => void;
    className?: string;
}

export function SensitivitySlider({
    label,
    defaultValue = 50,
    onChange,
    className
}: SensitivitySliderProps) {
    return (
        <div className={cn("flex flex-col gap-2", className)}>
            <div className="flex justify-between items-end">
                <span className="text-xs text-white/70 font-mono tracking-wide">{label}</span>
                <span className="text-[10px] text-white/30 uppercase">Risk Level</span>
            </div>

            <form className="group">
                <Slider.Root
                    className="relative flex items-center select-none touch-none w-full h-5"
                    defaultValue={[defaultValue]}
                    max={100}
                    step={1}
                    onValueChange={(vals) => onChange?.(vals[0])}
                >
                    <Slider.Track className="bg-white/10 relative grow rounded-full h-[3px] overflow-hidden">
                        <Slider.Range className="absolute bg-gradient-to-r from-emerald-500 via-yellow-500 to-red-500 rounded-full h-full" />
                    </Slider.Track>
                    <Slider.Thumb
                        className="block w-4 h-4 bg-white border-2 border-primary shadow-[0_0_10px_rgba(255,255,255,0.5)] rounded-[2px] rotate-45 hover:scale-110 focus:outline-none transition-transform"
                        aria-label="Volume"
                    />
                </Slider.Root>
            </form>

            <div className="flex justify-between px-1">
                <ShieldCheck className="w-3 h-3 text-emerald-500/50" />
                <ShieldAlert className="w-3 h-3 text-red-500/50" />
            </div>
        </div>
    );
}
