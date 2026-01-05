/**
 * Dashboard Tab - Metrics & Overview
 */
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Skeleton } from '../ui/skeleton';
import { 
  Key, 
  TrendingUp, 
  DollarSign, 
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Zap,
  RotateCw
} from 'lucide-react';
import { geminiKeysService, type DashboardMetrics } from '../../services/geminiKeysService';
import toast from 'react-hot-toast';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function DashboardTab() {
  const { data: metrics, isLoading, error, refetch } = useQuery<DashboardMetrics>({
    queryKey: ['gemini-dashboard'],
    queryFn: () => geminiKeysService.getDashboard(),
    refetchInterval: 30000, // Auto-refresh every 30s
  });

  useEffect(() => {
    if (error) {
      toast.error('Không thể tải dashboard metrics');
    }
  }, [error]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          Không có dữ liệu
        </CardContent>
      </Card>
    );
  }

  const { overview, usage_trends_7d, top_models, top_users, recent_rotations } = metrics;

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Keys</CardTitle>
            <Key className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview.total_keys}</div>
            <div className="flex gap-2 mt-2 text-xs">
              <Badge variant="default" className="bg-green-500">
                {overview.active_keys} active
              </Badge>
              {overview.quota_exceeded_keys > 0 && (
                <Badge variant="destructive">
                  {overview.quota_exceeded_keys} exceeded
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Quota Remaining</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(overview.total_quota_remaining / 1_000_000).toFixed(1)}M
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              tokens across all keys
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">7-Day Requests</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {usage_trends_7d.reduce((sum, day) => sum + day.total_requests, 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {(usage_trends_7d.reduce((sum, day) => sum + day.total_tokens, 0) / 1_000_000).toFixed(2)}M tokens
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">7-Day Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${usage_trends_7d.reduce((sum, day) => sum + day.total_cost_usd, 0).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Average: ${(usage_trends_7d.reduce((sum, day) => sum + day.total_cost_usd, 0) / 7).toFixed(2)}/day
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Alerts */}
      {overview.keys_near_limit.length > 0 && (
        <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-700 dark:text-orange-400">
              <AlertTriangle className="h-5 w-5" />
              Keys Near Limit
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {overview.keys_near_limit.map((keyName) => (
                <Badge key={keyName} variant="outline" className="border-orange-300">
                  {keyName} (&gt;80% used)
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Trends Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Usage Trends (7 Days)</CardTitle>
            <CardDescription>Requests & success rate over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={usage_trends_7d}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' })}
                />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  labelFormatter={(value: any) => new Date(value).toLocaleDateString('vi-VN')}
                  formatter={(value: any, name: any) => {
                    if (name === 'success_rate') return [`${Number(value).toFixed(1)}%`, 'Success Rate'];
                    return [Number(value).toLocaleString(), name === 'total_requests' ? 'Requests' : 'Tokens'];
                  }}
                />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="total_requests" 
                  stroke="#3b82f6" 
                  name="Requests"
                  strokeWidth={2}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="success_rate" 
                  stroke="#10b981" 
                  name="Success Rate (%)"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Models Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top Models (7 Days)</CardTitle>
            <CardDescription>Most used AI models</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={top_models}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="model" 
                  tick={{ fontSize: 10 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value: any, name: string) => {
                    if (name === 'total_cost_usd') return [`$${value.toFixed(2)}`, 'Cost'];
                    return [value.toLocaleString(), name === 'total_requests' ? 'Requests' : 'Tokens'];
                  }}
                />
                <Legend />
                <Bar dataKey="total_requests" fill="#3b82f6" name="Requests" />
                <Bar dataKey="total_cost_usd" fill="#10b981" name="Cost ($)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Users */}
        <Card>
          <CardHeader>
            <CardTitle>Top Users (7 Days)</CardTitle>
            <CardDescription>Highest API usage by user</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {top_users.slice(0, 5).map((user, index) => (
                <div key={user.user_id} className="flex items-center justify-between pb-3 border-b last:border-0">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{user.username}</p>
                      <p className="text-xs text-muted-foreground">
                        {user.total_requests.toLocaleString()} requests
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600">
                      ${user.total_cost_usd.toFixed(2)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {(user.total_tokens / 1000).toFixed(0)}k tokens
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Rotations */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Rotations</CardTitle>
            <CardDescription>Latest key rotation events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recent_rotations.slice(0, 5).map((rotation) => (
                <div key={rotation.id} className="flex items-start gap-3 pb-3 border-b last:border-0">
                  <RotateCw className="h-4 w-4 text-muted-foreground mt-1" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm">
                      <span className="font-medium">{rotation.from_key_name || 'N/A'}</span>
                      {' → '}
                      <span className="font-medium text-green-600">{rotation.to_key_name || 'N/A'}</span>
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {rotation.reason.replace(/_/g, ' ')}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(rotation.rotated_at).toLocaleString('vi-VN')}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
              {recent_rotations.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No rotations yet
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
