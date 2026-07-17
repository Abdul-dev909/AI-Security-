import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Swords,
  Shield,
  FileSearch,
  Microscope,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  MessageSquare,
} from 'lucide-react';
import './Sidebar.css';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/attacks', label: 'Attack Engine', icon: Swords },
  { path: '/detection', label: 'Detection', icon: Shield },
  { path: '/evidence', label: 'Evidence', icon: FileSearch },
  { path: '/forensics', label: 'Forensics', icon: Microscope },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/chat', label: 'AI Chat', icon: MessageSquare },
  { path: '/settings', label: 'Settings', icon: Settings },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const location = useLocation();

  return (
    <aside className={`sidebar ${collapsed ? 'sidebar--collapsed' : ''}`} role="navigation" aria-label="Main navigation">
      {/* Logo */}
      <div className="sidebar__logo">
        <div className="sidebar__logo-icon">
          <ShieldAlert size={24} />
        </div>
        {!collapsed && (
          <div className="sidebar__logo-text">
            <span className="sidebar__logo-title">AEGIS</span>
            <span className="sidebar__logo-subtitle">AI Security</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="sidebar__nav">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`sidebar__link ${isActive ? 'sidebar__link--active' : ''}`}
              title={collapsed ? item.label : undefined}
              aria-label={item.label}
            >
              <item.icon size={20} className="sidebar__link-icon" />
              {!collapsed && <span className="sidebar__link-label">{item.label}</span>}
              {isActive && <div className="sidebar__link-indicator" />}
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <button
        className="sidebar__toggle"
        onClick={onToggle}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  );
}
