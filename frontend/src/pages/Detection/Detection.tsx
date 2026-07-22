import { useSearchParams, useLocation, useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/common/PageHeader';
import { StatCard } from '../../components/common/StatCard';
import { SectionCard } from '../../components/common/SectionCard';
import { EmptyState } from '../../components/common/EmptyState';
import { GlassCard } from '../../components/common/GlassCard';
import { DataTable } from '../../components/common/DataTable';
import { StatusBadge } from '../../components/common/StatusBadge';
import { getExecution } from '../../services/executionStore';
import type { DetectionResultItem, Severity } from '../../types';
import './Detection.css';

const severityMap: Record<Severity | string, { variant: 'failed' | 'placeholder' | 'running' | 'inactive'; label: string }> = {
  critical: { variant: 'failed', label: 'Critical' },
  high: { variant: 'placeholder', label: 'High' },
  medium: { variant: 'running', label: 'Medium' },
  low: { variant: 'inactive', label: 'Low' },
  none: { variant: 'inactive', label: 'None' },
};

export function Detection() {
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const execId = searchParams.get('exec');
  
  const execution = execId ? getExecution(execId) : null;
  const report = execution?.result.detection_report || location.state?.report;
  const attackName = execution?.attack.name || location.state?.attackName || 'Unknown Attack';
  const timestamp = execution?.timestamp ? new Date(execution.timestamp).toLocaleString() : 'Never';

  const detectionMetrics = [
    { 
      id: 'threats', 
      icon: 'ShieldAlert', 
      title: 'Threats Detected', 
      value: report ? report.total_detections.toString() : '0', 
      status: report && report.total_detections > 0 ? 'failed' : 'inactive', 
      statusLabel: report && report.total_detections > 0 ? 'Detections Found' : 'None' 
    },
    { 
      id: 'last-scan', 
      icon: 'Clock', 
      title: 'Last Scan', 
      value: report ? timestamp : 'Never', 
      status: report ? 'success' : 'inactive', 
      statusLabel: report ? 'Completed' : 'Pending' 
    },
    { 
      id: 'engine', 
      icon: 'Cpu', 
      title: 'Detection Engine', 
      value: report ? `${report.detection_time.toFixed(2)}s` : 'Standby', 
      status: report ? 'online' : 'placeholder', 
      statusLabel: report ? 'Active' : 'Ready' 
    },
    { 
      id: 'model', 
      icon: 'Brain', 
      title: 'Model Status', 
      value: 'Loaded', 
      status: 'online', 
      statusLabel: 'Active' 
    },
  ];

  const resultsColumns = [
    { key: 'detector_name', header: 'Detector', width: '200px' },
    { 
      key: 'detected', 
      header: 'Detected', 
      width: '120px',
      render: (row: DetectionResultItem) => (
        <StatusBadge 
          variant={row.detected ? 'failed' : 'inactive'} 
          label={row.detected ? 'Yes' : 'No'} 
        />
      )
    },
    {
      key: 'severity',
      header: 'Severity',
      width: '120px',
      render: (row: DetectionResultItem) => {
        const severity = row.severity || 'none';
        const sevConfig = severityMap[severity] || severityMap.none;
        return <StatusBadge variant={sevConfig.variant} label={sevConfig.label} />;
      }
    },
    { 
      key: 'confidence', 
      header: 'Confidence', 
      width: '120px',
      render: (row: DetectionResultItem) => `${(row.confidence * 100).toFixed(0)}%`
    },
    { key: 'explanation', header: 'Explanation' }
  ];

  const severityCounts = { critical: 0, high: 0, medium: 0, low: 0 };
  if (report) {
    report.results.forEach((r: DetectionResultItem) => {
      if (r.detected && r.severity && r.severity in severityCounts) {
        severityCounts[r.severity as keyof typeof severityCounts]++;
      }
    });
  }

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
            value={metric.value as string}
            status={metric.status as any}
            statusLabel={metric.statusLabel}
            index={i}
          />
        ))}
      </section>

      {report ? (
        <>
          <GlassCard className="detection__context-header" hoverable={false}>
            <div>
              <h3 className="detection__context-title">Results for: {attackName}</h3>
              <span className="detection__context-meta">Executed on {timestamp} • Analysed {report.total_detectors_executed} detectors</span>
            </div>
          </GlassCard>

          <div className="detection__severity-summary">
            <GlassCard className="detection__severity-card detection__severity-card--critical" hoverable={false}>
              <div className="detection__severity-card-label">Critical</div>
              <div className="detection__severity-card-value">{severityCounts.critical}</div>
            </GlassCard>
            <GlassCard className="detection__severity-card detection__severity-card--high" hoverable={false}>
              <div className="detection__severity-card-label">High</div>
              <div className="detection__severity-card-value">{severityCounts.high}</div>
            </GlassCard>
            <GlassCard className="detection__severity-card detection__severity-card--medium" hoverable={false}>
              <div className="detection__severity-card-label">Medium</div>
              <div className="detection__severity-card-value">{severityCounts.medium}</div>
            </GlassCard>
            <GlassCard className="detection__severity-card detection__severity-card--low" hoverable={false}>
              <div className="detection__severity-card-label">Low</div>
              <div className="detection__severity-card-value">{severityCounts.low}</div>
            </GlassCard>
          </div>

          <SectionCard title="Detection Results" subtitle="Detailed breakdown per detector">
            <div className="detection__results-table">
              <DataTable<DetectionResultItem>
                columns={resultsColumns}
                data={report.results}
                keyExtractor={(row) => row.detector_name}
              />
            </div>
          </SectionCard>
        </>
      ) : (
        <SectionCard title="Detection Results" subtitle="Threat analysis output">
          <EmptyState
            icon="ShieldOff"
            title="No Detection Results"
            description="Run attacks to generate detection data. The detection engine will analyze AI model responses for potential vulnerabilities and security issues."
            buttonText="Go to Attack Engine"
            onClick={() => navigate('/attacks')}
          />
        </SectionCard>
      )}

      {/* Evidence Section (Reserved for Module 4) */}
      <SectionCard title="Evidence Collection" subtitle="Forensic evidence from detection analysis" className="detection__evidence">
        <EmptyState
          icon="FileSearch"
          title="No Evidence Collected"
          description="Evidence artifacts will appear here as detection modules generate forensic data. This section will be populated by the Evidence Collection module."
        />
      </SectionCard>
    </div>
  );
}
