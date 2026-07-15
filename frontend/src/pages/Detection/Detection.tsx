import { PageHeader } from '../../components/common/PageHeader';
import { StatCard } from '../../components/common/StatCard';
import { SectionCard } from '../../components/common/SectionCard';
import { EmptyState } from '../../components/common/EmptyState';
import './Detection.css';

const detectionMetrics = [
  { id: 'threats', icon: 'ShieldAlert', title: 'Threats Detected', value: '0', status: 'inactive' as const, statusLabel: 'None' },
  { id: 'last-scan', icon: 'Clock', title: 'Last Scan', value: 'Never', status: 'inactive' as const, statusLabel: 'Pending' },
  { id: 'engine', icon: 'Cpu', title: 'Detection Engine', value: 'Standby', status: 'placeholder' as const, statusLabel: 'Ready' },
  { id: 'model', icon: 'Brain', title: 'Model Status', value: 'Loaded', status: 'online' as const, statusLabel: 'Active' },
];

export function Detection() {
  return (
    <div className="detection">
      <PageHeader
        title="Detection"
        subtitle="AI-powered threat detection and analysis engine"
      />

      {/* Detection Metrics */}
      <section className="detection__metrics" aria-label="Detection metrics">
        {detectionMetrics.map((metric, i) => (
          <StatCard
            key={metric.id}
            icon={metric.icon}
            title={metric.title}
            value={metric.value}
            status={metric.status}
            statusLabel={metric.statusLabel}
            index={i}
          />
        ))}
      </section>

      {/* Empty State */}
      <SectionCard title="Detection Results" subtitle="Threat analysis output">
        <EmptyState
          icon="ShieldOff"
          title="No Detection Results"
          description="Run attacks to generate detection data. The detection engine will analyze AI model responses for potential vulnerabilities and security issues."
          buttonText="Start Detection Scan"
          buttonDisabled
        />
      </SectionCard>
    </div>
  );
}
