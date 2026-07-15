import type { AnalyticsMetric } from '../types';

export const analyticsMetrics: AnalyticsMetric[] = [
  {
    id: 'metric-success-rate',
    icon: 'Target',
    label: 'Attack Success Rate',
    value: '62%',
    trend: 'up',
    trendValue: '+8%',
    color: 'danger',
  },
  {
    id: 'metric-detection-accuracy',
    icon: 'Shield',
    label: 'Detection Accuracy',
    value: '94%',
    trend: 'up',
    trendValue: '+3%',
    color: 'success',
  },
  {
    id: 'metric-memory-usage',
    icon: 'HardDrive',
    label: 'Memory Usage',
    value: '2.4 MB',
    trend: 'neutral',
    trendValue: '—',
    color: 'primary',
  },
  {
    id: 'metric-system-health',
    icon: 'Activity',
    label: 'System Health',
    value: '98%',
    trend: 'up',
    trendValue: '+1%',
    color: 'secondary',
  },
];
