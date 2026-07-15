import { useLocation } from 'react-router-dom';
import { Bell, Search, Menu } from 'lucide-react';
import './TopNav.css';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/attacks': 'Attack Engine',
  '/detection': 'Detection',
  '/evidence': 'Evidence',
  '/forensics': 'Forensics',
  '/analytics': 'Analytics',
  '/settings': 'Settings',
};

interface TopNavProps {
  onMobileMenuToggle: () => void;
}

export function TopNav({ onMobileMenuToggle }: TopNavProps) {
  const location = useLocation();
  const currentPage = pageTitles[location.pathname] || 'Dashboard';

  return (
    <header className="topnav" role="banner">
      <div className="topnav__left">
        <button
          className="topnav__menu-btn"
          onClick={onMobileMenuToggle}
          aria-label="Toggle menu"
        >
          <Menu size={20} />
        </button>
        <div className="topnav__breadcrumb">
          <span className="topnav__breadcrumb-root">AEGIS</span>
          <span className="topnav__breadcrumb-sep">/</span>
          <span className="topnav__breadcrumb-page">{currentPage}</span>
        </div>
      </div>

      <div className="topnav__right">
        <div className="topnav__search">
          <Search size={16} className="topnav__search-icon" />
          <input
            type="text"
            className="topnav__search-input"
            placeholder="Search..."
            aria-label="Search"
          />
        </div>
        <button className="topnav__icon-btn" aria-label="Notifications">
          <Bell size={18} />
          <span className="topnav__notification-dot" />
        </button>
        <div className="topnav__avatar" aria-label="User profile">
          <span>IR</span>
        </div>
      </div>
    </header>
  );
}
