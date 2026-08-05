"use client";

import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Server } from "lucide-react";
import Link from "next/link";
import { getStoredAccessToken } from "@/lib/auth-client";
import { getServers, getServersSummary } from "@/lib/servers-client";

export function ServersView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();

  const serversQuery = useQuery({
    queryKey: ["servers", "list"],
    queryFn: () => getServers(token ?? ""),
    enabled: Boolean(token),
  });

  const summaryQuery = useQuery({
    queryKey: ["servers", "summary"],
    queryFn: () => getServersSummary(token ?? ""),
    enabled: Boolean(token),
  });

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">إدارة السيرفرات</h2>
          <p className="metric-note">يجب تسجيل الدخول أولا لعرض السيرفرات.</p>
          <Link className="button primary" href="/login">
            تسجيل الدخول
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="grid" aria-label="ملخص السيرفرات">
        <article className="card metric-card">
          <p className="card-title">الإجمالي</p>
          <p className="metric-value">{summaryQuery.data?.total ?? "-"}</p>
          <p className="metric-note">كل السيرفرات المعرفة حاليا.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">نشطة</p>
          <p className="metric-value">{summaryQuery.data?.active ?? "-"}</p>
          <p className="metric-note">جاهزة للمراقبة عند ربط الأدوات.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">صيانة</p>
          <p className="metric-value">{summaryQuery.data?.maintenance ?? "-"}</p>
          <p className="metric-note">مستثناة مؤقتا من التشغيل.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">معطلة</p>
          <p className="metric-value">{summaryQuery.data?.disabled ?? "-"}</p>
          <p className="metric-note">لا تستخدم في دورات المراقبة.</p>
        </article>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">السيرفرات</h2>
            <p className="metric-note">
              تعرض هذه المرحلة بيانات foundation مؤقتة إلى حين ربط repository وقاعدة البيانات.
            </p>
          </div>
          <button
            className="button primary"
            type="button"
            onClick={() => {
              void serversQuery.refetch();
              void summaryQuery.refetch();
            }}
          >
            <RefreshCw aria-hidden="true" />
            تحديث
          </button>
        </div>

        {serversQuery.isError ? (
          <p className="notice danger">تعذر تحميل السيرفرات. قد يكون token منتهي الصلاحية.</p>
        ) : null}

        <ul className="status-list">
          {(serversQuery.data?.servers ?? []).map((server) => (
            <li className="status-row" key={server.id}>
              <div>
                <strong>{server.name}</strong>
                <span dir="ltr">{server.hostname}</span>
                <span>
                  {server.environment} / {server.os_family ?? "unknown"} / {server.monitoring_status}
                </span>
              </div>
              <span className={`badge ${server.status === "active" ? "success" : "neutral"}`}>
                {server.status}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card side-card">
        <div className="toolbar">
          <h2 className="section-title">الخطوة القادمة</h2>
          <Server aria-hidden="true" />
        </div>
        <p className="metric-note">
          بعد هذه المرحلة سيتم بناء create/update وربط PostgreSQL ثم credentials handling بشكل آمن.
        </p>
      </section>
    </div>
  );
}
