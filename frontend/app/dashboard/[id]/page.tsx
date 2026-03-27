"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getRun, getDownloadUrl } from "@/lib/api";
import { AnalyzeResponse } from "@/lib/types";
import { ScoreHero } from "@/components/ScoreHero";
import { MetricsRadar } from "@/components/RadarChart";
import { BenchmarkBars } from "@/components/BenchmarkBars";
import { RiskHeatmap } from "@/components/RiskHeatmap";
import { Button } from "@/components/ui/button";
import { Loader2, Download, ArrowLeft, Lightbulb, AlertTriangle, CheckCircle2 } from "lucide-react";

export default function Dashboard() {
    const params = useParams();
    const router = useRouter();
    const id = params.id as string;

    const [data, setData] = useState<AnalyzeResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return;

        let isMounted = true;
        async function fetchData() {
            try {
                const res = await getRun(id);
                if (isMounted) setData(res);
            } catch (err: unknown) {
                if (isMounted) setError(err instanceof Error ? err.message : "Failed to load analysis.");
            } finally {
                if (isMounted) setLoading(false);
            }
        }

        fetchData();

        return () => { isMounted = false; };
    }, [id]);

    if (loading) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center min-h-[60vh]">
                <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-6" />
                <h2 className="text-2xl font-bold animate-pulse">Running Deep Analysis...</h2>
                <p className="text-muted-foreground mt-2 max-w-md">
                    Evaluating structural integrity, ATS parsability, and executive impact across industry benchmarks.
                </p>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="flex flex-col items-center justify-center flex-1 p-12">
                <AlertTriangle className="w-12 h-12 text-destructive mb-4" />
                <h2 className="text-xl font-bold text-destructive">Analysis Not Found</h2>
                <p className="text-muted-foreground mt-2">{error}</p>
                <Button variant="outline" className="mt-6" onClick={() => router.push("/")}>
                    Return Home
                </Button>
            </div>
        );
    }

    const { analysis, risk_assessment } = data;

    return (
        <div className="flex flex-col w-full max-w-7xl mx-auto px-4 py-8 space-y-8 animate-in fade-in duration-700">

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <Button variant="ghost" size="sm" onClick={() => router.push("/")} className="w-fit">
                    <ArrowLeft className="w-4 h-4 mr-2" /> New Analysis
                </Button>
                <div className="flex gap-3">
                    <Button onClick={() => window.open(getDownloadUrl(id), '_blank')} className="font-semibold shadow-md">
                        <Download className="w-4 h-4 mr-2" />
                        Download Optimized DOCX
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Score & Benchmarks */}
                <div className="space-y-8 lg:col-span-1">
                    <ScoreHero score={analysis.overall_score} tier={analysis.tier} />
                    <BenchmarkBars score={analysis.overall_score} />

                    <div className="glass-panel p-6 rounded-2xl">
                        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-success" />
                            Key Strengths
                        </h3>
                        <ul className="space-y-3">
                            {analysis.key_strengths.map((str, idx) => (
                                <li key={idx} className="flex gap-2 text-sm text-foreground/90">
                                    <span className="text-success mt-0.5">•</span>
                                    {str}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Middle/Right Column: Details */}
                <div className="space-y-8 lg:col-span-2">

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="glass-panel p-4 rounded-2xl flex flex-col justify-center">
                            <h3 className="text-lg font-bold mb-2 ml-4">Metric Radar</h3>
                            <MetricsRadar metrics={analysis.metrics} />
                        </div>

                        <div className="glass-panel p-6 rounded-2xl flex flex-col">
                            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5 text-warning" />
                                Actionable Gaps
                            </h3>
                            <div className="flex-1 overflow-y-auto space-y-4 max-h-[320px] pr-2 custom-scrollbar">
                                {analysis.actionable_gaps.map((gap, idx) => (
                                    <div key={idx} className="p-4 rounded-xl border bg-background/50 space-y-2">
                                        <div className="flex items-center justify-between">
                                            <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase ${gap.priority === 'High' ? 'bg-destructive/20 text-destructive' :
                                                gap.priority === 'Medium' ? 'bg-warning/20 text-warning' :
                                                    'bg-info/20 text-info'
                                                }`}>
                                                {gap.priority}
                                            </span>
                                        </div>
                                        <p className="text-sm font-semibold text-foreground">{gap.issue}</p>
                                        <p className="text-xs text-muted-foreground">{gap.recommendation}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="glass-panel p-6 rounded-2xl">
                        <h3 className="text-lg font-bold mb-4">Risk Assessment</h3>
                        <RiskHeatmap assessment={risk_assessment} />
                    </div>

                    <div className="glass-panel p-6 rounded-2xl space-y-4">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Lightbulb className="w-5 h-5 text-primary" />
                            Improvement Plan
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="p-4 bg-destructive/5 rounded-xl border border-destructive/10">
                                <h4 className="font-semibold text-sm mb-2 text-destructive">Critical Fixes</h4>
                                <ul className="list-disc pl-4 space-y-1 text-xs text-foreground/80">
                                    {analysis.improvement_plan.critical_fixes.map((f, i) => <li key={i}>{f}</li>)}
                                </ul>
                            </div>
                            <div className="p-4 bg-warning/5 rounded-xl border border-warning/10">
                                <h4 className="font-semibold text-sm mb-2 text-warning">Quick Wins</h4>
                                <ul className="list-disc pl-4 space-y-1 text-xs text-foreground/80">
                                    {analysis.improvement_plan.quick_wins.map((f, i) => <li key={i}>{f}</li>)}
                                </ul>
                            </div>
                            <div className="p-4 bg-info/5 rounded-xl border border-info/10">
                                <h4 className="font-semibold text-sm mb-2 text-info">Long-term Strategy</h4>
                                <ul className="list-disc pl-4 space-y-1 text-xs text-foreground/80">
                                    {analysis.improvement_plan.long_term_strategy.map((f, i) => <li key={i}>{f}</li>)}
                                </ul>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            {/* Footer safe spacing */}
            <div className="h-12" />
        </div>
    );
}
