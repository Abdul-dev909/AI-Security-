/* ── Types for AI Security Dashboard ── */

/** Status badge variant options */
export type StatusVariant =
  | 'online'
  | 'offline'
  | 'running'
  | 'success'
  | 'failed'
  | 'inactive'
  | 'placeholder';

/** Severity levels matching backend Attack model */
export type Severity = 'low' | 'medium' | 'high' | 'critical';

/** Attack category types */
export type AttackCategory =
  | 'jailbreak'
  | 'prompt-injection'
  | 'data-extraction'
  | 'evasion'
  | 'manipulation';

/** Dashboard stat card data */
export interface DashboardStat {
  id: string;
  icon: string;
  title: string;
  value: string | number;
  status: StatusVariant;
  statusLabel: string;
}

/** Recent activity item */
export interface ActivityItem {
  id: string;
  timestamp: string;
  title: string;
  description: string;
  type: 'info' | 'success' | 'warning' | 'danger';
}

/** Attack definition - mirrors backend Attack model */
export interface Attack {
  id: string;
  name: string;
  category: AttackCategory;
  description: string;
  prompt: string;
  severity: Severity;
  enabled: boolean;
}

/** Attack execution result - mirrors backend AttackResult model */
export interface AttackResult {
  attack_id: string;
  attack_name: string;
  prompt: string;
  response: string | null;
  execution_success: boolean;
  error: string | null;
  execution_time: number;
}

/** Execution history row for the attack engine table */
export interface ExecutionHistoryRow {
  id: string;
  timestamp: string;
  attackName: string;
  severity: Severity;
  status: 'success' | 'failed' | 'running';
  result: string;
}

/** Detection metric */
export interface DetectionMetric {
  id: string;
  icon: string;
  label: string;
  value: string | number;
  status: StatusVariant;
}

/** Evidence record */
export interface EvidenceRecord {
  id: string;
  timestamp: string;
  attackName: string;
  evidenceType: string;
  status: StatusVariant;
}

/** Forensic artifact */
export interface ForensicArtifact {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: string;
}

/** Analytics metric card data */
export interface AnalyticsMetric {
  id: string;
  icon: string;
  label: string;
  value: string;
  trend: 'up' | 'down' | 'neutral';
  trendValue: string;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
}

/** Settings section */
export interface SettingsSection {
  id: string;
  title: string;
  description: string;
  items: SettingsItem[];
}

/** Individual settings item */
export interface SettingsItem {
  id: string;
  label: string;
  description: string;
  type: 'toggle' | 'select' | 'input' | 'button';
  value?: string | boolean;
  options?: string[];
  disabled?: boolean;
  danger?: boolean;
}

/** DataTable column definition */
export interface TableColumn<T> {
  key: keyof T & string;
  header: string;
  width?: string;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

/** System overview info row */
export interface SystemInfoRow {
  label: string;
  value: string;
}
