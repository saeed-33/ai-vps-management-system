"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Sidebar } from "@/components/navigation/sidebar";
import { LoginView } from "@/features/auth/components/login-view";
import { getStoredAccessToken } from "@/lib/auth-client";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [token, setToken] = useState<string | null | undefined>(undefined);

  useEffect(() => {
    setToken(getStoredAccessToken());
  }, [pathname]);

  if (token === undefined) {
    return null;
  }

  if (!token) {
    return (
      <main className="auth-only">
        <LoginView />
      </main>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <header className="topbar">
          <div>
            <h1>لوحة إدارة مراقبة VPS</h1>
            <p>مركز التحكم بالمراقبة، الوكلاء، المشكلات، والتقارير.</p>
          </div>
          <span className="badge success">نشط</span>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
