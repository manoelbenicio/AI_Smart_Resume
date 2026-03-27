"use client";

import { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface ScoreHeroProps {
    score: number;
    tier: "Needs Work" | "Good" | "Very Good" | "Outstanding" | "Executive";
}

export function ScoreHero({ score, tier }: ScoreHeroProps) {
    const [hasMounted, setHasMounted] = useState(false);

    // Use framer-motion spring for count up effect
    const springScore = useSpring(0, {
        stiffness: 50,
        damping: 20,
        mass: 1,
        duration: 2000
    });

    const displayScore = useTransform(springScore, (latest) => Math.round(latest));

    useEffect(() => {
        setHasMounted(true);
    }, []);

    useEffect(() => {
        if (hasMounted) {
            springScore.set(score);
        }
    }, [score, springScore, hasMounted]);

    // Determine color based on tier
    let tierColor = "text-primary";
    let bgGlow = "from-primary/20 to-transparent";

    if (tier === "Needs Work") {
        tierColor = "text-destructive";
        bgGlow = "from-destructive/20 to-transparent";
    } else if (tier === "Good") {
        tierColor = "text-warning";
        bgGlow = "from-warning/20 to-transparent";
    } else if (tier === "Very Good") {
        tierColor = "text-info";
        bgGlow = "from-info/20 to-transparent";
    } else if (tier === "Outstanding") {
        tierColor = "text-success";
        bgGlow = "from-success/20 to-transparent";
    } else if (tier === "Executive") {
        tierColor = "text-primary";
        bgGlow = "from-primary/30 to-purple-500/20";
    }

    if (!hasMounted) return null;

    return (
        <div className="relative flex flex-col items-center justify-center p-8 overflow-hidden rounded-3xl glass-panel">
            {/* Background glow */}
            <div
                className={cn(
                    "absolute inset-0 bg-gradient-to-b opacity-50 pointer-events-none -z-10",
                    bgGlow
                )}
            />

            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", bounce: 0.5, duration: 1 }}
                className="flex mb-4"
            >
                <span className={cn("px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest border shadow-sm",
                    tier === "Executive" ? "bg-primary text-primary-foreground border-primary/50 shadow-primary/20" :
                        tier === "Outstanding" ? "bg-success/20 text-success border-success/30" :
                            tier === "Very Good" ? "bg-info/20 text-info border-info/30" :
                                tier === "Good" ? "bg-warning/20 text-warning border-warning/30" :
                                    "bg-destructive/20 text-destructive border-destructive/30"
                )}>
                    {tier} Tier
                </span>
            </motion.div>

            <div className="flex items-baseline relative">
                <motion.span
                    className={cn("text-8xl md:text-9xl font-black tabular-nums tracking-tighter drop-shadow-md", tierColor)}
                >
                    {displayScore}
                </motion.span>
                <span className="text-2xl md:text-3xl font-medium text-muted-foreground ml-2">/ 100</span>
            </div>

            <p className="mt-6 text-center text-muted-foreground max-w-md mx-auto">
                This is your overall Executive Check score based on industry benchmarks. Review the metrics below to close the gaps.
            </p>
        </div>
    );
}
