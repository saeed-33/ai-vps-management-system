"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { KeyRound, RefreshCw, Server } from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { getStoredAccessToken } from "@/lib/auth-client";
import { getServer, getServers, getServersSummary, updateServerSshAccess } from "@/lib/servers-client";

export function ServersView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();
  const [sshEnabled, setSshEnabled] = useState(false);
  const [sshHost, setSshHost] = useState("");
  const [sshPort, setSshPort] = useState(22);
  const [sshUsername, setSshUsername] = useState("");
  const [sshPrivateKeyPath, setSshPrivateKeyPath] = useState("");
  const [sshPassword, setSshPassword] = useState("");

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

  const foundationServerQuery = useQuery({
    queryKey: ["servers", "detail", "srv-foundation-001"],
    queryFn: () => getServer(token ?? "", "srv-foundation-001"),
    enabled: Boolean(token),
  });

  const sshMutation = useMutation({
    mutationFn: () =>
      updateServerSshAccess(token ?? "", "srv-foundation-001", {
        enabled: sshEnabled,
        host: sshHost || null,
        port: sshPort,
        username: sshUsername || null,
        private_key_path: sshPrivateKeyPath || null,
        password: sshPassword || null,
      }),
    onSuccess: () => {
      setSshPassword("");
      void foundationServerQuery.refetch();
    },
  });

  function handleSshSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    sshMutation.mutate();
  }

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
          <h2 className="section-title">إعداد SSH مؤقت</h2>
          <KeyRound aria-hidden="true" />
        </div>
        <p className="metric-note">الحفظ الحالي داخل ذاكرة API فقط ولا يعرض كلمة المرور بعد حفظها.</p>
        <form className="form-stack" onSubmit={handleSshSubmit}>
          <label className="field">
            <span>تفعيل SSH</span>
            <input
              type="checkbox"
              checked={sshEnabled}
              onChange={(event) => setSshEnabled(event.target.checked)}
            />
          </label>
          <label className="field">
            <span>Host</span>
            <input dir="ltr" value={sshHost} onChange={(event) => setSshHost(event.target.value)} />
          </label>
          <label className="field">
            <span>Port</span>
            <input
              dir="ltr"
              min={1}
              max={65535}
              type="number"
              value={sshPort}
              onChange={(event) => setSshPort(Number(event.target.value))}
            />
          </label>
          <label className="field">
            <span>Username</span>
            <input dir="ltr" value={sshUsername} onChange={(event) => setSshUsername(event.target.value)} />
          </label>
          <label className="field">
            <span>Private key path</span>
            <input
              dir="ltr"
              value={sshPrivateKeyPath}
              onChange={(event) => setSshPrivateKeyPath(event.target.value)}
            />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              dir="ltr"
              type="password"
              value={sshPassword}
              onChange={(event) => setSshPassword(event.target.value)}
            />
          </label>
          <button className="button primary" type="submit" disabled={sshMutation.isPending}>
            <Server aria-hidden="true" />
            {sshMutation.isPending ? "جاري الحفظ" : "حفظ SSH"}
          </button>
        </form>
        {sshMutation.isError ? <p className="notice danger">تعذر حفظ إعدادات SSH.</p> : null}
        {sshMutation.isSuccess ? <p className="notice success">تم حفظ إعدادات SSH مؤقتا.</p> : null}
        <p className="metric-note">
          الحالة الحالية: {foundationServerQuery.data?.ssh_access.enabled ? "enabled" : "disabled"} /{" "}
          {foundationServerQuery.data?.ssh_access.auth_method ?? "none"}
        </p>
      </section>
    </div>
  );
}
