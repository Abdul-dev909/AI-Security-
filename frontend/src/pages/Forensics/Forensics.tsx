import { Microscope, FileText } from 'lucide-react';
import { PageHeader } from '../../components/common/PageHeader';
import { GlassCard } from '../../components/common/GlassCard';
import { SectionCard } from '../../components/common/SectionCard';
import './Forensics.css';

const timelineItems = [
  { id: 't1', label: 'Evidence Collection', status: 'pending' },
  { id: 't2', label: 'Data Analysis', status: 'pending' },
  { id: 't3', label: 'Pattern Recognition', status: 'pending' },
  { id: 't4', label: 'Report Generation', status: 'pending' },
];

export function Forensics() {
  return (
    <div className="forensics">
      <PageHeader
        title="Forensics"
        subtitle="Digital forensic analysis and artifact investigation"
      />

      {/* Hero Card */}
      <GlassCard className="forensics__hero" glowing>
        <div className="forensics__hero-icon-wrap">
          <Microscope size={56} className="forensics__hero-icon" />
          <div className="forensics__hero-ring forensics__hero-ring--1" />
          <div className="forensics__hero-ring forensics__hero-ring--2" />
        </div>
        <h2 className="forensics__hero-title">Digital Forensics</h2>
        <p className="forensics__hero-subtitle">
          No forensic artifacts available. Execute attacks and run detection scans to generate forensic data for analysis.
        </p>
      </GlassCard>

      {/* Bottom Grid */}
      <div className="forensics__grid">
        {/* Timeline */}
        <SectionCard title="Analysis Pipeline" subtitle="Forensic processing stages">
          <div className="forensics__timeline">
            {timelineItems.map((item, i) => (
              <div key={item.id} className="forensics__timeline-item" style={{ animationDelay: `${i * 100}ms` }}>
                <div className="forensics__timeline-node">
                  <div className="forensics__timeline-dot" />
                  {i < timelineItems.length - 1 && <div className="forensics__timeline-line" />}
                </div>
                <div className="forensics__timeline-content">
                  <span className="forensics__timeline-label">{item.label}</span>
                  <span className="forensics__timeline-status">Pending</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        {/* Analysis Card */}
        <SectionCard title="Forensic Report" subtitle="Analysis output">
          <div className="forensics__report-placeholder">
            <FileText size={40} className="forensics__report-icon" />
            <p className="forensics__report-text">
              Forensic reports will be generated here after analysis is complete.
              Reports include attack patterns, vulnerability assessments, and mitigation recommendations.
            </p>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
