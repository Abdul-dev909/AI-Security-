import { PageHeader } from '../../components/common/PageHeader';
import { MetricCard } from '../../components/common/MetricCard';
import { PlaceholderPanel } from '../../components/common/PlaceholderPanel';
import { SectionCard } from '../../components/common/SectionCard';
import { analyticsMetrics } from '../../mock/mockAnalytics';
import './Analytics.css';

export function Analytics() {
  return (
    <div className="analytics">
      <PageHeader
        title="Analytics"
        subtitle="Security metrics, performance analysis, and system intelligence"
      />

      {/* Metric Cards */}
      <section className="analytics__metrics" aria-label="Analytics metrics">
        {analyticsMetrics.map((metric, i) => (
          <MetricCard key={metric.id} metric={metric} index={i} />
        ))}
      </section>

      {/* Chart Placeholder */}
      <SectionCard title="Attack Analysis" subtitle="Threat detection over time">
        <PlaceholderPanel
          title="Attack Success Rate — Timeline"
          subtitle="Connect backend to populate real-time analytics"
          height="360px"
        />
      </SectionCard>

      {/* Secondary Charts Row */}
      <div className="analytics__charts-row">
        <SectionCard title="Category Breakdown" subtitle="Attacks by type">
          <PlaceholderPanel
            title="Category Distribution"
            subtitle="Pie chart visualization"
            height="240px"
          />
        </SectionCard>

        <SectionCard title="Severity Heatmap" subtitle="Risk distribution">
          <PlaceholderPanel
            title="Severity Analysis"
            subtitle="Heatmap visualization"
            height="240px"
          />
        </SectionCard>
      </div>
    </div>
  );
}
