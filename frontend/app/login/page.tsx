"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useMemo, useState } from "react";
import { ArrowRight, Loader2, LockKeyhole, Mail } from "lucide-react";

import { authRequest, persistClientAuthToken } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

function safeNextPath(value: string | null): string {
    if (!value || !value.startsWith("/")) {
        return "/";
    }

    return value;
}

export default function LoginPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const nextPath = useMemo(() => safeNextPath(searchParams.get("next")), [searchParams]);

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const result = await authRequest({ action: "login", email, password });
            await persistClientAuthToken(result.access_token);
            router.replace(nextPath);
            router.refresh();
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Login failed.");
            setLoading(false);
        }
    }

    return (
        <main className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center overflow-hidden px-4 py-10 sm:px-6 lg:px-8">
            <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(124,58,237,0.18),_transparent_34%),radial-gradient(circle_at_bottom_right,_rgba(59,130,246,0.14),_transparent_28%),linear-gradient(180deg,_rgba(2,6,23,0.04),_transparent)]" />
            <div className="absolute left-[-10%] top-10 -z-10 h-64 w-64 rounded-full bg-primary/15 blur-3xl" />

            <Card className="w-full max-w-md border-border/70 bg-card/90 shadow-2xl backdrop-blur-xl">
                <CardHeader className="space-y-2 pb-2">
                    <div className="inline-flex w-fit items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-primary">
                        <LockKeyhole className="h-3.5 w-3.5" />
                        Secure access
                    </div>
                    <CardTitle className="text-2xl">Sign in</CardTitle>
                    <CardDescription>Use your Smart AI Resume account to continue.</CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4 pt-4">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <div className="relative">
                                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                <input
                                    id="email"
                                    type="email"
                                    required
                                    autoComplete="email"
                                    className="flex h-11 w-full rounded-lg border border-input bg-background/60 pl-10 pr-3 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(event) => setEmail(event.target.value)}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <div className="relative">
                                <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                <input
                                    id="password"
                                    type="password"
                                    required
                                    autoComplete="current-password"
                                    className="flex h-11 w-full rounded-lg border border-input bg-background/60 pl-10 pr-3 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(event) => setPassword(event.target.value)}
                                />
                            </div>
                        </div>

                        {error ? (
                            <div className="rounded-lg border border-destructive/20 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                                {error}
                            </div>
                        ) : null}
                    </CardContent>

                    <CardFooter className="flex flex-col gap-3 border-t border-border/60 bg-muted/20 p-4 sm:flex-row sm:justify-between">
                        <Button className="w-full sm:w-auto" size="lg" disabled={loading} type="submit">
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Signing in
                                </>
                            ) : (
                                <>
                                    Continue
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </>
                            )}
                        </Button>

                        <p className="text-sm text-muted-foreground">
                            New here?{" "}
                            <Link href="/register" className="font-medium text-foreground underline underline-offset-4">
                                Create an account
                            </Link>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </main>
    );
}
