"use client";

import { useQuery } from "@tanstack/react-query";
import { RefreshCw, ScrollText } from "lucide-react";
import Link from "next/link";
import { getStoredAccessToken } from "@/lib/auth-client";
import { getMonitoringProfiles, getMonitoringProfilesSummary } from "@/lib/monitoring-profiles-client";

export function MonitoringProfilesView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();

  const profilesQuery = useQuery({
    queryKey: ["monitoring-profiles", "list"],
    queryFn: () => getMonitoringProfiles(token ?? ""),
    enabled: Boolean(token),
  });

  const summaryQuery = useQuery({
    queryKey: ["monitoring-profiles", "summary"],
    queryFn: () => getMonitoringProfilesSummary(token ?? ""),
    enabled: Boolean(token),
  });

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">ملفات المراقبة</h2>
          <p className="metric-note">يجب تسجيل الدخول أولا لعرض ملفات المراقبة.</p>
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
      <section className="grid" aria-label="ملخص ملفات المراقبة">
        <article className="card metric-card">
          <p className="card-title">الإجمالي</p>
          <p className="metric-value">{summaryQuery.data?.total ?? "-"}</p>
          <p className="metric-note">كل ملفات المراقبة المعرفة حاليا.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">نشطة</p>
          <p className="metric-value">{summaryQuery.data?.active ?? "-"}</p>
          <p className="metric-note">يمكن إسنادها للسيرفرات لاحقا.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">مسودة</p>
          <p className="metric-value">{summaryQuery.data?.draft ?? "-"}</p>
          <p className="metric-note">تعريفات لم تعتمد للتشغيل بعد.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">المجالات</p>
          <p className="metric-value">{domains.length || "-"}</p>
          <p className="metric-note">تصنيف حسب مجال المراقبة.</p>
        </article>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">ملفات المراقبة</h2>
            <p className="metric-note">
              العتبات هنا إشارات تحليل وليست أحكاما نهائية، لأن القيم المنخفضة قد تكون مشكلة عند وجود أعراض أخرى.
            </p>
          </div>
          <button
            className="button primary"
            type="button"
            onClick={() => {
              void profilesQuery.refetch();
              void summaryQuery.refetch();
            }}
          >
            <RefreshCw aria-hidden="true" />
            تحديث
          </button>
        </div>

        {profilesQuery.isError ? (
          <p className="notice danger">تعذر تحميل ملفات المراقبة. قد يكون token منتهي الصلاحية.</p>
        ) : null}

        <ul className="status-list">
          {(profilesQuery.data?.profiles ?? []).map((profile) => (
            <li className="status-row" key={profile.id}>
              <div>
                <strong>{profile.name}</strong>
                <span dir="ltr">{profile.id}</span>
                <span>
                  {profile.domain} / v{profile.version} / {profile.thresholds_count} thresholds /{" "}
                  {profile.assigned_servers} servers
                </span>
                <span>{profile.specialist_agents.join(", ") || "no specialist agents"}</span>
              </div>
              <span className={`badge ${profile.status === "active" ? "success" : "neutral"}`}>
                {profile.status}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card side-card">
        <div className="toolbar">
          <h2 className="section-title">قاعدة مهمة</h2>
          <ScrollText aria-hidden="true" />
        </div>
        <p className="metric-note">
          ملف المراقبة يحدد أدوات وعتبات وملاحظات تحليلية. القرار النهائي يبقى نتيجة تحليل التقرير والسياق، لا رقم
          العتبة وحده.
        </p>
      </section>
    </div>
  );
}
