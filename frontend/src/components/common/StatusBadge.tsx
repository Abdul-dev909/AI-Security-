import type { StatusVariant } from '../../types';
import './StatusBadge.css';

interface StatusBadgeProps {
  variant: StatusVariant;
  label: string;
}

const variantConfig: Record<StatusVariant, { className: string }> = {
  online: { className: 'status-badge--online' },
  offline: { className: 'status-badge--offline' },
  running: { className: 'status-badge--running' },
  success: { className: 'status-badge--success' },
  failed: { className: 'status-badge--failed' },
  inactive: { className: 'status-badge--inactive' },
  placeholder: { className: 'status-badge--placeholder' },
};

export function StatusBadge({ variant, label }: StatusBadgeProps) {
  const config = variantConfig[variant];

  return (
    <span className={`status-badge ${config.className}`} role="status" aria-label={label}>
      <span className="status-badge__dot" />
      <span className="status-badge__label">{label}</span>
    </span>
  );
}
