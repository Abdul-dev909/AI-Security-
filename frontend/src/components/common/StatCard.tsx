import * as LucideIcons from 'lucide-react';
import type { StatusVariant } from '../../types';
import { StatusBadge } from './StatusBadge';
import './StatCard.css';

interface StatCardProps {
  icon: string;
  title: string;
  value: string | number;
  status: StatusVariant;
  statusLabel: string;
  index?: number;
}

export function StatCard({ icon, title, value, status, statusLabel, index = 0 }: StatCardProps) {
  const IconComponent = (LucideIcons as unknown as Record<string, React.ComponentType<{ size?: number; className?: string }>>)[icon];

  return (
    <div className="stat-card" style={{ animationDelay: `${index * 80}ms` }}>
      <div className="stat-card__icon-wrap">
        {IconComponent && <IconComponent size={22} className="stat-card__icon" />}
      </div>
      <div className="stat-card__content">
        <span className="stat-card__title">{title}</span>
        <span className="stat-card__value">{value}</span>
      </div>
      <div className="stat-card__status">
        <StatusBadge variant={status} label={statusLabel} />
      </div>
    </div>
  );
}
