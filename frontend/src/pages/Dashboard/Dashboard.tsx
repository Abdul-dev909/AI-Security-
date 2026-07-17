import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as LucideIcons from 'lucide-react';
import { PageHeader } from '../../components/common/PageHeader';
import { StatCard } from '../../components/common/StatCard';
import { SectionCard } from '../../components/common/SectionCard';
import { InfoRow } from '../../components/common/InfoRow';
import { OutlineButton } from '../../components/common/OutlineButton';
import { dashboardStats, recentActivity, systemOverview, quickActions } from '../../mock/mockDashboard';
import { checkHealth } from '../../services/apiService';
import type { DashboardStat } from '../../types';
import './Dashboard.css';

export function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStat[]>(dashboardStats);

  useEffect(() => {
    let isMounted = true;
    const verifyHealth = async () => {
      let isOnline = false;
      try {
        const data = await checkHealth();
        if (data && data.status === 'running') {
          isOnline = true;
        }
      } catch (error) {
        isOnline = false;
      } finally {
        if (isMounted) {
          setStats((currentStats) =>
            currentStats.map((stat) => {
              if (stat.id === 'backend-status') {
                return {
                  ...stat,
                  value: isOnline ? 'Connected' : 'Disconnected',
                  status: isOnline ? 'online' : 'offline',
                  statusLabel: isOnline ? 'Online' : 'Offline',
                };
              }
              return stat;
            })
          );
        }
      }
    };

    verifyHealth();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="dashboard">
      <PageHeader
        title="Command Center"
        subtitle="AI Security Operations Dashboard — System Overview"
      />

      {/* Status Cards Grid */}
      <section className="dashboard__stats" aria-label="System status cards">
        {stats.map((stat, i) => (
          <StatCard
            key={stat.id}
            icon={stat.icon}
            title={stat.title}
            value={stat.value}
            status={stat.status}
            statusLabel={stat.statusLabel}
            index={i}
          />
        ))}
      </section>

      {/* Bottom Panels */}
      <div className="dashboard__panels">
        {/* Recent Activity */}
        <SectionCard title="Recent Activity" subtitle="Latest system events">
          <div className="dashboard__activity-list">
            {recentActivity.map((item, i) => (
              <div
                key={item.id}
                className="dashboard__activity-item"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div className={`dashboard__activity-dot dashboard__activity-dot--${item.type}`} />
                <div className="dashboard__activity-content">
                  <div className="dashboard__activity-header">
                    <span className="dashboard__activity-title">{item.title}</span>
                    <span className="dashboard__activity-time">{item.timestamp}</span>
                  </div>
                  <p className="dashboard__activity-desc">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        {/* System Overview */}
        <div className="dashboard__right-panels">
          <SectionCard title="System Overview" subtitle="Infrastructure status">
            {systemOverview.map((row) => (
              <InfoRow key={row.label} label={row.label} value={row.value} />
            ))}
          </SectionCard>

          {/* Quick Actions */}
          <SectionCard title="Quick Actions" subtitle="Common operations">
            <div className="dashboard__quick-actions">
              {quickActions.map((action) => {
                const Icon = (LucideIcons as unknown as Record<string, React.ComponentType<{ size?: number }>>)[action.icon];
                return (
                  <OutlineButton
                    key={action.id}
                    disabled={action.disabled}
                    onClick={action.disabled ? undefined : () => navigate('/analytics')}
                  >
                    {Icon && <Icon size={16} />}
                    {action.label}
                  </OutlineButton>
                );
              })}
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
