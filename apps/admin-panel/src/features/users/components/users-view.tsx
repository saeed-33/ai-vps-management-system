"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { RefreshCw, Users } from "lucide-react";
import { getStoredAccessToken } from "@/lib/auth-client";
import { getRoles, getUsers } from "@/lib/users-client";

export function UsersView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();

  const usersQuery = useQuery({
    queryKey: ["users", "list"],
    queryFn: () => getUsers(token ?? ""),
    enabled: Boolean(token),
  });

  const rolesQuery = useQuery({
    queryKey: ["users", "roles"],
    queryFn: () => getRoles(token ?? ""),
    enabled: Boolean(token),
  });

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">إدارة المستخدمين</h2>
          <p className="metric-note">يجب تسجيل الدخول أولا لعرض المستخدمين والأدوار.</p>
          <Link className="button primary" href="/login">
            تسجيل الدخول
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">إدارة المستخدمين</h2>
            <p className="metric-note">
              تعرض هذه المرحلة مستخدم bootstrap الحالي والأدوار المعرفة في RBAC catalog.
            </p>
          </div>
          <button
            className="button primary"
            type="button"
            onClick={() => {
              void usersQuery.refetch();
              void rolesQuery.refetch();
            }}
          >
            <RefreshCw aria-hidden="true" />
            تحديث
          </button>
        </div>

        {usersQuery.isError ? (
          <p className="notice danger">تعذر تحميل المستخدمين. قد يكون token منتهي الصلاحية.</p>
        ) : null}

        <ul className="status-list">
          {(usersQuery.data?.users ?? []).map((user) => (
            <li className="status-row" key={user.id}>
              <div>
                <strong>{user.display_name}</strong>
                <span dir="ltr">{user.email}</span>
                <span>roles: {user.roles.join(", ")}</span>
              </div>
              <span className="badge success">{user.status}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="grid">
        <article className="card wide-card">
          <div className="toolbar">
            <h2 className="section-title">الأدوار</h2>
            <Users aria-hidden="true" />
          </div>
          <ul className="status-list">
            {(rolesQuery.data?.roles ?? []).map((role) => (
              <li className="status-row" key={role.code}>
                <div>
                  <strong>{role.name}</strong>
                  <span>{role.code}</span>
                </div>
                <span className="badge neutral">{role.permission_count} صلاحية</span>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}
