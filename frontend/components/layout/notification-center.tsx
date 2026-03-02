"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Bell, AlertTriangle, Info, CheckCircle, BrainCircuit, X } from 'lucide-react';

type NotificationUrgency = 'green' | 'yellow' | 'red';

interface NotificationItem {
    id: string;
    title: string;
    message: string;
    urgency: NotificationUrgency;
    timestamp: string;
    read: boolean;
    source: 'system' | 'trade' | 'macro' | 'ai';
}

const MOCK_NOTIFICATIONS: NotificationItem[] = [
    {
        id: '1',
        title: 'Critical Margin Alert',
        message: 'Account margin utilization exceeded 85%. Immediate action required.',
        urgency: 'red',
        timestamp: 'Just now',
        read: false,
        source: 'system',
    },
    {
        id: '2',
        title: 'Macro Regime Shift Detected',
        message: 'AI Neural Core detected 3-sigma deviation in Physical Premium correlating with generic algo flows.',
        urgency: 'yellow',
        timestamp: '2m ago',
        read: false,
        source: 'ai',
    },
    {
        id: '3',
        title: 'Trade Executed',
        message: 'Bought 50 WTI Crude @ $82.45',
        urgency: 'green',
        timestamp: '15m ago',
        read: true,
        source: 'trade',
    },
    {
        id: '4',
        title: 'System Optimal',
        message: 'All localized prediction models are synced and running optimally.',
        urgency: 'green',
        timestamp: '1h ago',
        read: true,
        source: 'system',
    },
];

const getUrgencyColor = (urgency: NotificationUrgency) => {
    switch (urgency) {
        case 'red': return 'text-destructive bg-destructive/10 border-destructive/20';
        case 'yellow': return 'text-gold bg-gold/10 border-gold/20';
        case 'green': return 'text-primary bg-primary/10 border-primary/20';
        default: return 'text-muted-foreground bg-white/5 border-white/10';
    }
};

const getSourceIcon = (source: NotificationItem['source'], urgency: NotificationUrgency) => {
    const className = `w-4 h-4 ${getUrgencyColor(urgency).split(' ')[0]}`;
    switch (source) {
        case 'system': return <Info className={className} />;
        case 'trade': return <CheckCircle className={className} />;
        case 'macro': return <AlertTriangle className={className} />;
        case 'ai': return <BrainCircuit className={className} />;
    }
};

export function NotificationCenter() {
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState<NotificationItem[]>(MOCK_NOTIFICATIONS);
    const popoverRef = useRef<HTMLDivElement>(null);

    const unreadCount = notifications.filter(n => !n.read).length;

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

    const markAsRead = (id: string) => {
        setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
    };

    const markAllAsRead = () => {
        setNotifications(notifications.map(n => ({ ...n, read: true })));
    };

    const dismiss = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setNotifications(notifications.filter(n => n.id !== id));
    };

    return (
        <div className="relative" ref={popoverRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group flex items-center justify-center h-[38px] w-[38px]"
            >
                <Bell className="w-4 h-4 text-muted-foreground group-hover:text-white transition-colors" />
                {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[9px] font-bold text-white shadow-[0_0_10px_rgba(239,68,68,0.5)]">
                        {unreadCount}
                    </span>
                )}
            </button>

            {isOpen && (
                <div className="absolute top-full right-0 mt-2 w-80 sm:w-96 bg-black/90 border border-white/10 rounded-xl shadow-2xl backdrop-blur-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/[0.02]">
                        <h3 className="font-bold text-sm tracking-wider text-white flex items-center gap-2">
                            NOTIFICATIONS
                            {unreadCount > 0 && (
                                <span className="px-1.5 py-0.5 rounded-sm bg-primary/20 text-primary text-[10px] font-mono">
                                    {unreadCount} NEW
                                </span>
                            )}
                        </h3>
                        {unreadCount > 0 && (
                            <button
                                onClick={markAllAsRead}
                                className="text-[10px] text-muted-foreground hover:text-white transition-colors font-mono uppercase"
                            >
                                Mark all read
                            </button>
                        )}
                    </div>

                    <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
                        {notifications.length === 0 ? (
                            <div className="px-4 py-8 text-center flex flex-col items-center gap-2 justify-center">
                                <CheckCircle className="w-8 h-8 text-muted-foreground/30" />
                                <p className="text-sm text-muted-foreground font-mono">No new notifications</p>
                            </div>
                        ) : (
                            <div className="flex flex-col">
                                {notifications.map((notification) => (
                                    <div
                                        key={notification.id}
                                        onClick={() => markAsRead(notification.id)}
                                        className={`group relative flex items-start gap-3 p-4 border-b border-white/5 hover:bg-white/[0.04] transition-colors cursor-pointer ${
                                            !notification.read ? 'bg-white/[0.02]' : ''
                                        }`}
                                    >
                                        {!notification.read && (
                                            <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary" />
                                        )}
                                        <div className={`mt-0.5 p-1.5 rounded-md border ${getUrgencyColor(notification.urgency)} shrink-0`}>
                                            {getSourceIcon(notification.source, notification.urgency)}
                                        </div>
                                        <div className="flex-1 min-w-0 pr-6">
                                            <div className="flex items-center justify-between gap-2 mb-1">
                                                <p className={`text-sm font-bold truncate ${!notification.read ? 'text-white' : 'text-gray-300'}`}>
                                                    {notification.title}
                                                </p>
                                                <span className="text-[10px] font-mono text-muted-foreground shrink-0 tabular-nums">
                                                    {notification.timestamp}
                                                </span>
                                            </div>
                                            <p className={`text-xs leading-relaxed ${!notification.read ? 'text-gray-300' : 'text-muted-foreground'}`}>
                                                {notification.message}
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => dismiss(notification.id, e)}
                                            className="absolute right-4 top-4 p-1 text-muted-foreground/50 hover:text-white hover:bg-white/10 rounded-md transition-all opacity-0 group-hover:opacity-100"
                                        >
                                            <X className="w-3 h-3" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="p-2 border-t border-white/10 bg-white/[0.02] text-center">
                        <button className="text-[10px] text-muted-foreground hover:text-white transition-colors font-mono uppercase tracking-widest w-full py-1">
                            View Archive
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
