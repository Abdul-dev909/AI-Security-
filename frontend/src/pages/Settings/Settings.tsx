import { PageHeader } from '../../components/common/PageHeader';
import { SectionCard } from '../../components/common/SectionCard';
import { OutlineButton } from '../../components/common/OutlineButton';
import { AlertTriangle } from 'lucide-react';
import './Settings.css';

interface SettingRowProps {
  label: string;
  description: string;
  children: React.ReactNode;
}

function SettingRow({ label, description, children }: SettingRowProps) {
  return (
    <div className="settings__row">
      <div className="settings__row-text">
        <span className="settings__row-label">{label}</span>
        <span className="settings__row-desc">{description}</span>
      </div>
      <div className="settings__row-control">
        {children}
      </div>
    </div>
  );
}

function TogglePlaceholder({ checked = false }: { checked?: boolean }) {
  return (
    <div className={`settings__toggle ${checked ? 'settings__toggle--active' : ''}`}>
      <div className="settings__toggle-thumb" />
    </div>
  );
}

function SelectPlaceholder({ value }: { value: string }) {
  return (
    <div className="settings__select">
      <span>{value}</span>
    </div>
  );
}

export function Settings() {
  return (
    <div className="settings">
      <PageHeader
        title="Settings"
        subtitle="System configuration and preferences"
      />

      {/* General */}
      <SectionCard title="General" subtitle="Application preferences" className="settings__section">
        <SettingRow label="Theme" description="Interface color scheme">
          <SelectPlaceholder value="Dark Mode" />
        </SettingRow>
        <SettingRow label="Language" description="Display language">
          <SelectPlaceholder value="English" />
        </SettingRow>
        <SettingRow label="Notifications" description="Enable system notifications">
          <TogglePlaceholder checked />
        </SettingRow>
      </SectionCard>

      {/* AI Configuration */}
      <SectionCard title="AI Configuration" subtitle="Model and inference settings" className="settings__section">
        <SettingRow label="AI Model" description="Active language model for analysis">
          <SelectPlaceholder value="Qwen3" />
        </SettingRow>
        <SettingRow label="Fallback Model" description="Backup model when primary is unavailable">
          <SelectPlaceholder value="qwen3:8b" />
        </SettingRow>
        <SettingRow label="Auto-detect Threats" description="Automatically analyze responses for threats">
          <TogglePlaceholder />
        </SettingRow>
      </SectionCard>

      {/* Attack Configuration */}
      <SectionCard title="Attack Configuration" subtitle="Attack engine settings" className="settings__section">
        <SettingRow label="Parallel Execution" description="Run multiple attacks simultaneously">
          <TogglePlaceholder />
        </SettingRow>
        <SettingRow label="Execution Timeout" description="Maximum time per attack execution">
          <SelectPlaceholder value="30 seconds" />
        </SettingRow>
        <SettingRow label="Auto-save Evidence" description="Automatically save attack results as evidence">
          <TogglePlaceholder checked />
        </SettingRow>
      </SectionCard>

      {/* System Preferences */}
      <SectionCard title="System" subtitle="System-level preferences" className="settings__section">
        <SettingRow label="API Endpoint" description="Backend server address">
          <SelectPlaceholder value="http://127.0.0.1:8000" />
        </SettingRow>
        <SettingRow label="Database" description="Memory storage backend">
          <SelectPlaceholder value="SQLite — memory.db" />
        </SettingRow>
        <SettingRow label="Debug Mode" description="Enable verbose logging">
          <TogglePlaceholder />
        </SettingRow>
      </SectionCard>

      {/* Danger Zone */}
      <SectionCard title="Danger Zone" subtitle="Irreversible operations" className="settings__section settings__section--danger">
        <div className="settings__danger-content">
          <div className="settings__danger-info">
            <AlertTriangle size={20} className="settings__danger-icon" />
            <div>
              <p className="settings__danger-title">Reset System</p>
              <p className="settings__danger-desc">
                Clear all data, evidence, forensic artifacts, and reset the system to its initial state. This action cannot be undone.
              </p>
            </div>
          </div>
          <OutlineButton variant="danger" disabled>
            Reset System
          </OutlineButton>
        </div>
      </SectionCard>
    </div>
  );
}
