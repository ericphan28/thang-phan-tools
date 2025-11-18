import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { activityLogService } from '../services';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Activity,
  UserPlus,
  UserMinus,
  Edit3,
  Shield,
  LogIn,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import type { ActivityLog } from '../types';

// Action icon mapping
const getActionIcon = (action: string) => {
  switch (action) {
    case 'create':
      return <UserPlus className="h-4 w-4 text-green-600" />;
    case 'update':
      return <Edit3 className="h-4 w-4 text-blue-600" />;
    case 'delete':
      return <UserMinus className="h-4 w-4 text-red-600" />;
    case 'login':
      return <LogIn className="h-4 w-4 text-purple-600" />;
    default:
      return <Activity className="h-4 w-4 text-gray-600" />;
  }
};

// Resource icon mapping
const getResourceIcon = (resourceType: string) => {
  switch (resourceType) {
    case 'user':
      return <UserPlus className="h-5 w-5" />;
    case 'role':
      return <Shield className="h-5 w-5" />;
    default:
      return <Activity className="h-5 w-5" />;
  }
};

// Action name mapping (Vietnamese)
const getActionName = (action: string): string => {
  const map: Record<string, string> = {
    create: 'Tạo mới',
    update: 'Cập nhật',
    delete: 'Xóa',
    login: 'Đăng nhập',
    logout: 'Đăng xuất',
  };
  return map[action] || action;
};

// Resource name mapping (Vietnamese)
const getResourceName = (resourceType: string): string => {
  const map: Record<string, string> = {
    user: 'người dùng',
    role: 'vai trò',
    permission: 'quyền hạn',
    auth: 'xác thực',
  };
  return map[resourceType] || resourceType;
};

// Format relative time
const formatRelativeTime = (dateString: string): string => {
  // Backend trả UTC, cần thêm 'Z' để JavaScript hiểu đúng múi giờ
  const date = new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return 'Vừa xong';
  if (diffMins < 60) return `${diffMins} phút trước`;
  if (diffHours < 24) return `${diffHours} giờ trước`;
  if (diffDays < 7) return `${diffDays} ngày trước`;
  
  return date.toLocaleDateString('vi-VN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export default function ActivityLogsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    action: '',
    resource_type: '',
  });

  const { data: logsData, isLoading } = useQuery({
    queryKey: ['activity-logs', page, search, filters],
    queryFn: () =>
      activityLogService.getLogs({
        page,
        page_size: 20,
        search: search || undefined,
        action: filters.action || undefined,
        resource_type: filters.resource_type || undefined,
      }),
  });

  const { data: stats } = useQuery({
    queryKey: ['activity-stats'],
    queryFn: () => activityLogService.getStats(7),
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Nhật ký hoạt động</h1>
        <p className="text-muted-foreground mt-2">
          Theo dõi tất cả hoạt động trong hệ thống
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Tổng hoạt động
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_activities}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.days_analyzed} ngày qua
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Tạo mới
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.by_action.create || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Cập nhật
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {stats.by_action.update || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Xóa
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {stats.by_action.delete || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Tìm kiếm trong nhật ký..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            {/* Action Filter */}
            <select
              value={filters.action}
              onChange={(e) => setFilters({ ...filters, action: e.target.value })}
              className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Tất cả hành động</option>
              <option value="create">Tạo mới</option>
              <option value="update">Cập nhật</option>
              <option value="delete">Xóa</option>
              <option value="login">Đăng nhập</option>
            </select>

            {/* Resource Filter */}
            <select
              value={filters.resource_type}
              onChange={(e) =>
                setFilters({ ...filters, resource_type: e.target.value })
              }
              className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Tất cả loại</option>
              <option value="user">Người dùng</option>
              <option value="role">Vai trò</option>
              <option value="auth">Xác thực</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Activity Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Nhật ký hoạt động</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse flex gap-4">
                  <div className="w-10 h-10 bg-gray-200 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : logsData && logsData.logs.length > 0 ? (
            <div className="space-y-4">
              {logsData.logs.map((log) => (
                <div
                  key={log.id}
                  className="flex gap-4 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {/* Icon */}
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                      {getActionIcon(log.action)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="font-medium">
                          {log.username} {getActionName(log.action)}{' '}
                          {getResourceName(log.resource_type)}
                        </p>
                        {log.details && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {JSON.parse(log.details).username ||
                              JSON.parse(log.details).role_name ||
                              ''}
                          </p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                          <span>{formatRelativeTime(log.created_at)}</span>
                          {log.ip_address && <span>IP: {log.ip_address}</span>}
                        </div>
                      </div>
                      <div className="flex-shrink-0">
                        {getResourceIcon(log.resource_type)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Pagination */}
              <div className="flex items-center justify-between pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Trang {logsData.page} / {logsData.total_pages} (Tổng{' '}
                  {logsData.total} hoạt động)
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Trước
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page >= logsData.total_pages}
                  >
                    Sau
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Không có hoạt động nào</h3>
              <p className="text-muted-foreground">
                Chưa có hoạt động nào được ghi nhận.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
