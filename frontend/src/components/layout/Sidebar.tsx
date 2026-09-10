import { NavLink } from "react-router-dom";

const navigation = [
  { label: "Overview", path: "/dashboard", icon: "⌂" },
  { label: "Identities", path: "/identities", icon: "◉" },
  { label: "Policies", path: "/policies", icon: "◇" },
  { label: "Resources", path: "/resources", icon: "▣" },
  { label: "Assets", path: "/assets", icon: "◆" },
  { label: "Audit Log", path: "/audit", icon: "≡" },
  { label: "Security Center", path: "/security", icon: "⌁" },
  { label: "Recovery", path: "/recovery", icon: "◎" },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">T</div>

        <div>
          <div className="brand-name">TrustLayer</div>
          <div className="brand-subtitle">Security Infrastructure</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-label">PLATFORM</div>

        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="network-dot" />
        <div>
          <div className="network-title">Polygon Amoy</div>
          <div className="network-status">Development network</div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;