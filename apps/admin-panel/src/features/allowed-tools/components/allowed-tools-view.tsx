"use client";

import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Wrench } from "lucide-react";
import Link from "next/link";
import { getAllowedTools, getAllowedToolsSummary } from "@/lib/allowed-tools-client";
import { getStoredAccessToken } from "@/lib/auth-client";

export function AllowedToolsView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();

  const toolsQuery = useQuery({
    queryKey: ["allowed-tools", "list"],
    queryFn: () => getAllowedTools(token ?? ""),
    enabled: Boolean(token),
  });

  const summaryQuery = useQuery({
    queryKey: ["allowed-tools", "summary"],
    queryFn: () => getAllowedToolsSummary(token ?? ""),
    enabled: Boolean(token),
  });

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">الأدوات المسموحة</h2>
          <p className="metric-note">يجب تسجيل الدخول أولا لعرض الأدوات المسموحة.</p>
          <Link className="button primary" href="/login">
            تسجيل الدخول
          </Link>
        </section>
      </div>
    );
  }

  const categories = Object.entries(summaryQuery.data?.by_category ?? {});

  return (
    <div className="page-stack">
      <section className="grid" aria-label="ملخص الأدوات المسموحة">
        <article className="card metric-card">
          <p className="card-title">الإجمالي</p>
          <p className="metric-value">{summaryQuery.data?.total ?? "-"}</p>
          <p className="metric-note">كل الأدوات المعرفة حاليا.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">نشطة</p>
          <p className="metric-value">{summaryQuery.data?.active ?? "-"}</p>
          <p className="metric-note">متاحة للعقود اللاحقة.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">قراءة فقط</p>
          <p className="metric-value">{summaryQuery.data?.read_only ?? "-"}</p>
          <p className="metric-note">لا تغير حالة السيرفر.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">الفئات</p>
          <p className="metric-value">{categories.length || "-"}</p>
          <p className="metric-note">تصنيف حسب مجال الاستخدام.</p>
        </article>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">الأدوات المسموحة</h2>
            <p className="metric-note">
              هذه القائمة تعرف أدوات القراءة والتحليل فقط. أي أداة تغير حالة السيرفر تحتاج سياسة منفصلة لاحقا.
            </p>
          </div>
          <button
            className="button primary"
            type="button"
            onClick={() => {
              void toolsQuery.refetch();
              void summaryQuery.refetch();
            }}
          >
            <RefreshCw aria-hidden="true" />
            تحديث
          </button>
        </div>

        {toolsQuery.isError ? (
          <p className="notice danger">تعذر تحميل الأدوات المسموحة. قد يكون token منتهي الصلاحية.</p>
        ) : null}

        <ul className="status-list">
          {(toolsQuery.data?.tools ?? []).map((tool) => (
            <li className="status-row" key={tool.id}>
              <div>
                <strong>{tool.name}</strong>
                <span dir="ltr">{tool.code}</span>
                <span>
                  {tool.category} / v{tool.version} / {tool.execution_scope} /{" "}
                  {tool.read_only ? "read-only" : "mutating"}
                </span>
                <span>{tool.used_by.join(", ") || "not assigned"}</span>
              </div>
              <span className={`badge ${tool.status === "active" ? "success" : "neutral"}`}>
                {tool.status}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card side-card">
        <div className="toolbar">
          <h2 className="section-title">حدود المرحلة</h2>
          <Wrench aria-hidden="true" />
        </div>
        <p className="metric-note">
          تسجيل الأداة هنا لا يعني السماح بتنفيذ حلول. التنفيذ يبقى ممنوعا افتراضيا حتى يتم تعريف الحلول وسياسات
          الاعتماد.
        </p>
      </section>
    </div>
  );
}
