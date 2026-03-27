import type { Metadata } from "next";
import Link from "next/link";
import { cookies } from "next/headers";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const AUTH_COOKIE_NAME = "smart_resume_auth";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Smart AI Resume | Executive Dashboard",
  description: "Premium ATS, styling, and structural analysis visualization.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const isAuthenticated = cookieStore.has(AUTH_COOKIE_NAME);

  return (
    <html lang="en" className={`dark ${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-xl">
          <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <Link href="/" className="flex items-center gap-3 text-sm font-semibold tracking-wide text-foreground">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-primary/15 text-primary ring-1 ring-primary/20">
                SA
              </span>
              <span>Smart AI Resume</span>
            </Link>

            <nav className="flex items-center gap-2 text-sm">
              {isAuthenticated ? (
                <a
                  href="/api/auth?action=logout"
                  className="inline-flex h-9 items-center rounded-lg border border-border/70 bg-muted/40 px-3 font-medium text-foreground transition-colors hover:bg-muted"
                >
                  Logout
                </a>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="inline-flex h-9 items-center rounded-lg px-3 font-medium text-muted-foreground transition-colors hover:text-foreground"
                  >
                    Login
                  </Link>
                  <Link
                    href="/register"
                    className="inline-flex h-9 items-center rounded-lg bg-primary px-3 font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                  >
                    Register
                  </Link>
                </>
              )}
            </nav>
          </div>
        </header>

        <div className="flex-1">{children}</div>
      </body>
    </html>
  );
}
