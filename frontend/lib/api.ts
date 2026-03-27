import { AnalyzeRequest, AnalyzeResponse, AuthRequest, AuthResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const AUTH_COOKIE_NAME = "smart_resume_auth_client";

function readAuthToken(): string | null {
    if (typeof document === "undefined") {
        return null;
    }

    const cookie = document.cookie
        .split("; ")
        .find((part) => part.startsWith(`${AUTH_COOKIE_NAME}=`));

    if (!cookie) {
        return null;
    }

    return decodeURIComponent(cookie.split("=").slice(1).join("="));
}

function buildHeaders(headers?: HeadersInit): Headers {
    const merged = new Headers(headers);
    const token = readAuthToken();

    if (token && !merged.has("Authorization")) {
        merged.set("Authorization", `Bearer ${token}`);
    }

    return merged;
}

async function authFetch(input: string, init: RequestInit = {}): Promise<Response> {
    return fetch(input, {
        ...init,
        credentials: "include",
        headers: buildHeaders(init.headers),
    });
}

export function getAuthToken(): string | null {
    return readAuthToken();
}

/**
 * Submits raw text for analysis.
 */
export async function analyzeText(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
    const res = await authFetch(`${API_BASE_URL}/api/v1/analyze`, {
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
export async function analyzeUpload(
    file: File,
    opts?: { jd_text?: string; job_url?: string; job_title?: string; strict_mode?: boolean }
): Promise<AnalyzeResponse> {
    const formData = new FormData();
    formData.append("cv_file", file);
    formData.append("jd_text", opts?.jd_text || "");
    if (opts?.job_url) formData.append("job_url", opts.job_url);
    if (opts?.job_title) formData.append("job_title", opts.job_title);
    if (opts?.strict_mode) formData.append("strict_mode", "true");

    const res = await authFetch(`${API_BASE_URL}/api/v1/analyze/upload`, {
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
    const res = await authFetch(`${API_BASE_URL}/api/v1/runs/${runId}`);

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

export async function clearClientAuthToken(): Promise<void> {
    if (typeof document === "undefined") {
        return;
    }

    document.cookie = `${AUTH_COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Lax`;
}

export async function persistClientAuthToken(token: string): Promise<void> {
    if (typeof document === "undefined") {
        return;
    }

    document.cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; Max-Age=86400; SameSite=Lax`;
}

export async function authRequest(payload: AuthRequest): Promise<AuthResponse> {
    const res = await fetch("/api/auth", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        credentials: "include",
    });

    if (!res.ok) {
        const errorText = await res.text();

        try {
            const parsed = JSON.parse(errorText) as { detail?: string };
            throw new Error(parsed.detail || errorText || `Authentication failed: ${res.status}`);
        } catch {
            throw new Error(errorText || `Authentication failed: ${res.status}`);
        }
    }

    return res.json();
}
