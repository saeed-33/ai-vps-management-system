import Link from "next/link";

export default function NotFound() {
  return (
    <div className="page-stack">
      <section className="card wide-card">
        <h2 className="section-title">الصفحة غير موجودة</h2>
        <p className="metric-note">المسار المطلوب غير متاح في لوحة الإدارة الحالية.</p>
        <Link className="button primary" href="/">
          العودة إلى Dashboard
        </Link>
      </section>
    </div>
  );
}
