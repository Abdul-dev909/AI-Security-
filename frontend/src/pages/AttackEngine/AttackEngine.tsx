import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, AlertTriangle } from 'lucide-react';
import { PageHeader } from '../../components/common/PageHeader';
import { GlassCard } from '../../components/common/GlassCard';
import { SectionCard } from '../../components/common/SectionCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { PrimaryButton } from '../../components/common/PrimaryButton';
import { OutlineButton } from '../../components/common/OutlineButton';
import { DataTable } from '../../components/common/DataTable';
import { StatCard } from '../../components/common/StatCard';
import { attackCategories } from '../../mock/mockAttacks';
import { listAttacks, runAttack, runAllAttacks } from '../../services/apiService';
import { addExecution, getAllExecutions } from '../../services/executionStore';
import type { Attack, AttackResult, ExecutionEntry, Severity } from '../../types';
import './AttackEngine.css';

const severityMap: Record<Severity | string, { variant: 'failed' | 'placeholder' | 'running' | 'inactive'; label: string }> = {
  critical: { variant: 'failed', label: 'Critical' },
  high: { variant: 'placeholder', label: 'High' },
  medium: { variant: 'running', label: 'Medium' },
  low: { variant: 'inactive', label: 'Low' },
  none: { variant: 'inactive', label: 'None' },
};

