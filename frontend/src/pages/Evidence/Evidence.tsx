import { PageHeader } from '../../components/common/PageHeader';
import { SectionCard } from '../../components/common/SectionCard';
import { DataTable } from '../../components/common/DataTable';
import { EmptyState } from '../../components/common/EmptyState';
import type { EvidenceRecord } from '../../types';
import './Evidence.css';

const evidenceColumns = [
  { key: 'timestamp', header: 'Timestamp', width: '180px' },
  { key: 'attackName', header: 'Attack' },
  { key: 'evidenceType', header: 'Evidence Type', width: '160px' },
  { key: 'status', header: 'Status', width: '120px' },
];

const evidenceData: EvidenceRecord[] = [];

export function Evidence() {
  return (
    <div className="evidence">
      <PageHeader
        title="Evidence"
        subtitle="Forensic evidence collection and management"
      />

      <SectionCard title="Evidence Records" subtitle="Collected artifacts from executed attacks">
        {evidenceData.length === 0 ? (
          <EmptyState
            icon="FolderSearch"
            title="No Evidence Records"
            description="Evidence artifacts will appear here after attack executions. Run attacks from the Attack Engine to begin collecting forensic data."
            buttonText="Go to Attack Engine"
            buttonDisabled
          />
        ) : (
          <DataTable<EvidenceRecord>
            columns={evidenceColumns}
            data={evidenceData}
            keyExtractor={(row) => row.id}
          />
        )}
      </SectionCard>
    </div>
  );
}
