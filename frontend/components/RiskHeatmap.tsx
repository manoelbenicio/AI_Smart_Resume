"use client";

import { RiskAssessment } from "@/lib/types";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { AlertTriangle, AlertCircle, CheckCircle, ShieldAlert } from "lucide-react";

interface RiskHeatmapProps {
    assessment: RiskAssessment;
}

export function RiskHeatmap({ assessment }: RiskHeatmapProps) {
    const getRiskIcon = (level: string) => {
        switch (level) {
            case "Critical": return <ShieldAlert className="w-5 h-5 text-destructive" />;
            case "High": return <AlertTriangle className="w-5 h-5 text-destructive" />;
            case "Medium": return <AlertCircle className="w-5 h-5 text-warning" />;
            default: return <CheckCircle className="w-5 h-5 text-success" />;
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case "Critical": return "from-destructive/20 to-destructive/5 text-destructive border-destructive/20";
            case "High": return "from-destructive/20 to-destructive/5 text-destructive border-destructive/20";
            case "Medium": return "from-warning/20 to-warning/5 text-warning border-warning/20";
            default: return "from-success/20 to-success/5 text-success border-success/20";
        }
    };

    const calculateComponentLevel = (probability: string[]) => {
        if (probability.some(p => p.includes("High"))) return "High";
        if (probability.some(p => p.includes("Medium"))) return "Medium";
        return "Low";
    };

    const components = [
        { key: "format_risk", label: "Format & Structure", data: assessment.components.format_risk },
        { key: "content_risk", label: "Content Quality", data: assessment.components.content_risk },
        { key: "ats_risk", label: "ATS Compatibility", data: assessment.components.ats_risk },
        { key: "alignment_risk", label: "Role Alignment", data: assessment.components.alignment_risk },
        { key: "timeline_risk", label: "Career Timeline", data: assessment.components.timeline_risk },
    ];

    return (
        <div className="w-full space-y-6">
            <div className={`p-4 rounded-xl border bg-gradient-to-br flex items-center justify-between shadow-sm ${getRiskColor(assessment.overall_risk_level)}`}>
                <div className="flex items-center gap-3">
                    {getRiskIcon(assessment.overall_risk_level)}
                    <div>
                        <h3 className="font-bold">Overall Risk Level</h3>
                        <p className="text-sm opacity-80">Probability of automated rejection</p>
                    </div>
                </div>
                <div className="text-2xl font-black uppercase tracking-widest">
                    {assessment.overall_risk_level}
                </div>
            </div>

            <Accordion className="w-full space-y-3">
                {components.map((comp) => {
                    const level = calculateComponentLevel(comp.data.probability);
                    return (
                        <AccordionItem value={comp.key} key={comp.key} className="glass-panel border px-4 rounded-xl">
                            <AccordionTrigger className="hover:no-underline py-4">
                                <div className="flex items-center gap-3 w-full">
                                    {getRiskIcon(level)}
                                    <span className="font-semibold text-foreground">{comp.label}</span>
                                    <span className={`ml-auto text-xs px-2 py-1 rounded-md font-bold ${getRiskColor(level).split(" ")[0]} ${getRiskColor(level).split(" ")[2]}`}>
                                        {level} Risk
                                    </span>
                                </div>
                            </AccordionTrigger>
                            <AccordionContent className="pb-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                                    <div className="space-y-3">
                                        <div>
                                            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">Impact</h4>
                                            <ul className="list-disc pl-4 space-y-1">
                                                {comp.data.impact.map((i, idx) => (
                                                    <li key={idx} className="text-sm text-foreground/90">{i}</li>
                                                ))}
                                            </ul>
                                        </div>
                                        <div>
                                            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">Probability</h4>
                                            <ul className="list-disc pl-4 space-y-1">
                                                {comp.data.probability.map((p, idx) => (
                                                    <li key={idx} className="text-sm text-foreground/90">{p}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                    <div className="bg-primary/5 border border-primary/20 rounded-lg p-3">
                                        <h4 className="text-xs font-bold text-primary uppercase tracking-wider mb-2">Mitigations</h4>
                                        <ul className="list-disc pl-4 space-y-1">
                                            {comp.data.mitigations.map((m, idx) => (
                                                <li key={idx} className="text-sm text-primary/90">{m}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </AccordionContent>
                        </AccordionItem>
                    );
                })}
            </Accordion>
        </div>
    );
}
