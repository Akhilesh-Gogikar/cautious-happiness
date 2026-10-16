"use client";

import { IntelligenceView } from '@/components/dashboard/intelligence-view';
import { AuthPending } from '@/components/auth/auth-pending';
import { useRequireAuth } from '@/lib/auth';

export default function IntelligencePage() {
    // Admins only, as in the dashboard's Intelligence view.
    const user = useRequireAuth('Admin');
    if (!user) return <AuthPending />;
    return <IntelligenceView />;
}
