import { AnalyzeRequest, AnalyzeResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Submits raw text for analysis.
 */
export async function analyzeText(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
    const res = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Analysis failed: ${res.status} ${errorText}`);
    }

    return res.json();
}

/**
 * Submits a file (PDF/DOCX) and optional JD text for analysis.
 */
export async function analyzeUpload(file: File, jdText?: string): Promise<AnalyzeResponse> {
    const formData = new FormData();
    formData.append("file", file);
    if (jdText) {
        formData.append("jd_text", jdText);
    }

    const res = await fetch(`${API_BASE_URL}/api/v1/analyze/upload`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Upload analysis failed: ${res.status} ${errorText}`);
    }

    return res.json();
}

/**
 * Fetches a specific analysis run result.
 */
export async function getRun(runId: string): Promise<AnalyzeResponse> {
    const res = await fetch(`${API_BASE_URL}/api/v1/runs/${runId}`);

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Failed to fetch run: ${res.status} ${errorText}`);
    }

    return res.json();
}

/**
 * Returns the URL for downloading the rewritten DOCX file.
 */
export function getDownloadUrl(runId: string): string {
    return `${API_BASE_URL}/api/v1/runs/${runId}/download`;
}
