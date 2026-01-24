"use client";

import { DashboardLayout } from "@/components/layout";
import AttributionDashboard from "@/components/dashboard/attribution-dashboard";
import { BarChart2 } from "lucide-react";

export default function AttributionPage() {
    return (
        <DashboardLayout title="ATTRIBUTION" subtitle="ALPHA_DECOMPOSITION" icon={BarChart2}>
            <div className="p-6">
                <AttributionDashboard />
            </div>
        </DashboardLayout>
    );
}
