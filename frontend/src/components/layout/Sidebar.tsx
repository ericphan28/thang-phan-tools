import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, Shield, Activity, LogOut, Wrench, X, FileText, FileEdit } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';

const menuItems = [
  { icon: LayoutDashboard, label: 'Tổng quan', path: '/' },
  { icon: Users, label: 'Người dùng', path: '/users' },
  { icon: Shield, label: 'Vai trò', path: '/roles' },
  { icon: Activity, label: 'Nhật ký', path: '/logs' },
  { icon: Wrench, label: 'Công cụ', path: '/tools' },
  { icon: FileText, label: 'Adobe PDF', path: '/adobe-pdf' },
  { icon: FileEdit, label: 'Mẫu 2C', path: '/mau-2c', badge: '🆕 NEW' },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  const handleLinkClick = () => {
    // Close sidebar on mobile when clicking a link
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  return (
    <div 
      className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 bg-card border-r border-border flex flex-col
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}
    >
      {/* Logo & Close button */}
      <div className="p-6 border-b border-border flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-primary">Quản Trị Hệ Thống</h1>
          <p className="text-sm text-muted-foreground mt-1">Bảng điều khiển</p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onClose}
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link key={item.path} to={item.path} onClick={handleLinkClick}>
              <div
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium">{item.label}</span>
                {item.badge && (
                  <span className="ml-auto text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-semibold">
                    {item.badge}
                  </span>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-border">
        <div className="mb-3 px-4 py-2 bg-accent rounded-lg">
          <div className="text-sm font-medium">{user?.username}</div>
          <div className="text-xs text-muted-foreground">{user?.email}</div>
          <div className="flex gap-1 mt-2">
            {user?.roles.map((role) => (
              <span
                key={role}
                className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded"
              >
                {role}
              </span>
            ))}
          </div>
        </div>
        <Button
          variant="outline"
          className="w-full justify-start gap-2"
          onClick={handleLogout}
        >
          <LogOut className="h-4 w-4" />
          Đăng xuất
        </Button>
      </div>
    </div>
  );
}
