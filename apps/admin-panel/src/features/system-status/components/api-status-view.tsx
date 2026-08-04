"use client";

import { useQuery } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { getApiBaseUrl, getApiLiveness, getApiMetadata } from "@/lib/api-client";

export function ApiStatusView() {
  const liveQuery = useQuery({
    queryKey: ["api", "live"],
    queryFn: getApiLiveness,
  });

  const metaQuery = useQuery({
    queryKey: ["api", "meta"],
    queryFn: getApiMetadata,
  });

  const isHealthy = liveQuery.isSuccess;
  const liveDetail = liveQuery.data
    ? `${liveQuery.data.service} - ${liveQuery.data.environment}`
    : null;
  const moduleCount = metaQuery.data ? metaQuery.data.modules.length : null;

  return (
    <div className="page-stack">
      <section className="card wide-card api-box">
        <div className="toolbar">
          <div>
            <h2 className="section-title">حالة الاتصال بالـ Backend API</h2>
            <p className="metric-note">
              هذه الصفحة تتحقق من endpoints التي تم إنشاؤها في مرحلة Control Plane Foundation.
            </p>
          </div>
          <button
            className="button primary"
            type="button"
            onClick={() => {
              void liveQuery.refetch();
              void metaQuery.refetch();
            }}
          >
            <RefreshCw aria-hidden="true" />
            تحديث
          </button>
        </div>

        <div className="code-line">{getApiBaseUrl()}</div>

        <ul className="status-list">
          <li className="status-row">
            <div>
              <strong>Liveness</strong>
              <span>
                {liveQuery.isLoading
                  ? "جاري الفحص"
                  : liveQuery.isError
                    ? "لا يوجد اتصال. شغل API على المنفذ 8000."
                    : liveDetail}
              </span>
            </div>
            <span className={`badge ${isHealthy ? "success" : "danger"}`}>
              {isHealthy ? "متصل" : "غير متصل"}
            </span>
          </li>

          <li className="status-row">
            <div>
              <strong>Metadata</strong>
              <span>
                {metaQuery.isLoading
                  ? "جاري التحميل"
                  : metaQuery.isError
                    ? "تعذر جلب معلومات الوحدات"
                    : `${moduleCount} modules`}
              </span>
            </div>
            <span className={`badge ${metaQuery.isSuccess ? "success" : "warning"}`}>
              {metaQuery.isSuccess ? "جاهز" : "ينتظر"}
            </span>
          </li>
        </ul>
      </section>

      {metaQuery.isSuccess ? (
        <section className="grid" aria-label="وحدات Backend">
          <article className="card wide-card">
            <h2 className="section-title">وحدات Control Plane</h2>
            <ul className="status-list">
              {metaQuery.data.modules.map((module) => (
                <li className="status-row" key={module.name}>
                  <div>
                    <strong>{module.name}</strong>
                    <span>الحالة الحالية للوحدة في Backend foundation.</span>
                  </div>
                  <span className="badge neutral">{module.status}</span>
                </li>
              ))}
            </ul>
          </article>
        </section>
      ) : null}
    </div>
  );
}
