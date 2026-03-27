import { NextRequest, NextResponse } from "next/server";

const AUTH_COOKIE_NAME = "smart_resume_auth";

function isPublicPath(pathname: string): boolean {
    return (
        pathname.startsWith("/login") ||
        pathname.startsWith("/register") ||
        pathname.startsWith("/api") ||
        pathname.startsWith("/_next") ||
        pathname === "/favicon.ico"
    );
}

export function middleware(request: NextRequest): NextResponse {
    const { pathname, search } = request.nextUrl;

    if (isPublicPath(pathname)) {
        const authCookie = request.cookies.get(AUTH_COOKIE_NAME)?.value;

        if (authCookie && (pathname === "/login" || pathname === "/register")) {
            const redirectUrl = request.nextUrl.clone();
            redirectUrl.pathname = "/";
            redirectUrl.search = search;
            return NextResponse.redirect(redirectUrl);
        }

        return NextResponse.next();
    }

    const authCookie = request.cookies.get(AUTH_COOKIE_NAME)?.value;

    if (!authCookie) {
        const redirectUrl = request.nextUrl.clone();
        redirectUrl.pathname = "/login";
        redirectUrl.searchParams.set("next", `${pathname}${search}`);
        return NextResponse.redirect(redirectUrl);
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
