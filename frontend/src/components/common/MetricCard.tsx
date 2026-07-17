import * as LucideIcons from 'lucide-react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { AnalyticsMetric } from '../../types';
import './MetricCard.css';

interface MetricCardProps {
  metric: AnalyticsMetric;
  index?: number;
}

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
};

export function MetricCard({ metric, index = 0 }: MetricCardProps) {
  const IconComponent = (LucideIcons as unknown as Record<string, React.ComponentType<{ size?: number; className?: string }>>)[metric.icon];
  const TrendIcon = trendIcons[metric.trend];

  return (
    <div
      className={`metric-card metric-card--${metric.color}`}
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="metric-card__header">
        <div className="metric-card__icon-wrap">
          {IconComponent && <IconComponent size={20} className="metric-card__icon" />}
        </div>
        <span className="metric-card__label">{metric.label}</span>
      </div>
      <div className="metric-card__value">{metric.value}</div>
      <div className={`metric-card__trend metric-card__trend--${metric.trend}`}>
        <TrendIcon size={14} />
        <span>{metric.trendValue}</span>
      </div>
    </div>
  );
}
