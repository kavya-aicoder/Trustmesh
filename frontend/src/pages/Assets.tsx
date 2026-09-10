import { useEffect, useMemo, useState } from "react";

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import StatusBadge from "../components/ui/StatusBadge";
import { getAssets } from "../services/assets";
import type { Asset } from "../types/api";

function Assets() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function loadAssets() {
      try {
        const response = await getAssets();
        setAssets(response.assets);
      } catch (error) {
        console.error("Failed to load assets:", error);
      } finally {
        setLoading(false);
      }
    }

    loadAssets();
  }, []);

  const filteredAssets = useMemo(() => {
    const query = search.toLowerCase();

    return assets.filter((asset) =>
      `${asset.name} ${asset.asset_id} ${asset.asset_type} ${asset.owner} ${asset.policy}`
        .toLowerCase()
        .includes(query),
    );
  }, [assets, search]);

  const activeCount = assets.filter(
    (asset) => asset.status === "Active",
  ).length;

  const protectedCount = assets.filter(
    (asset) => asset.status === "Protected",
  ).length;

  const typeCount = new Set(
    assets.map((asset) => asset.asset_type),
  ).size;

  return (
    <div className="app-shell">
      <Sidebar />

      <div className="main-area">
        <Topbar />

        <main className="dashboard">
          <section className="page-heading">
            <div>
              <div className="eyebrow">DIGITAL ASSET MANAGEMENT</div>
              <h1>Assets</h1>
              <p>
                Manage digital assets and enforce policy-controlled
                access across TrustLayer.
              </p>
            </div>

            <StatusBadge>Asset layer ready</StatusBadge>
          </section>

          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-card-top">
                <span className="stat-label">TOTAL ASSETS</span>
                <span className="stat-icon">◇</span>
              </div>

              <div className="stat-value">
                {loading ? "…" : assets.length}
              </div>

              <div className="stat-detail">
                Registered digital assets
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-top">
                <span className="stat-label">ACTIVE</span>
                <span className="stat-icon">✓</span>
              </div>

              <div className="stat-value">
                {loading ? "…" : activeCount}
              </div>

              <div className="stat-detail">
                Assets currently active
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-top">
                <span className="stat-label">PROTECTED</span>
                <span className="stat-icon">□</span>
              </div>

              <div className="stat-value">
                {loading ? "…" : protectedCount}
              </div>

              <div className="stat-detail">
                Assets under policy control
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-top">
                <span className="stat-label">ASSET TYPES</span>
                <span className="stat-icon">▣</span>
              </div>

              <div className="stat-value">
                {loading ? "…" : typeCount}
              </div>

              <div className="stat-detail">
                Registered asset categories
              </div>
            </div>
          </section>

          <section className="panel asset-panel">
            <div className="panel-header">
              <div>
                <div className="panel-kicker">ASSET INVENTORY</div>
                <h2>Digital assets</h2>
              </div>

              <button className="primary-action">
                + Register asset
              </button>
            </div>

            <div className="identity-toolbar">
              <div className="identity-search">
                <span>⌕</span>

                <input
                  type="text"
                  placeholder="Search assets..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>

              <button className="filter-button">
                All assets ▾
              </button>
            </div>

            {loading ? (
              <div className="resource-empty">
                <div>◇</div>

                <h3>Loading assets</h3>

                <p>
                  Reading the TrustLayer asset registry.
                </p>
              </div>
            ) : filteredAssets.length === 0 ? (
              <div className="resource-empty">
                <div>⌕</div>

                <h3>No assets found</h3>

                <p>
                  Try a different asset, owner, or policy name.
                </p>
              </div>
            ) : (
              <div className="asset-table">
                <div className="asset-table-header">
                  <span>ASSET</span>
                  <span>TYPE</span>
                  <span>OWNER</span>
                  <span>POLICY</span>
                  <span>ACCESS</span>
                  <span>STATUS</span>
                </div>

                {filteredAssets.map((asset) => (
                  <div
                    className="asset-row"
                    key={asset.asset_id}
                  >
                    <div className="asset-primary">
                      <span className="asset-icon">◇</span>

                      <div>
                        <strong>{asset.name}</strong>
                        <span>{asset.asset_id}</span>
                      </div>
                    </div>

                    <span className="asset-type">
                      {asset.asset_type}
                    </span>

                    <div className="asset-owner">
                      <strong>{asset.owner}</strong>
                      <span>Identity owner</span>
                    </div>

                    <span className="asset-policy">
                      {asset.policy}
                    </span>

                    <span className="asset-access">
                      {asset.access_level}
                    </span>

                    <StatusBadge>{asset.status}</StatusBadge>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}

export default Assets;