import { NextRequest, NextResponse } from "next/server";

import type { AuthResponse } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const AUTH_COOKIE_NAME = "smart_resume_auth";
const AUTH_COOKIE_CLIENT_NAME = "smart_resume_auth_client";
const AUTH_COOKIE_MAX_AGE = 60 * 60 * 24;

type AuthAction = "login" | "register";

interface AuthPayload {
    action?: AuthAction;
    email?: string;
    password?: string;
    full_name?: string;
}

function authCookieOptions() {
    return {
        httpOnly: true,
        sameSite: "lax" as const,
        secure: process.env.NODE_ENV === "production",
        path: "/",
        maxAge: AUTH_COOKIE_MAX_AGE,
    };
}

function applyAuthCookies(response: NextResponse, token: string): NextResponse {
    const cookieOptions = authCookieOptions();

    response.cookies.set(AUTH_COOKIE_NAME, token, cookieOptions);
    response.cookies.set(AUTH_COOKIE_CLIENT_NAME, token, {
        ...cookieOptions,
        httpOnly: false,
    });

    return response;
}

async function readJson(request: NextRequest): Promise<AuthPayload> {
    try {
        return (await request.json()) as AuthPayload;
    } catch {
        return {};
    }
}

async function proxyBackend(path: string, payload: Record<string, unknown>): Promise<Response> {
    return fetch(`${API_BASE_URL}/api/v1/auth${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        cache: "no-store",
    });
}

function errorResponse(status: number, detail: string) {
    return NextResponse.json({ detail }, { status });
}

export async function POST(request: NextRequest): Promise<NextResponse> {
    const payload = await readJson(request);

    if (!payload.action || !payload.email || !payload.password) {
        return errorResponse(400, "Missing auth action, email, or password");
    }

    const normalizedPayload = {
        email: payload.email,
        password: payload.password,
        ...(payload.full_name ? { full_name: payload.full_name } : {}),
    };

    let tokenResponse: Response;

    if (payload.action === "login") {
        tokenResponse = await proxyBackend("/login", normalizedPayload);
    } else {
        const registerResponse = await proxyBackend("/register", normalizedPayload);

        if (!registerResponse.ok) {
            const detail = await registerResponse.text();
            return errorResponse(registerResponse.status, detail || "Registration failed");
        }

        tokenResponse = await proxyBackend("/login", normalizedPayload);
    }

    if (!tokenResponse.ok) {
        const detail = await tokenResponse.text();
        return errorResponse(tokenResponse.status, detail || "Authentication failed");
    }

    const data = (await tokenResponse.json()) as AuthResponse;
    const response = NextResponse.json({ access_token: data.access_token, token_type: data.token_type });

    return applyAuthCookies(response, data.access_token);
}

export async function GET(request: NextRequest): Promise<NextResponse> {
    if (request.nextUrl.searchParams.get("action") !== "logout") {
        return errorResponse(405, "Method not allowed");
    }

    const response = NextResponse.redirect(new URL("/login", request.url));
    response.cookies.set(AUTH_COOKIE_NAME, "", { path: "/", maxAge: 0 });
    response.cookies.set(AUTH_COOKIE_CLIENT_NAME, "", { path: "/", maxAge: 0 });
    return response;
}