export function AttackEngine() {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  const [attacks, setAttacks] = useState<Attack[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningAttacks, setRunningAttacks] = useState<Set<string>>(new Set());
  const [resultsMap, setResultsMap] = useState<Map<string, AttackResult>>(new Map());
  const [executions, setExecutions] = useState<ExecutionEntry[]>([]);
  
  const [summary, setSummary] = useState({
    total: 0,
    completed: 0,
    failed: 0,
    criticalDetections: 0,
  });

  useEffect(() => {
    let isMounted = true;
    listAttacks().then(data => {
      if (isMounted) {
        setAttacks(data);
        setLoading(false);
      }
    }).catch(err => {
      console.error(err);
      if (isMounted) setLoading(false);
    });
    
    setExecutions(getAllExecutions());
  }, []);

  const updateSummary = (results: AttackResult[]) => {
    setSummary(prev => {
      let completed = prev.completed;
      let failed = prev.failed;
      let criticalDetections = prev.criticalDetections;
      
      results.forEach(r => {
        if (r.execution_success) completed++;
        else failed++;
        if (r.detection_report?.highest_severity === 'critical') criticalDetections++;
      });
      
      return {
        total: prev.total + results.length,
        completed,
        failed,
        criticalDetections,
      };
    });
  };

  const handleRunAttack = async (attack: Attack) => {
    setRunningAttacks(prev => new Set(prev).add(attack.id));
    
    try {
      const result = await runAttack(attack.id);
      setResultsMap(prev => new Map(prev).set(attack.id, result));
      addExecution(attack, result);
      setExecutions(getAllExecutions());
      updateSummary([result]);
    } catch (error) {
      console.error(`Failed to run ${attack.name}:`, error);
    } finally {
      setRunningAttacks(prev => {
        const next = new Set(prev);
        next.delete(attack.id);
        return next;
      });
    }
  };

  const handleRunAll = async () => {
    const enabledAttacks = attacks.filter(a => a.enabled);
    setRunningAttacks(new Set(enabledAttacks.map(a => a.id)));
    
    try {
      const response = await runAllAttacks();
      
      const newResults = new Map(resultsMap);
      response.results.forEach((r: AttackResult) => {
        newResults.set(r.attack_id, r);
        const attackDef = attacks.find(a => a.id === r.attack_id);
        if (attackDef) {
          addExecution(attackDef, r);
        }
      });
      
      setResultsMap(newResults);
      setExecutions(getAllExecutions());
      updateSummary(response.results);
    } catch (error) {
      console.error('Failed to run all:', error);
    } finally {
      setRunningAttacks(new Set());
    }
  };

  const filteredAttacks = attacks.filter((attack) => {
    const matchesCategory = activeCategory === 'all' || attack.category === activeCategory;
    const matchesSearch =
      searchQuery === '' ||
      attack.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      attack.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const historyColumns = [
    { 
      key: 'timestamp', 
      header: 'Time', 
      width: '160px',
      render: (row: ExecutionEntry) => new Date(row.timestamp).toLocaleTimeString()
    },
    { 
      key: 'attackName', 
      header: 'Attack',
      render: (row: ExecutionEntry) => row.attack.name
    },
    {
      key: 'severity',
      header: 'Severity',
      width: '120px',
      render: (row: ExecutionEntry) => {
        const severity = row.result.detection_report?.highest_severity || 'none';
        const sevConfig = severityMap[severity] || severityMap.none;
        return <StatusBadge variant={sevConfig.variant} label={sevConfig.label} />;
      },
    },
    {
      key: 'status',
      header: 'Status',
      width: '120px',
      render: (row: ExecutionEntry) => (
        <StatusBadge 
          variant={row.result.execution_success ? 'success' : 'failed'} 
          label={row.result.execution_success ? 'Success' : 'Failed'} 
        />
      ),
    },
    { 
      key: 'result', 
      header: 'Detections',
      render: (row: ExecutionEntry) => `${row.result.detection_report?.total_detections || 0} hits`
    },
    {
      key: 'action',
      header: 'Action',
      width: '100px',
      render: (row: ExecutionEntry) => (
        <a 
          href="#" 
          onClick={(e) => {
            e.preventDefault();
            navigate(`/detection?exec=${row.id}`);
          }}
          className="text-accent"
        >
          View
        </a>
      )
    }
  ];

  return (
    <div className="attack-engine">
      <div className="attack-engine__header-actions">
        <PageHeader
          title="Attack Engine"
          subtitle="Adversarial attack library and execution interface"
        />
        <PrimaryButton onClick={handleRunAll} disabled={runningAttacks.size > 0 || attacks.length === 0}>
          Run All Enabled
        </PrimaryButton>
      </div>

      <div className="attack-engine__summary">
        <StatCard icon="Swords" title="Total Executions" value={summary.total} status="inactive" statusLabel="Total" />
        <StatCard icon="CheckCircle" title="Completed" value={summary.completed} status="success" statusLabel="Success" />
        <StatCard icon="XCircle" title="Failed" value={summary.failed} status="failed" statusLabel="Error" />
        <StatCard icon="AlertTriangle" title="Critical Detections" value={summary.criticalDetections} status="running" statusLabel="Critical" />
      </div>

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
        {loading && <p className="text-muted">Loading attack library...</p>}
        {!loading && filteredAttacks.map((attack) => {
          const sev = severityMap[attack.severity] || severityMap.none;
          const isRunning = runningAttacks.has(attack.id);
          const result = resultsMap.get(attack.id);
          
          return (
            <GlassCard 
              key={attack.id} 
              className={`attack-engine__card ${isRunning ? 'attack-engine__running-indicator' : ''}`} 
              hoverable
            >
              <div className="attack-engine__card-header">
                <div className="attack-engine__card-title-row">
                  <AlertTriangle size={16} className="attack-engine__card-icon" />
                  <h3 className="attack-engine__card-name">{attack.name}</h3>
                </div>
                <StatusBadge variant={sev.variant} label={sev.label} />
              </div>
              <span className="attack-engine__card-category">{attack.category}</span>
              <p className="attack-engine__card-desc">{attack.description}</p>
              
              {result && (
                <div className="attack-engine__card-result">
                  <StatusBadge 
                    variant={result.execution_success ? 'success' : 'failed'} 
                    label={result.execution_success ? 'Success' : 'Failed'} 
                  />
                  <span className="attack-engine__card-time">{result.execution_time.toFixed(2)}s</span>
                  {result.detection_report && (
                    <>
                      <span className="text-muted">•</span>
                      <StatusBadge 
                        variant={severityMap[result.detection_report.highest_severity || 'none'].variant} 
                        label={severityMap[result.detection_report.highest_severity || 'none'].label + ' Detection'} 
                      />
                    </>
                  )}
                </div>
              )}

              <div className="attack-engine__card-actions">
                {result && result.detection_report && (
                  <OutlineButton 
                    size="sm" 
                    onClick={() => {
                      const exec = executions.find(e => e.attack.id === attack.id && e.result.execution_time === result.execution_time);
                      if (exec) navigate(`/detection?exec=${exec.id}`);
                    }}
                  >
                    View Detection
                  </OutlineButton>
                )}
                <PrimaryButton 
                  size="sm" 
                  disabled={isRunning || !attack.enabled}
                  onClick={() => handleRunAttack(attack)}
                >
                  {isRunning ? 'Running...' : 'Run Attack'}
                </PrimaryButton>
              </div>
            </GlassCard>
          );
        })}
      </div>

      {/* Execution History */}
      <SectionCard
        title="Recent Executions"
        subtitle="Log of previously executed attacks"
        className="attack-engine__executions"
      >
        <DataTable<ExecutionEntry>
          columns={historyColumns}
          data={executions}
          keyExtractor={(row) => row.id}
          emptyTitle="No Executions"
          emptyDescription="No attacks have been executed in this session."
        />
      </SectionCard>
    </div>
  );
}
