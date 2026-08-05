"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { CheckCircle2, Database, KeyRound, Plus, PlugZap, RefreshCw, Server, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { getStoredAccessToken } from "@/lib/auth-client";
import {
  createServer,
  getServer,
  getServers,
  getServersSummary,
  testServerSshAccess,
  updateServerSshAccess,
  type ServerDetail,
  type ServerSummary,
} from "@/lib/servers-client";

const DEFAULT_PROFILE = "profile-linux-baseline";

export function ServersView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();
  const [selectedServerId, setSelectedServerId] = useState("");
  const [newServerName, setNewServerName] = useState("");
  const [newServerHostname, setNewServerHostname] = useState("");
  const [newServerIp, setNewServerIp] = useState("");
  const [newServerOsFamily, setNewServerOsFamily] = useState("linux");
  const [newServerEnvironment, setNewServerEnvironment] = useState("production");
  const [newServerStatus, setNewServerStatus] = useState("active");
  const [newServerProfiles, setNewServerProfiles] = useState(DEFAULT_PROFILE);
  const [sshEnabled, setSshEnabled] = useState(true);
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

  const selectedServerQuery = useQuery({
    queryKey: ["servers", "detail", selectedServerId],
    queryFn: () => getServer(token ?? "", selectedServerId),
    enabled: Boolean(token && selectedServerId),
  });

  const selectedServer = selectedServerQuery.data;
  const servers = useMemo(() => serversQuery.data?.servers ?? [], [serversQuery.data?.servers]);

  useEffect(() => {
    if (servers.length === 0) {
      return;
    }
    if (!selectedServerId || !servers.some((server) => server.id === selectedServerId)) {
      setSelectedServerId(servers[0].id);
    }
  }, [selectedServerId, servers]);

  useEffect(() => {
    if (!selectedServer) {
      return;
    }
    setSshEnabled(selectedServer.ssh_access.enabled);
    setSshHost(selectedServer.ssh_access.host ?? selectedServer.ip_address ?? selectedServer.hostname);
    setSshPort(selectedServer.ssh_access.port);
    setSshUsername(selectedServer.ssh_access.username ?? "");
    setSshPrivateKeyPath(selectedServer.ssh_access.private_key_path ?? "");
    setSshPassword("");
  }, [selectedServer]);

  const createMutation = useMutation({
    mutationFn: () =>
      createServer(token ?? "", {
        name: newServerName.trim(),
        hostname: newServerHostname.trim(),
        ip_address: newServerIp.trim() || null,
        os_family: newServerOsFamily.trim() || null,
        environment: newServerEnvironment,
        status: newServerStatus,
        assigned_monitoring_profiles: splitProfiles(newServerProfiles),
        metadata: {},
      }),
    onSuccess: (server) => {
      setSelectedServerId(server.id);
      setNewServerName("");
      setNewServerHostname("");
      setNewServerIp("");
      setNewServerOsFamily("linux");
      setNewServerEnvironment("production");
      setNewServerStatus("active");
      setNewServerProfiles(DEFAULT_PROFILE);
      setSshHost(server.ip_address ?? server.hostname);
      void serversQuery.refetch();
      void summaryQuery.refetch();
    },
  });

  const sshMutation = useMutation({
    mutationFn: () =>
      updateServerSshAccess(token ?? "", selectedServerId, {
        enabled: sshEnabled,
        host: sshHost.trim() || null,
        port: sshPort,
        username: sshUsername.trim() || null,
        private_key_path: sshPrivateKeyPath.trim() || null,
        password: sshPassword || null,
      }),
    onSuccess: () => {
      setSshPassword("");
      void selectedServerQuery.refetch();
      void serversQuery.refetch();
      void summaryQuery.refetch();
    },
  });

  const sshTestMutation = useMutation({
    mutationFn: () => testServerSshAccess(token ?? "", selectedServerId),
  });

  function handleCreateSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.mutate();
  }

  function handleSshSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    sshMutation.mutate();
  }

  function selectServer(server: ServerSummary) {
    setSelectedServerId(server.id);
    setSshHost(server.ip_address ?? server.hostname);
    sshTestMutation.reset();
    sshMutation.reset();
  }

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">إدارة السيرفرات</h2>
          <p className="metric-note">يجب تسجيل الدخول لإضافة السيرفرات وإعداد SSH.</p>
          <Link className="button primary" href="/login">
            تسجيل الدخول
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="grid" aria-label="Servers summary">
        <MetricCard title="الإجمالي" value={summaryQuery.data?.total ?? "-"} note="كل السيرفرات المسجلة." />
        <MetricCard title="نشطة" value={summaryQuery.data?.active ?? "-"} note="تدخل في المراقبة الدورية." />
        <MetricCard title="صيانة" value={summaryQuery.data?.maintenance ?? "-"} note="خارج المراقبة أثناء الصيانة." />
        <MetricCard title="معطلة" value={summaryQuery.data?.disabled ?? "-"} note="لا يستخدمها الوكيل." />
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">إضافة سيرفر</h2>
            <p className="metric-note">أدخل بيانات السيرفر أولا، ثم اختره من القائمة واحفظ إعدادات SSH.</p>
          </div>
          <DatabaseStatus servers={servers} />
        </div>

        <form className="form-stack form-wide" onSubmit={handleCreateSubmit}>
          <div className="form-grid">
            <label className="field">
              <span>اسم السيرفر</span>
              <input
                dir="ltr"
                required
                placeholder="prod-app-01"
                value={newServerName}
                onChange={(event) => setNewServerName(event.target.value)}
              />
            </label>
            <label className="field">
              <span>Hostname</span>
              <input
                dir="ltr"
                required
                placeholder="prod-app-01.example.com"
                value={newServerHostname}
                onChange={(event) => setNewServerHostname(event.target.value)}
              />
            </label>
            <label className="field">
              <span>IP اختياري</span>
              <input dir="ltr" placeholder="203.0.113.10" value={newServerIp} onChange={(event) => setNewServerIp(event.target.value)} />
            </label>
            <label className="field">
              <span>نظام التشغيل</span>
              <select value={newServerOsFamily} onChange={(event) => setNewServerOsFamily(event.target.value)}>
                <option value="linux">linux</option>
                <option value="ubuntu">ubuntu</option>
                <option value="debian">debian</option>
                <option value="centos">centos</option>
              </select>
            </label>
            <label className="field">
              <span>البيئة</span>
              <select value={newServerEnvironment} onChange={(event) => setNewServerEnvironment(event.target.value)}>
                <option value="production">production</option>
                <option value="staging">staging</option>
                <option value="development">development</option>
              </select>
            </label>
            <label className="field">
              <span>الحالة</span>
              <select value={newServerStatus} onChange={(event) => setNewServerStatus(event.target.value)}>
                <option value="active">active</option>
                <option value="maintenance">maintenance</option>
                <option value="disabled">disabled</option>
              </select>
            </label>
          </div>
          <label className="field">
            <span>ملفات المراقبة</span>
            <input
              dir="ltr"
              value={newServerProfiles}
              onChange={(event) => setNewServerProfiles(event.target.value)}
              placeholder="profile-linux-baseline"
            />
          </label>
          <div className="toolbar">
            <button className="button primary" type="submit" disabled={createMutation.isPending}>
              <Plus aria-hidden="true" />
              {createMutation.isPending ? "جاري الإضافة" : "إضافة السيرفر"}
            </button>
            {createMutation.isSuccess ? <span className="badge success">تم الحفظ</span> : null}
          </div>
        </form>
        {createMutation.isError ? <p className="notice danger">{errorText(createMutation.error)}</p> : null}
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">السيرفرات</h2>
            <p className="metric-note">اختر سيرفرا لإعداد SSH أو اختبار الاتصال.</p>
          </div>
          <button
            className="button"
            type="button"
            onClick={() => {
              void serversQuery.refetch();
              void summaryQuery.refetch();
              void selectedServerQuery.refetch();
            }}
          >
            <RefreshCw aria-hidden="true" />
            تحديث
          </button>
        </div>

        {serversQuery.isError ? <p className="notice danger">{errorText(serversQuery.error)}</p> : null}

        <ul className="status-list server-list">
          {servers.map((server) => (
            <li className={`status-row server-row ${selectedServerId === server.id ? "selected" : ""}`} key={server.id}>
              <div>
                <strong>{server.name}</strong>
                <span dir="ltr">{server.hostname}</span>
                <span>
                  {server.environment} / {server.os_family ?? "unknown"} / {server.status}
                </span>
                <span>{server.monitoring_status}</span>
              </div>
              <div className="row-actions">
                <span className={`badge ${persistenceBadge(server.source)}`}>{persistenceLabel(server.source)}</span>
                <button className={selectedServerId === server.id ? "button primary" : "button"} type="button" onClick={() => selectServer(server)}>
                  {selectedServerId === server.id ? "محدد" : "اختيار"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">إعداد SSH</h2>
            <p className="metric-note">
              السيرفر المحدد: <span dir="ltr">{selectedServer?.name ?? selectedServerId}</span>
            </p>
          </div>
          <KeyRound aria-hidden="true" />
        </div>

        {selectedServer ? <SelectedServerSummary server={selectedServer} /> : null}

        <form className="form-stack form-wide" onSubmit={handleSshSubmit}>
          <label className="field checkbox-field">
            <span>تفعيل SSH لهذا السيرفر</span>
            <input type="checkbox" checked={sshEnabled} onChange={(event) => setSshEnabled(event.target.checked)} />
          </label>
          <div className="form-grid">
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
                placeholder="C:\\Users\\SAEED\\.ssh\\id_rsa"
                value={sshPrivateKeyPath}
                onChange={(event) => setSshPrivateKeyPath(event.target.value)}
              />
            </label>
          </div>
          <label className="field">
            <span>Password</span>
            <input dir="ltr" type="password" value={sshPassword} onChange={(event) => setSshPassword(event.target.value)} />
          </label>

          <div className="toolbar">
            <button className="button primary" type="submit" disabled={sshMutation.isPending || !selectedServer}>
              <Server aria-hidden="true" />
              {sshMutation.isPending ? "جاري الحفظ" : "حفظ SSH"}
            </button>
            <button
              className="button"
              type="button"
              disabled={sshTestMutation.isPending || !selectedServer}
              onClick={() => sshTestMutation.mutate()}
            >
              <PlugZap aria-hidden="true" />
              {sshTestMutation.isPending ? "جاري الاختبار" : "اختبار SSH"}
            </button>
          </div>
        </form>

        {selectedServer?.ssh_access.has_password ? (
          <p className="notice">يوجد password محفوظ لهذا السيرفر. اترك الحقل فارغا إذا لم تكن تريد تغييره.</p>
        ) : null}
        {sshMutation.isError ? <p className="notice danger">{errorText(sshMutation.error)}</p> : null}
        {sshMutation.isSuccess ? <p className="notice success">تم حفظ إعدادات SSH. نفذ اختبار الاتصال قبل تشغيل المراقبة.</p> : null}
        {sshTestMutation.data ? (
          <p className={`notice ${sshTestMutation.data.ok ? "success" : "danger"}`} dir="ltr">
            {sshTestMutation.data.detail}
          </p>
        ) : null}
        {sshTestMutation.isError ? <p className="notice danger">{errorText(sshTestMutation.error)}</p> : null}
      </section>
    </div>
  );
}

function MetricCard({ title, value, note }: { title: string; value: string | number; note: string }) {
  return (
    <article className="card metric-card">
      <p className="card-title">{title}</p>
      <p className="metric-value">{value}</p>
      <p className="metric-note">{note}</p>
    </article>
  );
}

function DatabaseStatus({ servers }: { servers: ServerSummary[] }) {
  const hasMemoryFallback = servers.some((server) => server.source !== "database");
  return (
    <span className={`badge ${hasMemoryFallback ? "warning" : "success"}`}>
      <Database aria-hidden="true" />
      {hasMemoryFallback ? "تحقق من الحفظ" : "محفوظ"}
    </span>
  );
}

function SelectedServerSummary({ server }: { server: ServerDetail }) {
  return (
    <ul className="status-list">
      <li className="status-row">
        <div>
          <strong>{server.name}</strong>
          <span dir="ltr">{server.hostname}</span>
          <span>
            {server.environment} / {server.status} / {persistenceLabel(server.source)}
          </span>
        </div>
        <div className="row-actions">
          <span className={`badge ${server.ssh_access.enabled ? "success" : "neutral"}`}>
            <ShieldCheck aria-hidden="true" />
            {server.ssh_access.enabled ? server.ssh_access.auth_method : "ssh disabled"}
          </span>
          {server.source === "database" ? (
            <span className="badge success">
              <CheckCircle2 aria-hidden="true" />
              دائم
            </span>
          ) : (
            <span className="badge warning">غير دائم</span>
          )}
        </div>
      </li>
    </ul>
  );
}

function splitProfiles(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function persistenceLabel(source: string) {
  return source === "database" ? "محفوظ" : "غير دائم";
}

function persistenceBadge(source: string) {
  return source === "database" ? "success" : "warning";
}

function errorText(error: unknown) {
  return error instanceof Error ? error.message : "حدث خطأ غير متوقع.";
}
