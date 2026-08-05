"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Activity, Play, RefreshCw } from "lucide-react";
import Link from "next/link";
import { getStoredAccessToken } from "@/lib/auth-client";
import {
  getPeriodicMonitoringCycles,
  startPeriodicMonitoringCycle,
} from "@/lib/periodic-monitoring-client";

export function PeriodicMonitoringView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();

  const cyclesQuery = useQuery({
    queryKey: ["periodic-monitoring", "cycles"],
    queryFn: () => getPeriodicMonitoringCycles(token ?? ""),
    enabled: Boolean(token),
  });

  const startMutation = useMutation({
    mutationFn: () => startPeriodicMonitoringCycle(token ?? ""),
    onSuccess: () => {
      void cyclesQuery.refetch();
    },
  });

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">المراقبة الدورية</h2>
          <p className="metric-note">يجب تسجيل الدخول أولا لتشغيل دورة مراقبة دورية.</p>
          <Link className="button primary" href="/login">
            تسجيل الدخول
          </Link>
        </section>
      </div>
    );
  }

  const latestCycle = cyclesQuery.data?.cycles[0];
  const latestReport = latestCycle?.reports[0];

  return (
    <div className="page-stack">
      <section className="grid" aria-label="ملخص المراقبة الدورية">
        <article className="card metric-card">
          <p className="card-title">الدورات</p>
          <p className="metric-value">{cyclesQuery.data?.cycles.length ?? "-"}</p>
          <p className="metric-note">دورات محفوظة في ذاكرة API الحالية.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">السيرفرات</p>
          <p className="metric-value">{latestCycle?.servers_checked ?? "-"}</p>
          <p className="metric-note">آخر دورة مراقبة.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">التقارير</p>
          <p className="metric-value">{latestCycle?.reports_count ?? "-"}</p>
          <p className="metric-note">تقارير السيرفرات في آخر دورة.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">الحالة</p>
          <p className="metric-value">{latestCycle?.status ?? "-"}</p>
          <p className="metric-note">لا يوجد تحليل أو حلول في هذه المرحلة.</p>
        </article>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">تشغيل دورة مراقبة</h2>
            <p className="metric-note">
              تنشئ هذه العملية وكيلا فرعيا منطقيا لكل سيرفر نشط وتجمع قيما أساسية فقط داخل تقرير دوري.
            </p>
          </div>
          <div className="toolbar">
            <button
              className="button"
              type="button"
              onClick={() => {
                void cyclesQuery.refetch();
              }}
            >
              <RefreshCw aria-hidden="true" />
              تحديث
            </button>
            <button
              className="button primary"
              type="button"
              disabled={startMutation.isPending}
              onClick={() => startMutation.mutate()}
            >
              <Play aria-hidden="true" />
              {startMutation.isPending ? "جاري التشغيل" : "تشغيل دورة"}
            </button>
          </div>
        </div>

        {startMutation.isError || cyclesQuery.isError ? (
          <p className="notice danger">تعذر تشغيل أو تحميل دورات المراقبة. تحقق من token وصلاحية monitoring.write.</p>
        ) : null}

        {latestCycle ? (
          <ul className="status-list">
            <li className="status-row">
              <div>
                <strong>{latestCycle.cycle_id}</strong>
                <span>{latestCycle.scope_note}</span>
                <span>
                  {latestCycle.servers_checked} checked / {latestCycle.reports_count} reports /{" "}
                  {new Date(latestCycle.completed_at).toLocaleString()}
                </span>
              </div>
              <span className="badge success">{latestCycle.status}</span>
            </li>
          </ul>
        ) : (
          <p className="notice">لا توجد دورة مراقبة بعد.</p>
        )}
      </section>

      {latestReport ? (
        <section className="card wide-card">
          <div className="toolbar">
            <div>
              <h2 className="section-title">آخر تقرير سيرفر</h2>
              <p className="metric-note">{latestReport.collection_summary}</p>
            </div>
            <Activity aria-hidden="true" />
          </div>
          <ul className="status-list">
            {latestReport.metrics.map((metric) => (
              <li className="status-row" key={`${latestReport.sub_agent_id}-${metric.metric}`}>
                <div>
                  <strong>{metric.metric}</strong>
                  <span>
                    {metric.domain} / {metric.source_tool}
                  </span>
                </div>
                <span className="badge neutral">
                  {String(metric.value)} {metric.unit}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
