/**
 * Frontend Types matching the FastAPI Backend Contract
 */

export interface AnalyzeRequest {
    cv_text: string;
    jd_text?: string;
    job_title?: string;
    job_url?: string;
    focus_areas?: string[];
    strict_mode?: boolean;
}

export interface AuthRequest {
    action: "login" | "register";
    email: string;
    password: string;
    full_name?: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: "bearer";
}

export interface MetricDetail {
    score: number;
    max_score: number;
    feedback: string[];
}

export interface Metrics {
    impact_metrics: MetricDetail;
    action_verbs: MetricDetail;
    clarity_brevity: MetricDetail;
    ats_compatibility: MetricDetail;
    keyword_optimization: MetricDetail;
    skills_alignment: MetricDetail;
    executive_presence: MetricDetail;
    format_structure: MetricDetail;
}

export interface ActionableGap {
    issue: string;
    recommendation: string;
    priority: "High" | "Medium" | "Low";
}

export interface ImprovementPlan {
    critical_fixes: string[];
    quick_wins: string[];
    long_term_strategy: string[];
}

export interface ResumeAnalysis {
    overall_score: number;
    tier: "Needs Work" | "Good" | "Very Good" | "Outstanding" | "Executive";
    metrics: Metrics;
    key_strengths: string[];
    actionable_gaps: ActionableGap[];
    improvement_plan: ImprovementPlan;
}

export interface ComponentRisk {
    impact: string[];
    probability: string[];
    mitigations: string[];
}

export interface RiskAssessment {
    overall_risk_level: "Low" | "Medium" | "High" | "Critical";
    risk_factors: string[];
    components: {
        format_risk: ComponentRisk;
        content_risk: ComponentRisk;
        ats_risk: ComponentRisk;
        alignment_risk: ComponentRisk;
        timeline_risk: ComponentRisk;
    };
}

export interface AnalyzeResponse {
    run_id: string;
    status: "success" | "error";
    analysis: ResumeAnalysis;
    risk_assessment: RiskAssessment;
    processing_time_ms: number;
    warnings?: string[];
}
