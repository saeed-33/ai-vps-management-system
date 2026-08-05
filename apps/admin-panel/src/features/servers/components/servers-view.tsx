"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { KeyRound, Plus, PlugZap, RefreshCw, Server } from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { getStoredAccessToken } from "@/lib/auth-client";
import {
  createServer,
  getServer,
  getServers,
  getServersSummary,
  testServerSshAccess,
  updateServerSshAccess,
} from "@/lib/servers-client";

export function ServersView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();
  const [selectedServerId, setSelectedServerId] = useState("srv-foundation-001");
  const [newServerName, setNewServerName] = useState("");
  const [newServerHostname, setNewServerHostname] = useState("");
  const [newServerIp, setNewServerIp] = useState("");
  const [newServerEnvironment, setNewServerEnvironment] = useState("production");
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

  const selectedServerQuery = useQuery({
    queryKey: ["servers", "detail", selectedServerId],
    queryFn: () => getServer(token ?? "", selectedServerId),
    enabled: Boolean(token && selectedServerId),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createServer(token ?? "", {
        name: newServerName,
        hostname: newServerHostname,
        ip_address: newServerIp || null,
        os_family: "linux",
        environment: newServerEnvironment,
        status: "active",
        assigned_monitoring_profiles: ["profile-linux-baseline"],
        metadata: {},
      }),
    onSuccess: (server) => {
      setSelectedServerId(server.id);
      setNewServerName("");
      setNewServerHostname("");
      setNewServerIp("");
      void serversQuery.refetch();
      void summaryQuery.refetch();
    },
  });

  const sshMutation = useMutation({
    mutationFn: () =>
      updateServerSshAccess(token ?? "", selectedServerId, {
        enabled: sshEnabled,
        host: sshHost || null,
        port: sshPort,
        username: sshUsername || null,
        private_key_path: sshPrivateKeyPath || null,
        password: sshPassword || null,
      }),
    onSuccess: () => {
      setSshPassword("");
      void selectedServerQuery.refetch();
      void serversQuery.refetch();
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

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">Servers</h2>
          <p className="metric-note">Sign in to manage servers.</p>
          <Link className="button primary" href="/login">
            Sign in
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="grid" aria-label="Servers summary">
        <article className="card metric-card">
          <p className="card-title">Total</p>
          <p className="metric-value">{summaryQuery.data?.total ?? "-"}</p>
          <p className="metric-note">Registered servers.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">Active</p>
          <p className="metric-value">{summaryQuery.data?.active ?? "-"}</p>
          <p className="metric-note">Included in periodic monitoring.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">Maintenance</p>
          <p className="metric-value">{summaryQuery.data?.maintenance ?? "-"}</p>
          <p className="metric-note">Excluded from active monitoring.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">Disabled</p>
          <p className="metric-value">{summaryQuery.data?.disabled ?? "-"}</p>
          <p className="metric-note">Not used by the agent.</p>
        </article>
      </section>

      <section className="card side-card">
        <div className="toolbar">
          <h2 className="section-title">Add Server</h2>
          <Plus aria-hidden="true" />
        </div>
        <form className="form-stack" onSubmit={handleCreateSubmit}>
          <label className="field">
            <span>Name</span>
            <input dir="ltr" required value={newServerName} onChange={(event) => setNewServerName(event.target.value)} />
          </label>
          <label className="field">
            <span>Hostname</span>
            <input
              dir="ltr"
              required
              value={newServerHostname}
              onChange={(event) => setNewServerHostname(event.target.value)}
            />
          </label>
          <label className="field">
            <span>IP address</span>
            <input dir="ltr" value={newServerIp} onChange={(event) => setNewServerIp(event.target.value)} />
          </label>
          <label className="field">
            <span>Environment</span>
            <select value={newServerEnvironment} onChange={(event) => setNewServerEnvironment(event.target.value)}>
              <option value="production">production</option>
              <option value="staging">staging</option>
              <option value="development">development</option>
            </select>
          </label>
          <button className="button primary" type="submit" disabled={createMutation.isPending}>
            <Plus aria-hidden="true" />
            {createMutation.isPending ? "Adding" : "Add server"}
          </button>
        </form>
        {createMutation.isError ? <p className="notice danger">Could not add server.</p> : null}
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">Servers</h2>
            <p className="metric-note">Database-backed when PostgreSQL is available, with memory fallback for local trials.</p>
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
            Refresh
          </button>
        </div>

        {serversQuery.isError ? <p className="notice danger">Could not load servers.</p> : null}

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
              <button className="button" type="button" onClick={() => setSelectedServerId(server.id)}>
                {selectedServerId === server.id ? "selected" : "select"}
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="card side-card">
        <div className="toolbar">
          <h2 className="section-title">SSH Access</h2>
          <KeyRound aria-hidden="true" />
        </div>
        <p className="metric-note">
          Selected: <span dir="ltr">{selectedServerId}</span>
        </p>
        <form className="form-stack" onSubmit={handleSshSubmit}>
          <label className="field">
            <span>Enable SSH</span>
            <input type="checkbox" checked={sshEnabled} onChange={(event) => setSshEnabled(event.target.checked)} />
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
            <input dir="ltr" type="password" value={sshPassword} onChange={(event) => setSshPassword(event.target.value)} />
          </label>
          <button className="button primary" type="submit" disabled={sshMutation.isPending}>
            <Server aria-hidden="true" />
            {sshMutation.isPending ? "Saving" : "Save SSH"}
          </button>
        </form>

        <button
          className="button"
          type="button"
          disabled={sshTestMutation.isPending}
          onClick={() => sshTestMutation.mutate()}
        >
          <PlugZap aria-hidden="true" />
          {sshTestMutation.isPending ? "Testing" : "Test SSH"}
        </button>

        {sshMutation.isError ? <p className="notice danger">Could not save SSH settings.</p> : null}
        {sshMutation.isSuccess ? <p className="notice success">SSH settings saved.</p> : null}
        {sshTestMutation.data ? (
          <p className={`notice ${sshTestMutation.data.ok ? "success" : "danger"}`} dir="ltr">
            {sshTestMutation.data.detail}
          </p>
        ) : null}
        {sshTestMutation.isError ? <p className="notice danger">SSH test request failed.</p> : null}
        <p className="metric-note">
          Current: {selectedServerQuery.data?.ssh_access.enabled ? "enabled" : "disabled"} /{" "}
          {selectedServerQuery.data?.ssh_access.auth_method ?? "none"}
        </p>
      </section>
    </div>
  );
}
