import { Sidebar } from "@/components/navigation/sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <header className="topbar">
          <div>
            <h1>لوحة إدارة مراقبة VPS</h1>
            <p>مركز التحكم بالمراقبة، الوكلاء، المشكلات، والتقارير.</p>
          </div>
          <span className="badge neutral">Foundation</span>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
