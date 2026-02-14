import React from 'react';

interface NewsItem {
    id: string;
    title: string;
    source: string;
    published_at: string;
    summary: string;
    sentiment?: {
        label: string;
        score: number;
    };
    link: string;
}

interface NewsFeedProps {
    items: NewsItem[];
}

export function NewsFeed({ items }: NewsFeedProps) {
    return (
        <div className="flex flex-col space-y-4">
            <h3 className="text-lg font-medium text-gray-300">Live Intelligence Feed</h3>
            <div className="space-y-3 overflow-y-auto max-h-[600px] pr-2">
                {items.map((item) => {
                    let badgeColor = "bg-gray-700 text-gray-300";
                    if (item.sentiment?.label === "positive") badgeColor = "bg-green-900 text-green-300 border border-green-700";
                    if (item.sentiment?.label === "negative") badgeColor = "bg-red-900 text-red-300 border border-red-700";

                    return (
                        <div key={item.id} className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors">
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-xs text-gray-500">{new Date(item.published_at).toLocaleString()} • {item.source}</span>
                                {item.sentiment && (
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${badgeColor}`}>
                                        {item.sentiment.label.toUpperCase()} {(item.sentiment.score * 100).toFixed(0)}%
                                    </span>
                                )}
                            </div>
                            <a href={item.link} target="_blank" rel="noopener noreferrer" className="block group">
                                <h4 className="text-sm font-semibold text-gray-200 group-hover:text-blue-400 transition-colors mb-1">
                                    {item.title}
                                </h4>
                                <p className="text-xs text-gray-400 line-clamp-2">
                                    {item.summary}
                                </p>
                            </a>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
