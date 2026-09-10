function Topbar() {
  return (
    <header className="topbar">
      <div>
        <div className="breadcrumb">Workspace / Overview</div>
      </div>

      <div className="topbar-actions">
        <button className="icon-button" aria-label="Notifications">
          ◌
        </button>

        <div className="wallet-chip">
          <span className="wallet-status" />
          <span>Not connected</span>
        </div>

        <div className="avatar">K</div>
      </div>
    </header>
  );
}

export default Topbar;