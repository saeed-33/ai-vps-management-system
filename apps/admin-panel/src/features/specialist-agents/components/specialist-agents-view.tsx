"use client";

import { useQuery } from "@tanstack/react-query";
import { Bot, RefreshCw } from "lucide-react";
import Link from "next/link";
import { getStoredAccessToken } from "@/lib/auth-client";
import { getSpecialistAgents, getSpecialistAgentsSummary } from "@/lib/specialist-agents-client";

export function SpecialistAgentsView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();

  const agentsQuery = useQuery({
    queryKey: ["specialist-agents", "list"],
    queryFn: () => getSpecialistAgents(token ?? ""),
    enabled: Boolean(token),
  });

  const summaryQuery = useQuery({
    queryKey: ["specialist-agents", "summary"],
    queryFn: () => getSpecialistAgentsSummary(token ?? ""),
    enabled: Boolean(token),
  });

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">الوكلاء المتخصصون</h2>
          <p className="metric-note">يجب تسجيل الدخول أولا لعرض الوكلاء المتخصصين.</p>
          <Link className="button primary" href="/login">
            تسجيل الدخول
          </Link>
        </section>
      </div>
    );
  }

  const domains = Object.entries(summaryQuery.data?.by_domain ?? {});

  return (
    <div className="page-stack">
      <section className="grid" aria-label="ملخص الوكلاء المتخصصين">
        <article className="card metric-card">
          <p className="card-title">الإجمالي</p>
          <p className="metric-value">{summaryQuery.data?.total ?? "-"}</p>
          <p className="metric-note">كل الوكلاء المتخصصين المعرفين حاليا.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">نشطون</p>
          <p className="metric-value">{summaryQuery.data?.active ?? "-"}</p>
          <p className="metric-note">جاهزون للاستدعاء لاحقا عند وجود سبب.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">مسودات</p>
          <p className="metric-value">{summaryQuery.data?.draft ?? "-"}</p>
          <p className="metric-note">تعريفات غير معتمدة للتشغيل بعد.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">المجالات</p>
          <p className="metric-value">{domains.length || "-"}</p>
          <p className="metric-note">توزيع حسب مجال التحليل.</p>
        </article>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">الوكلاء المتخصصون</h2>
            <p className="metric-note">
              الوكيل المتخصص لا يعمل في كل دورة، بل يستدعى عند وجود دليل من تقرير المراقبة أو ملف مراقبة مرتبط.
            </p>
          </div>
          <button
            className="button primary"
            type="button"
            onClick={() => {
              void agentsQuery.refetch();
              void summaryQuery.refetch();
            }}
          >
            <RefreshCw aria-hidden="true" />
            تحديث
          </button>
        </div>

        {agentsQuery.isError ? (
          <p className="notice danger">تعذر تحميل الوكلاء المتخصصين. قد يكون token منتهي الصلاحية.</p>
        ) : null}

        <ul className="status-list">
          {(agentsQuery.data?.agents ?? []).map((agent) => (
            <li className="status-row" key={agent.id}>
              <div>
                <strong>{agent.name}</strong>
                <span dir="ltr">{agent.id}</span>
                <span>
                  {agent.domain} / v{agent.version} / {agent.execution_mode} / {agent.allowed_tools_count} tools
                </span>
                <span>{agent.trigger_profiles.join(", ") || "no trigger profiles"}</span>
              </div>
              <span className={`badge ${agent.status === "active" ? "success" : "neutral"}`}>
                {agent.status}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card side-card">
        <div className="toolbar">
          <h2 className="section-title">حدود التشغيل</h2>
          <Bot aria-hidden="true" />
        </div>
        <p className="metric-note">
          هذه المرحلة تعرف العقود فقط. لا يوجد استدعاء فعلي، ولا تنفيذ أوامر، ولا ربط مع sandbox حتى الآن.
        </p>
      </section>
    </div>
  );
}
