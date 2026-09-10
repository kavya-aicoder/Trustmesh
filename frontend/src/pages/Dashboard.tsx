import { useEffect, useState } from "react";

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import StatCard from "../components/ui/StatCard";
import StatusBadge from "../components/ui/StatusBadge";
import { getAuditEvents } from "../services/audit";
import type { AuditEvent } from "../types/api";

function Dashboard() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [auditLoading, setAuditLoading] = useState(true);

  useEffect(() => {
    async function loadAuditEvents() {
      try {
        const response = await getAuditEvents();
        setEvents(response.events);
      } catch (error) {
        console.error("Failed to load audit events:", error);
      } finally {
        setAuditLoading(false);
      }
    }

    loadAuditEvents();
  }, []);

  return (
    <div className="app-shell">
      <Sidebar />

      <div className="main-area">
        <Topbar />

        <main className="dashboard">
          <section className="page-heading">
            <div>
              <div className="eyebrow">CONTROL PLANE</div>

              <h1>Security overview</h1>

              <p>
                Monitor identity, access policies, assets, and security
                activity from one place.
              </p>
            </div>

            <StatusBadge>System protected</StatusBadge>
          </section>

          <section className="stats-grid">
            <StatCard
              label="IDENTITIES"
              value="—"
              detail="Awaiting identity index"
              icon="◉"
            />

            <StatCard
              label="ACTIVE POLICIES"
              value="—"
              detail="PolicyEngine pending"
              icon="◇"
            />

            <StatCard
              label="DIGITAL ASSETS"
              value="—"
              detail="Asset index pending"
              icon="◆"
            />

            <StatCard
              label="SECURITY EVENTS"
              value={auditLoading ? "…" : String(events.length)}
              detail={
                auditLoading
                  ? "Loading audit index"
                  : events.length === 0
                    ? "No indexed events"
                    : "Indexed blockchain events"
              }
              icon="⌁"
            />
          </section>

          <section className="content-grid">
            <div className="panel activity-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-kicker">ACTIVITY</div>

                  <h2>Recent security events</h2>
                </div>

                <button className="text-button">View audit log →</button>
              </div>

              {auditLoading ? (
                <div className="empty-state">
                  <div className="empty-icon">⌁</div>

                  <h3>Loading activity</h3>

                  <p>Reading the TrustLayer audit index.</p>
                </div>
              ) : events.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">⌁</div>

                  <h3>No indexed activity yet</h3>

                  <p>
                    Blockchain audit events will appear here once the
                    finalized contract indexer is connected.
                  </p>
                </div>
              ) : (
                <div className="activity-list">
                  {events.slice(0, 6).map((event) => (
                    <div
                      className="activity-row"
                      key={`${event.transaction_hash}-${event.log_index}`}
                    >
                      <div>
                        <strong>{event.event_name}</strong>

                        <span>
                          Block {event.block_number} ·{" "}
                          {event.transaction_hash.slice(0, 10)}…
                        </span>
                      </div>

                      <span className="activity-action">Indexed</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="panel security-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-kicker">SECURITY</div>

                  <h2>Protection status</h2>
                </div>
              </div>

              <div className="security-list">
                <div className="security-row">
                  <div>
                    <strong>Identity layer</strong>
                    <span>DID verification</span>
                  </div>

                  <StatusBadge>Ready</StatusBadge>
                </div>

                <div className="security-row">
                  <div>
                    <strong>Policy engine</strong>
                    <span>Access decisions</span>
                  </div>

                  <StatusBadge>Ready</StatusBadge>
                </div>

                <div className="security-row">
                  <div>
                    <strong>Audit pipeline</strong>
                    <span>Event indexing</span>
                  </div>

                  <StatusBadge variant="warning">Pending</StatusBadge>
                </div>

                <div className="security-row">
                  <div>
                    <strong>AI security agent</strong>
                    <span>Threat analysis</span>
                  </div>

                  <StatusBadge variant="neutral">Offline</StatusBadge>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Dashboard;