interface StatCardProps {
  label: string;
  value: string;
  detail: string;
  icon: string;
}

function StatCard({
  label,
  value,
  detail,
  icon,
}: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <span className="stat-label">{label}</span>
        <span className="stat-icon">{icon}</span>
      </div>

      <div className="stat-value">{value}</div>

      <div className="stat-detail">{detail}</div>
    </div>
  );
}

export default StatCard;