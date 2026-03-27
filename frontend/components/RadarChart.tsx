"use client";

import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart as RechartsRadar, ResponsiveContainer } from "recharts";
import { Metrics } from "@/lib/types";
import { useMemo } from "react";

interface MetricsRadarProps {
    metrics: Metrics;
}

export function MetricsRadar({ metrics }: MetricsRadarProps) {
    const data = useMemo(() => {
        return [
            { subject: "Impact", A: metrics.impact_metrics.score, fullMark: 100 },
            { subject: "Action Verbs", A: metrics.action_verbs.score, fullMark: 100 },
            { subject: "Brevity", A: metrics.clarity_brevity.score, fullMark: 100 },
            { subject: "ATS", A: metrics.ats_compatibility.score, fullMark: 100 },
            { subject: "Keywords", A: metrics.keyword_optimization.score, fullMark: 100 },
            { subject: "Skills", A: metrics.skills_alignment.score, fullMark: 100 },
            { subject: "Executive", A: metrics.executive_presence.score, fullMark: 100 },
            { subject: "Structure", A: metrics.format_structure.score, fullMark: 100 },
        ];
    }, [metrics]);

    return (
        <div className="w-full h-80 glass-panel rounded-2xl p-4 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
                <RechartsRadar cx="50%" cy="50%" outerRadius="70%" data={data}>
                    <PolarGrid stroke="hsl(var(--muted-foreground))" strokeOpacity={0.2} />
                    <PolarAngleAxis
                        dataKey="subject"
                        tick={{ fill: "hsl(var(--foreground))", fontSize: 12, fontWeight: 500 }}
                    />
                    <PolarRadiusAxis
                        angle={30}
                        domain={[0, 100]}
                        tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                        tickCount={6}
                    />
                    <Radar
                        name="Score"
                        dataKey="A"
                        stroke="hsl(var(--primary))"
                        fill="hsl(var(--primary))"
                        fillOpacity={0.5}
                        animationDuration={1500}
                        animationEasing="ease-out"
                    />
                </RechartsRadar>
            </ResponsiveContainer>
        </div>
    );
}
