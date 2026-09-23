"use client";

import Link from "next/link";

import { useAuth } from "@/components/auth/auth-provider";
import { AuthGuard } from "@/components/auth/auth-guard";
import { Button } from "@/components/ui/button";

function NavShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-full flex-1 flex-col">
      <header className="flex items-center justify-between border-b px-6 py-3">
        <Link href="/job-descriptions" className="font-semibold">
          HireSense
        </Link>
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span>{user?.email}</span>
          <Button variant="outline" size="sm" onClick={logout}>
            Sign out
          </Button>
        </div>
      </header>
      <main className="flex flex-1 flex-col px-6 py-8">{children}</main>
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <NavShell>{children}</NavShell>
    </AuthGuard>
  );
}
