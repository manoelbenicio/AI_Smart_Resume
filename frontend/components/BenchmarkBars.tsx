"use client";

import { motion } from "framer-motion";

interface BenchmarkBarsProps {
    score: number;
}

export function BenchmarkBars({ score }: BenchmarkBarsProps) {
    const benchmarks = [
        { label: "Executive (Top 1%)", range: [90, 100], color: "bg-primary" },
        { label: "Outstanding (Top 5%)", range: [80, 89], color: "bg-success" },
        { label: "Very Good (Top 20%)", range: [70, 79], color: "bg-info" },
        { label: "Good (Average)", range: [50, 69], color: "bg-warning" },
        { label: "Needs Work (Bottom 50%)", range: [0, 49], color: "bg-destructive" },
    ];

    return (
        <div className="w-full space-y-5 p-6 glass-panel rounded-2xl">
            <div className="mb-4">
                <h3 className="text-xl font-bold text-foreground">Industry Benchmarks</h3>
                <p className="text-sm text-muted-foreground mt-1">How your CV compares to peer applications in the market.</p>
            </div>

            <div className="space-y-4">
                {benchmarks.map((b, i) => {
                    const isActive = score >= b.range[0] && score <= (b.range[1] === 100 ? 100 : b.range[1] + 0.99);
                    // Calculate percentage width relative to the maximum score (100) or scaled.
                    // Since ranges define the bucket, let's just make the width proportional to range max.
                    const fillWidth = `${b.range[1]}%`;

                    return (
                        <div key={b.label} className="relative flex flex-col space-y-1.5">
                            <div className="flex justify-between items-center text-sm font-medium">
                                <span className={isActive ? "text-foreground font-bold flex items-center" : "text-muted-foreground"}>
                                    {b.label}
                                    {isActive && <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="ml-2 text-xs px-2 py-0.5 bg-border rounded text-foreground">Your Tier</motion.span>}
                                </span>
                                <span className="text-xs text-muted-foreground">{b.range[0]}-{b.range[1]}</span>
                            </div>

                            <div className="w-full h-3 bg-muted rounded-full overflow-hidden relative">
                                <motion.div
                                    initial={{ width: 0 }}
                                    whileInView={{ width: fillWidth }}
                                    viewport={{ once: true }}
                                    transition={{ duration: 1, delay: i * 0.1, ease: "easeOut" }}
                                    className={`h-full rounded-full ${isActive ? b.color : 'bg-muted-foreground/30'}`}
                                />
                                {isActive && (
                                    <motion.div
                                        initial={{ left: 0 }}
                                        animate={{ left: `${score}%` }}
                                        transition={{ type: "spring", stiffness: 50, delay: 0.5 }}
                                        className="absolute top-0 bottom-0 w-1.5 bg-foreground border border-background z-10 -ml-[1px]"
                                    />
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
