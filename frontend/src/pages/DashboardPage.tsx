import { useQuery } from '@tanstack/react-query';
import { userService } from '../services';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { StatCardSkeleton } from '../components/ui/skeleton';
import { Users, UserCheck, UserX, Shield } from 'lucide-react';

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => userService.getStats(),
  });

  const statCards = [
    {
      title: 'Tổng người dùng',
      value: stats?.total_users || 0,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Đang hoạt động',
      value: stats?.active_users || 0,
      icon: UserCheck,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Không hoạt động',
      value: stats?.inactive_users || 0,
      icon: UserX,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
    {
      title: 'Quản trị viên',
      value: stats?.superusers || 0,
      icon: Shield,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Tổng quan</h1>
          <p className="text-muted-foreground mt-2">Chào mừng đến bảng điều khiển quản trị</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Tổng quan</h1>
        <p className="text-sm md:text-base text-muted-foreground mt-2">Chào mừng đến bảng điều khiển quản trị</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-full ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Thao tác nhanh</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/users"
              className="p-4 border rounded-lg hover:bg-accent transition-colors"
            >
              <Users className="h-8 w-8 text-primary mb-2" />
              <h3 className="font-semibold">Quản lý người dùng</h3>
              <p className="text-sm text-muted-foreground">
                Xem và quản lý tất cả người dùng
              </p>
            </a>
            <a
              href="/roles"
              className="p-4 border rounded-lg hover:bg-accent transition-colors"
            >
              <Shield className="h-8 w-8 text-primary mb-2" />
              <h3 className="font-semibold">Quản lý vai trò</h3>
              <p className="text-sm text-muted-foreground">
                Cấu hình vai trò và quyền hạn
              </p>
            </a>
            <div className="p-4 border rounded-lg bg-muted/50">
              <UserCheck className="h-8 w-8 text-muted-foreground mb-2" />
              <h3 className="font-semibold text-muted-foreground">Thêm tính năng</h3>
              <p className="text-sm text-muted-foreground">
                Sắp ra mắt...
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
