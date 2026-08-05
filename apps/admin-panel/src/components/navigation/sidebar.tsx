import {
  Activity,
  Bot,
  Database,
  FileText,
  Gauge,
  MessageSquare,
  LogIn,
  ScrollText,
  Server,
  Settings,
  ShieldCheck,
  TriangleAlert,
  Users,
  Wrench,
} from "lucide-react";
import Link from "next/link";

const navigationGroups = [
  {
    title: "التشغيل",
    items: [
      { label: "Dashboard", href: "/", icon: Gauge },
      { label: "حالة API", href: "/api-status", icon: Activity },
      { label: "السيرفرات", href: "/servers", icon: Server },
      { label: "المشكلات", href: "#issues", icon: TriangleAlert },
      { label: "التقارير", href: "#reports", icon: FileText },
    ],
  },
  {
    title: "الوكيل والمراقبة",
    items: [
      { label: "ملفات المراقبة", href: "/monitoring-profiles", icon: ScrollText },
      { label: "الوكلاء المتخصصون", href: "/specialist-agents", icon: Bot },
      { label: "الأدوات المسموحة", href: "/allowed-tools", icon: Wrench },
      { label: "الحلول المسموحة", href: "#allowed-solutions", icon: ShieldCheck },
    ],
  },
  {
    title: "النظام",
    items: [
      { label: "المستخدمون", href: "/users", icon: Users },
      { label: "الوثائق", href: "#documents", icon: Database },
      { label: "المحادثة", href: "#chat", icon: MessageSquare },
      { label: "تسجيل الدخول", href: "/login", icon: LogIn },
      { label: "الإعدادات", href: "#settings", icon: Settings },
    ],
  },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">AI</div>
        <div>
          <p className="brand-title">VPS Management</p>
          <p className="brand-subtitle">Control Plane</p>
        </div>
      </div>

      {navigationGroups.map((group) => (
        <nav key={group.title} aria-label={group.title}>
          <p className="nav-section-title">{group.title}</p>
          <ul className="nav-list">
            {group.items.map((item) => (
              <li key={item.label}>
                <Link className="nav-link" href={item.href}>
                  <item.icon aria-hidden="true" />
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      ))}
    </aside>
  );
}
