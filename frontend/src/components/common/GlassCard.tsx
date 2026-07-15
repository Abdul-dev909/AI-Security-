import type { ReactNode } from 'react';
import './GlassCard.css';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hoverable?: boolean;
  glowing?: boolean;
  onClick?: () => void;
}

export function GlassCard({
  children,
  className = '',
  hoverable = true,
  glowing = false,
  onClick,
}: GlassCardProps) {
  return (
    <div
      className={`glass-card ${hoverable ? 'glass-card--hoverable' : ''} ${glowing ? 'glass-card--glowing' : ''} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => { if (e.key === 'Enter' || e.key === ' ') onClick(); } : undefined}
    >
      {children}
    </div>
  );
}
