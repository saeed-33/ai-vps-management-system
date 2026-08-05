import { Activity, FileWarning, Server, UserRound } from "lucide-react";

const metrics = [
  {
    label: "السيرفرات",
    value: "0",
    note: "جاهزة للربط بعد بناء API modules",
    icon: Server,
  },
  {
    label: "المستخدمون",
    value: "1",
    note: "مستخدم bootstrap الحالي إلى حين ربط قاعدة البيانات",
    icon: UserRound,
  },
  {
    label: "دورات المراقبة",
    value: "0",
    note: "سيتم تعبئتها من monitoring_cycles",
    icon: Activity,
  },
  {
    label: "مشكلات مفتوحة",
    value: "0",
    note: "سيتم ربطها بجدول issues",
    icon: FileWarning,
  },
];

const plannedWork = [
  {
    title: "إدارة السيرفرات",
    detail: "إضافة وربط السيرفرات ومجموعاتها واعتمادات الاتصال.",
    status: "مخطط",
  },
  {
    title: "ملفات المراقبة",
    detail: "تعريف metrics وقواعد التحليل السياقي وtriggers.",
    status: "مخطط",
  },
  {
    title: "الوكلاء المتخصصون",
    detail: "تعريف وكلاء جدد وتحديد أدواتهم وصلاحياتهم.",
    status: "مخطط",
  },
  {
    title: "سجلات التدقيق",
    detail: "عرض كل عملية حساسة وقرار Policy Engine.",
    status: "مخطط",
  },
];

export function DashboardOverview() {
  return (
    <div className="page-stack">
      <section className="grid" aria-label="مؤشرات عامة">
        {metrics.map((metric) => (
          <article className="card metric-card" key={metric.label}>
            <div className="toolbar">
              <p className="card-title">{metric.label}</p>
              <metric.icon aria-hidden="true" />
            </div>
            <p className="metric-value">{metric.value}</p>
            <p className="metric-note">{metric.note}</p>
          </article>
        ))}
      </section>

      <section className="grid">
        <article className="card wide-card">
          <h2 className="section-title">أولويات التشغيل القادمة</h2>
          <ul className="status-list">
            {plannedWork.map((item) => (
              <li className="status-row" key={item.title}>
                <div>
                  <strong>{item.title}</strong>
                  <span>{item.detail}</span>
                </div>
                <span className="badge neutral">{item.status}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="card side-card">
          <h2 className="section-title">حالة المرحلة</h2>
          <ul className="status-list">
            <li className="status-row">
              <div>
                <strong>Admin Panel Foundation</strong>
                <span>layout وnavigation وdashboard أولي.</span>
              </div>
              <span className="badge success">نشط</span>
            </li>
            <li className="status-row">
              <div>
                <strong>Backend API</strong>
                <span>health وmeta endpoints متاحة عند تشغيله.</span>
              </div>
              <span className="badge neutral">جاهز</span>
            </li>
          </ul>
        </article>
      </section>
    </div>
  );
}
