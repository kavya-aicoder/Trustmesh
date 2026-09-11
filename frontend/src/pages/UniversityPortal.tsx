import { useState } from "react";

import StatusBadge from "../components/ui/StatusBadge";
import Icon from "../components/ui/Icon";
import {
  authorizeResource,
  simulateAttack,
  simulatePolicyImpact,
} from "../services/demo";
import type {
  AttackSimulationResult,
  DemoAccessResult,
  PolicySimulationResult,
} from "../services/demo";

function UniversityPortal() {
  const employeeIdentity = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8";
  const adminIdentity = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC";
  const [identity, setIdentity] = useState<"Employee" | "Admin">("Employee");
  const [resourceAccess, setResourceAccess] = useState<DemoAccessResult | null>(null);
  const [adminAccess, setAdminAccess] = useState<DemoAccessResult | null>(null);
  const [simulation, setSimulation] = useState<AttackSimulationResult | null>(null);
  const [policySimulation, setPolicySimulation] = useState<PolicySimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadResourceAccess() {
    setError("");
    try {
      setResourceAccess(await authorizeResource({
        org_id: "acme-organization",
        did: identity === "Employee" ? employeeIdentity : adminIdentity,
        role: identity,
        resource_id: "acme-employee-records",
        action: "READ",
      }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to check access.");
    }
  }

  async function loadAdminAccess() {
    setError("");
    try {
      setAdminAccess(await authorizeResource({
        org_id: "acme-organization",
        did: identity === "Employee" ? employeeIdentity : adminIdentity,
        role: identity,
        resource_id: "acme-admin-console",
        action: "ADMIN",
      }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to check admin access.");
    }
  }

  async function runSimulation() {
    setLoading(true);
    setError("");
    try {
      setSimulation(await simulateAttack({
        org_id: "acme-organization",
        did: employeeIdentity,
        role: "Employee",
        resource_id: "acme-admin-console",
        action: "ADMIN",
      }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to simulate the attack.");
    } finally {
      setLoading(false);
    }
  }

  async function runPolicySimulation() {
    try {
      setPolicySimulation(await simulatePolicyImpact({
        org_id: "acme-organization",
        did: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        role: "Employee",
        resource_id: "acme-employee-records",
        action: "READ",
        simulated_decision: "DENY",
      }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to simulate policy impact.");
    }
  }

  return (
    <div className="external-app-shell">
      <header className="external-app-header">
        <div className="external-app-brand">
          <span className="external-app-mark">A</span>
          <div>
            <strong>Acme Organization</strong>
            <span>Internal operations portal</span>
          </div>
        </div>
        <span className="external-protection-mark">
          <Icon name="shield" /> Protected by TrustMesh
        </span>
      </header>

      <main className="external-app-content portal-page">
          <section className="page-heading">
            <div>
              <div className="eyebrow">ACME OPERATIONS</div>
              <h1>Access workspace</h1>
              <p>Review protected resources and validate organization access decisions.</p>
            </div>
            <StatusBadge>Demo environment</StatusBadge>
          </section>

          <section className="external-identity-bar">
            <div>
              <span className="panel-kicker">ACTIVE ORGANIZATION IDENTITY</span>
              <strong>{identity} access profile</strong>
            </div>
            <div className="identity-selector" role="group" aria-label="Select demo identity">
              <button type="button" className={identity === "Employee" ? "active" : ""} onClick={() => { setIdentity("Employee"); setResourceAccess(null); setAdminAccess(null); }}>Employee</button>
              <button type="button" className={identity === "Admin" ? "active" : ""} onClick={() => { setIdentity("Admin"); setResourceAccess(null); setAdminAccess(null); }}>Admin</button>
            </div>
            <code>{identity === "Employee" ? employeeIdentity : adminIdentity}</code>
          </section>

          <section className="portal-banner">
            <div className="portal-banner-mark"><Icon name="shield" /></div>
            <div>
              <strong>Signed in as Jordan Lee</strong>
              <span>0x7099...79C8 · Employee role</span>
            </div>
            <span className="portal-identity-chip">Authorization active</span>
          </section>

          <section className="portal-grid">
            <article className="panel portal-resource-card">
              <div className="panel-kicker">PROTECTED RESOURCE</div>
              <h2>Employee Records</h2>
              <p>Profile, team assignments, and organization records.</p>
              <button type="button" className="primary-action" onClick={loadResourceAccess}>
                {identity === "Employee" ? "View employee records" : "View employee records as Admin"}
              </button>
              {resourceAccess && (
                <div className={`portal-decision ${resourceAccess.allowed ? "allowed" : "denied"}`}>
                  <strong>{resourceAccess.decision}</strong>
                  <span>Policy decision for {identity} → Employee Records</span>
                </div>
              )}
              {resourceAccess?.allowed && (
                <div className="portal-protected-content">
                  <strong>Employee records available</strong>
                  <span>Protected content rendered only after an ALLOWED decision.</span>
                </div>
              )}
            </article>

            <article className="panel portal-resource-card portal-admin-card">
              <div className="panel-kicker">PROTECTED ADMIN RESOURCE</div>
              <h2>Admin Console</h2>
              <p>Organization-wide identity, policy, and security administration.</p>
              <button type="button" className="primary-action" onClick={loadAdminAccess} disabled={loading}>
                <Icon name="shield" />
                {loading ? "Checking policy..." : `Open Admin Console as ${identity}`}
              </button>
              {adminAccess && (
                <div className={`portal-decision ${adminAccess.allowed ? "allowed" : "denied"}`}>
                  <strong>{adminAccess.decision}</strong>
                  <span>{identity} → Admin Console · {adminAccess.allowed ? "Admin action permitted" : "Admin action denied"}</span>
                </div>
              )}
              {adminAccess?.allowed && (
                <div className="portal-protected-content">
                  <strong>Admin console available</strong>
                  <span>Protected administration rendered after an ALLOWED decision.</span>
                </div>
              )}
            </article>
          </section>

          <section className="portal-tools">
            <article className="panel portal-tool-card">
              <div className="panel-kicker">CONTROLLED SECURITY TEST</div>
              <h2>Attack Simulation Mode</h2>
              <p>Run seven Employee admin attempts to demonstrate anomaly detection, escalation, restriction, and suspension.</p>
              <button type="button" className="attack-action" onClick={runSimulation} disabled={loading}>
                <Icon name="shield" />
                {loading ? "Running simulation..." : "Simulate Attack"}
              </button>
              {simulation && (
                <div className="portal-decision denied">
                  <strong>{simulation.attempts.length} synthetic attempts · {simulation.final.severity}</strong>
                  <span>{simulation.final.suspended ? "Identity suspended" : simulation.final.adaptive_state}</span>
                </div>
              )}
            </article>

            <article className="panel portal-tool-card">
              <div className="panel-kicker">POLICY IMPACT SIMULATOR</div>
              <h2>Test a policy change</h2>
              <p>Preview a denial without mutating the active PolicyEngine policy.</p>
              <button type="button" className="primary-action" onClick={runPolicySimulation}>
                Simulate Employee Records denial
              </button>
              {policySimulation && (
                <div className="portal-decision denied">
                  <strong>{policySimulation.current_decision} → {policySimulation.simulated_decision}</strong>
                  <span>Simulation only · policy unchanged</span>
                </div>
              )}
            </article>
          </section>

          {error && <div className="security-load-error" role="alert"><Icon name="shield" /><span>{error}</span></div>}

          <section className="portal-flow panel">
            <div className="panel-kicker">ACCESS CONTROL STATUS</div>
            <div className="portal-flow-steps">
              <span>Employee identity</span><b>→</b><span>Policy decision</span><b>→</b><span>Access outcome</span><b>→</b><span>Security record</span>
            </div>
          </section>
      </main>
    </div>
  );
}

export default UniversityPortal;