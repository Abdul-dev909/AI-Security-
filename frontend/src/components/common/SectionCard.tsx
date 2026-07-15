import type { ReactNode } from 'react';
import './SectionCard.css';

interface SectionCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  actions?: ReactNode;
}

export function SectionCard({ title, subtitle, children, className = '', actions }: SectionCardProps) {
  return (
    <section className={`section-card ${className}`}>
      <div className="section-card__header">
        <div className="section-card__header-text">
          <h2 className="section-card__title">{title}</h2>
          {subtitle && <p className="section-card__subtitle">{subtitle}</p>}
        </div>
        {actions && <div className="section-card__actions">{actions}</div>}
      </div>
      <div className="section-card__body">
        {children}
      </div>
    </section>
  );
}
