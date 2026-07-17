import { useState } from 'react';
import { Search, AlertTriangle } from 'lucide-react';
import { PageHeader } from '../../components/common/PageHeader';
import { GlassCard } from '../../components/common/GlassCard';
import { SectionCard } from '../../components/common/SectionCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { PrimaryButton } from '../../components/common/PrimaryButton';
import { DataTable } from '../../components/common/DataTable';
import { attackLibrary, attackCategories } from '../../mock/mockAttacks';
import { executionHistory } from '../../mock/mockHistory';
import type { ExecutionHistoryRow, Severity } from '../../types';
import './AttackEngine.css';

const severityMap: Record<Severity, { variant: 'failed' | 'placeholder' | 'running' | 'inactive'; label: string }> = {
  critical: { variant: 'failed', label: 'Critical' },
  high: { variant: 'placeholder', label: 'High' },
  medium: { variant: 'running', label: 'Medium' },
  low: { variant: 'inactive', label: 'Low' },
};

export function AttackEngine() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAttacks = attackLibrary.filter((attack) => {
    const matchesCategory = activeCategory === 'all' || attack.category === activeCategory;
    const matchesSearch =
      searchQuery === '' ||
      attack.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      attack.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const historyColumns = [
    { key: 'timestamp', header: 'Time', width: '160px' },
    { key: 'attackName', header: 'Attack' },
    {
      key: 'severity',
      header: 'Severity',
      width: '120px',
      render: (row: ExecutionHistoryRow) => {
        const sev = severityMap[row.severity];
        return <StatusBadge variant={sev.variant} label={sev.label} />;
      },
    },
    {
      key: 'status',
      header: 'Status',
      width: '120px',
      render: (row: ExecutionHistoryRow) => (
        <StatusBadge variant={row.status} label={row.status} />
      ),
    },
    { key: 'result', header: 'Result' },
  ];

  return (
    <div className="attack-engine">
      <PageHeader
        title="Attack Engine"
        subtitle="Adversarial attack library and execution interface"
      />

      {/* Category Filters */}
      <div className="attack-engine__categories" role="tablist" aria-label="Attack categories">
        {attackCategories.map((cat) => (
          <button
            key={cat.id}
            className={`attack-engine__category-btn ${activeCategory === cat.id ? 'attack-engine__category-btn--active' : ''}`}
            onClick={() => setActiveCategory(cat.id)}
            role="tab"
            aria-selected={activeCategory === cat.id}
          >
            {cat.label}
            <span className="attack-engine__category-count">{cat.count}</span>
          </button>
        ))}
      </div>

      {/* Search Bar */}
      <div className="attack-engine__search">
        <Search size={16} className="attack-engine__search-icon" />
        <input
          type="text"
          className="attack-engine__search-input"
          placeholder="Search attacks by name or description..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          aria-label="Search attacks"
        />
      </div>

      {/* Attack Cards Grid */}
      <div className="attack-engine__grid">
        {filteredAttacks.map((attack) => {
          const sev = severityMap[attack.severity];
          return (
            <GlassCard key={attack.id} className="attack-engine__card" hoverable>
              <div className="attack-engine__card-header">
                <div className="attack-engine__card-title-row">
                  <AlertTriangle size={16} className="attack-engine__card-icon" />
                  <h3 className="attack-engine__card-name">{attack.name}</h3>
                </div>
                <StatusBadge variant={sev.variant} label={sev.label} />
              </div>
              <span className="attack-engine__card-category">{attack.category}</span>
              <p className="attack-engine__card-desc">{attack.description}</p>
              <div className="attack-engine__card-footer">
                <PrimaryButton size="sm" disabled>
                  Run Attack
                </PrimaryButton>
              </div>
            </GlassCard>
          );
        })}
      </div>

      {/* Execution History */}
      <SectionCard
        title="Execution History"
        subtitle="Recent attack execution results"
        className="attack-engine__history"
      >
        <DataTable<ExecutionHistoryRow>
          columns={historyColumns}
          data={executionHistory}
          keyExtractor={(row) => row.id}
          emptyTitle="No Executions"
          emptyDescription="No attacks have been executed yet."
        />
      </SectionCard>
    </div>
  );
}
