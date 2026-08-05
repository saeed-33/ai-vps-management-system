"use client";

export type TabItem = {
  id: string;
  label: string;
  content: React.ReactNode;
};

export function Tabs({
  tabs,
  activeTab,
  onChange,
}: {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
}) {
  const active = tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

  return (
    <div className="tabs">
      <div className="tab-list" role="tablist" aria-label="Page sections">
        {tabs.map((tab) => (
          <button
            aria-selected={active.id === tab.id}
            className={`tab-button ${active.id === tab.id ? "active" : ""}`}
            key={tab.id}
            onClick={() => onChange(tab.id)}
            role="tab"
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tab-panel" role="tabpanel">
        {active.content}
      </div>
    </div>
  );
}
