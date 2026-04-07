import { Link, useLocation } from 'react-router-dom';
import { Home, Upload, Database, LayoutDashboard, Brain, Settings, HelpCircle, Sparkles, TrendingUp, Bell, GitCompare, Network, Cable, Mail } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();

  const mainNav = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/upload', label: 'Upload', icon: Upload },
    { path: '/datasets', label: 'Datasets', icon: Database },
    { path: '/dashboards', label: 'Dashboards', icon: LayoutDashboard },
    { path: '/ml', label: 'ML Models', icon: Brain },
    { path: '/forecast', label: 'Forecast', icon: TrendingUp },
    { path: '/alerts', label: 'Alerts', icon: Bell },
    { path: '/dataset-diff', label: 'Compare', icon: GitCompare },
    { path: '/data-mesh', label: 'Data Mesh', icon: Network },
    { path: '/database-agent', label: 'DB Agent', icon: Cable },
    { path: '/briefing', label: 'Briefings', icon: Mail },
  ];

  const bottomNav = [
    { path: '/settings', label: 'Settings', icon: Settings },
    { path: '/support', label: 'Support', icon: HelpCircle },
  ];

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <aside className="flex flex-col h-full bg-surface border-r border-border" style={{ width: 'var(--sidebar-width)' }}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-[#5AC8FA] flex items-center justify-center shadow-glow-sm">
          <span className="text-white font-bold text-sm">⬡</span>
        </div>
        <div className="flex flex-col">
          <span className="font-heading font-semibold text-sm text-text-primary leading-tight">Talking BI</span>
          <span className="tier-badge mt-0.5 w-fit" style={{ fontSize: '9px', padding: '1px 6px' }}>AI ENTERPRISE TIER</span>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-2 space-y-0.5">
        {mainNav.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200
                ${active
                  ? 'bg-primary/15 text-primary border-l-2 border-primary'
                  : 'text-text-secondary hover:text-text-primary hover:bg-white/[0.04]'
                }
              `}
            >
              <Icon size={18} strokeWidth={active ? 2 : 1.5} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* New Analysis Button */}
      <div className="px-3 py-3">
        <Link
          to="/upload"
          className="flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-lg text-[13px] font-semibold
            bg-gradient-to-r from-primary to-[#5AC8FA] text-white
            hover:shadow-glow-sm transition-all duration-300 hover:scale-[1.02]"
        >
          <Sparkles size={16} />
          New Analysis
        </Link>
      </div>

      {/* Bottom Navigation */}
      <div className="px-3 py-3 border-t border-border space-y-0.5">
        {bottomNav.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 w-full rounded-lg text-[13px] transition-colors
                ${active
                  ? 'bg-primary/15 text-primary'
                  : 'text-text-secondary hover:text-text-primary hover:bg-white/[0.04]'
                }`}
            >
              <Icon size={18} strokeWidth={active ? 2 : 1.5} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
