"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { RefreshCw, ScrollText } from "lucide-react";
import { useState } from "react";
import { Tabs } from "@/components/ui/tabs";
import { getStoredAccessToken } from "@/lib/auth-client";
import {
  createMonitoringProfile,
  getMonitoringProfiles,
  getMonitoringProfilesSummary,
  type MonitoringInstruction,
} from "@/lib/monitoring-profiles-client";

const DEFAULT_INSTRUCTIONS = JSON.stringify(
  [
    {
      id: "custom-uptime",
      title: "Collect uptime",
      tool_code: "custom_uptime",
      command: "uptime",
      purpose: "Collect load and uptime evidence.",
      parser: "uptime",
      expected_evidence: ["load average"],
      read_only: true,
    },
  ],
  null,
  2,
);

export function MonitoringProfilesView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();
  const [activeTab, setActiveTab] = useState("profiles");
  const [profileId, setProfileId] = useState("");
  const [name, setName] = useState("");
  const [domain, setDomain] = useState("system");
  const [description, setDescription] = useState("");
  const [instructionsJson, setInstructionsJson] = useState(DEFAULT_INSTRUCTIONS);
  const [formError, setFormError] = useState<string | null>(null);

  const profilesQuery = useQuery({
    queryKey: ["monitoring-profiles", "list"],
    queryFn: () => getMonitoringProfiles(token ?? ""),
    enabled: Boolean(token),
  });

  const summaryQuery = useQuery({
    queryKey: ["monitoring-profiles", "summary"],
    queryFn: () => getMonitoringProfilesSummary(token ?? ""),
    enabled: Boolean(token),
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!token) throw new Error("Missing access token.");
      const instructions = parseInstructions(instructionsJson);
      return createMonitoringProfile(token, {
        id: profileId,
        name,
        domain,
        status: "active",
        description,
        monitoring_instructions: instructions,
        analysis_instructions: [
          "Use the collected raw command evidence as the primary diagnostic input.",
          "Do not produce a conclusion when evidence is incomplete; state the missing evidence.",
        ],
        specialist_agents: [],
      });
    },
    onSuccess: () => {
      setFormError(null);
      setProfileId("");
      setName("");
      setDescription("");
      setInstructionsJson(DEFAULT_INSTRUCTIONS);
      void profilesQuery.refetch();
      void summaryQuery.refetch();
      setActiveTab("profiles");
    },
    onError: (error) => {
      setFormError(error instanceof Error ? error.message : "Could not create monitoring profile.");
    },
  });

  const domains = Object.entries(summaryQuery.data?.by_domain ?? {});

  return (
    <div className="page-stack">
      <section className="grid" aria-label="Monitoring profiles summary">
        <MetricCard title="Total" value={summaryQuery.data?.total ?? "-"} note="Defined monitoring profiles." />
        <MetricCard title="Active" value={summaryQuery.data?.active ?? "-"} note="Profiles available for periodic collection." />
        <MetricCard title="Draft" value={summaryQuery.data?.draft ?? "-"} note="Profiles not ready for execution yet." />
        <MetricCard title="Domains" value={domains.length || "-"} note="Monitoring domains covered by profiles." />
      </section>

      <Tabs
        activeTab={activeTab}
        onChange={setActiveTab}
        tabs={[
          {
            id: "profiles",
            label: "Profiles",
            content: (
              <section className="card wide-card">
                <div className="toolbar">
                  <div>
                    <h2 className="section-title">Monitoring Profiles</h2>
                    <p className="metric-note">Each profile defines the read-only instructions the agent runs during periodic monitoring.</p>
                  </div>
                  <button
                    className="button primary"
                    type="button"
                    onClick={() => {
                      void profilesQuery.refetch();
                      void summaryQuery.refetch();
                    }}
                  >
                    <RefreshCw aria-hidden="true" />
                    Refresh
                  </button>
                </div>

                {profilesQuery.isError ? <p className="notice danger">Could not load monitoring profiles.</p> : null}

                <ul className="status-list">
                  {(profilesQuery.data?.profiles ?? []).map((profile) => (
                    <li className="status-row" key={profile.id}>
                      <div>
                        <strong>{profile.name}</strong>
                        <span dir="ltr">{profile.id}</span>
                        <span>
                          {profile.domain} / v{profile.version} / {profile.instructions_count} instructions /{" "}
                          {profile.assigned_servers} servers
                        </span>
                        <span>{profile.specialist_agents.join(", ") || "no specialist agents"}</span>
                      </div>
                      <span className={`badge ${profile.status === "active" ? "success" : "neutral"}`}>{profile.status}</span>
                    </li>
                  ))}
                </ul>
              </section>
            ),
          },
          {
            id: "create",
            label: "Define Instructions",
            content: (
              <section className="card wide-card">
                <div className="toolbar">
                  <div>
                    <h2 className="section-title">Define Monitoring Instructions</h2>
                    <p className="metric-note">Commands are registered as read-only instructions and executed by the periodic monitoring agent.</p>
                  </div>
                </div>
                <div className="form-grid">
                  <label className="field">
                    Profile ID
                    <input dir="ltr" value={profileId} onChange={(event) => setProfileId(event.target.value)} placeholder="profile-custom-linux" />
                  </label>
                  <label className="field">
                    Name
                    <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Custom Linux Checks" />
                  </label>
                  <label className="field">
                    Domain
                    <input dir="ltr" value={domain} onChange={(event) => setDomain(event.target.value)} placeholder="system" />
                  </label>
                  <label className="field">
                    Description
                    <input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Read-only evidence collection profile." />
                  </label>
                </div>
                <label className="field">
                  Instructions JSON
                  <textarea
                    className="json-textarea"
                    dir="ltr"
                    value={instructionsJson}
                    onChange={(event) => setInstructionsJson(event.target.value)}
                    spellCheck={false}
                  />
                </label>
                {formError ? <p className="notice danger">{formError}</p> : null}
                <button
                  className="button primary"
                  disabled={createMutation.isPending}
                  onClick={() => {
                    setFormError(null);
                    try {
                      parseInstructions(instructionsJson);
                      createMutation.mutate();
                    } catch (error) {
                      setFormError(error instanceof Error ? error.message : "Invalid instructions JSON.");
                    }
                  }}
                  type="button"
                >
                  <ScrollText aria-hidden="true" />
                  Save Profile
                </button>
              </section>
            ),
          },
        ]}
      />
    </div>
  );
}

function MetricCard({ title, value, note }: { title: string; value: number | string; note: string }) {
  return (
    <article className="card metric-card">
      <p className="card-title">{title}</p>
      <p className="metric-value">{value}</p>
      <p className="metric-note">{note}</p>
    </article>
  );
}

function parseInstructions(value: string): MonitoringInstruction[] {
  const parsed = JSON.parse(value);
  if (!Array.isArray(parsed)) throw new Error("Instructions must be a JSON array.");
  return parsed.map((instruction) => ({
    id: String(instruction.id ?? ""),
    title: String(instruction.title ?? ""),
    tool_code: String(instruction.tool_code ?? ""),
    command: String(instruction.command ?? ""),
    purpose: String(instruction.purpose ?? ""),
    parser: instruction.parser === undefined ? null : instruction.parser,
    expected_evidence: Array.isArray(instruction.expected_evidence)
      ? instruction.expected_evidence.map((item: unknown) => String(item))
      : [],
    read_only: instruction.read_only !== false,
  }));
}
