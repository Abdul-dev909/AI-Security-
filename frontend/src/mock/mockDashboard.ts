import type { DashboardStat, ActivityItem, SystemInfoRow } from '../types';

export const dashboardStats: DashboardStat[] = [
  {
    id: 'backend-status',
    icon: 'Server',
    title: 'Backend Status',
    value: 'Connected',
    status: 'online',
    statusLabel: 'Online',
  },
  {
    id: 'ai-model',
    icon: 'Brain',
    title: 'AI Model',
    value: 'Qwen3',
    status: 'online',
    statusLabel: 'Active',
  },
  {
    id: 'memory-status',
    icon: 'Database',
    title: 'Memory Status',
    value: '12 Records',
    status: 'online',
    statusLabel: 'Healthy',
  },
  {
    id: 'available-attacks',
    icon: 'Swords',
    title: 'Available Attacks',
    value: 8,
    status: 'placeholder',
    statusLabel: 'Ready',
  },
  {
    id: 'executed-attacks',
    icon: 'Zap',
    title: 'Executed Attacks',
    value: 0,
    status: 'inactive',
    statusLabel: 'None',
  },
];

export const recentActivity: ActivityItem[] = [
  {
    id: 'act-1',
    timestamp: '2 min ago',
    title: 'System Initialized',
    description: 'AI Security Dashboard started successfully',
    type: 'success',
  },
  {
    id: 'act-2',
    timestamp: '5 min ago',
    title: 'Model Connected',
    description: 'Ollama Qwen3 model loaded and ready',
    type: 'info',
  },
  {
    id: 'act-3',
    timestamp: '8 min ago',
    title: 'Memory Database Online',
    description: 'SQLite memory.db initialized with 12 records',
    type: 'info',
  },
  {
    id: 'act-4',
    timestamp: '12 min ago',
    title: 'Attack Registry Loaded',
    description: '8 attack vectors registered in the engine',
    type: 'warning',
  },
  {
    id: 'act-5',
    timestamp: '15 min ago',
    title: 'Security Scan Pending',
    description: 'No detection scans have been executed yet',
    type: 'danger',
  },
];

export const systemOverview: SystemInfoRow[] = [
  { label: 'Platform', value: 'FastAPI v0.115' },
  { label: 'AI Provider', value: 'Ollama (Local)' },
  { label: 'Model', value: 'qwen3 / qwen3:8b' },
  { label: 'Database', value: 'SQLite — memory.db' },
  { label: 'API Endpoint', value: 'http://127.0.0.1:8000' },
  { label: 'Attack Engine', value: 'Loaded — 8 vectors' },
  { label: 'Detection Engine', value: 'Standby' },
  { label: 'Uptime', value: '00:15:32' },
];

export const quickActions = [
  { id: 'qa-1', label: 'Run All Attacks', icon: 'Play', disabled: true },
  { id: 'qa-2', label: 'Start Detection', icon: 'Shield', disabled: true },
  { id: 'qa-3', label: 'Export Evidence', icon: 'Download', disabled: true },
  { id: 'qa-4', label: 'View Analytics', icon: 'BarChart3', disabled: false },
];
