import React from 'react';

interface SentimentGaugeProps {
    score: number; // -1 (Execute Negative) to 1 (Extreme Positive)
}

export function SentimentGauge({ score }: SentimentGaugeProps) {
    // Normalize -1 to 1 range to 0 to 100 for gauge position
    const percentage = ((score + 1) / 2) * 100;

    let label = "Neutral";
    let color = "text-gray-400";

    if (score > 0.3) {
        label = "Greed / Bullish";
        color = "text-green-500";
    } else if (score < -0.3) {
        label = "Fear / Bearish";
        color = "text-red-500";
    }

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-gray-900 rounded-xl border border-gray-800">
            <h3 className="text-lg font-medium text-gray-300 mb-4">Market Sentiment</h3>

            <div className="relative w-64 h-32 overflow-hidden">
                {/* Gauge Background */}
                <div className="absolute top-0 left-0 w-full h-full bg-gray-700 rounded-t-full opacity-30"></div>

                {/* Needle */}
                <div
                    className="absolute bottom-0 left-1/2 w-1 h-28 bg-white origin-bottom transition-transform duration-1000 ease-out"
                    style={{ transform: `translateX(-50%) rotate(${(percentage * 1.8) - 90}deg)` }}
                ></div>

                {/* Center Pivot */}
                <div className="absolute bottom-0 left-1/2 w-4 h-4 bg-white rounded-full transform -translate-x-1/2 translate-y-1/2"></div>
            </div>

            <div className={`mt-4 text-2xl font-bold ${color}`}>
                {label}
            </div>
            <div className="text-sm text-gray-500">
                Score: {score.toFixed(2)}
            </div>
        </div>
    );
}
