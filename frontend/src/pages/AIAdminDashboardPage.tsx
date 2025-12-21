import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { getDashboard, getBalanceStatus, getUsageStats, getRecentUsage, type DashboardData, type BalanceStatus } from '../services/aiAdminService';
import { AlertCircle, TrendingUp, DollarSign, Activity, RefreshCw, Database } from 'lucide-react';
import UsageStatsCard from '../components/ai-admin/UsageStatsCard';
import RecentUsageLogsCard from '../components/ai-admin/RecentUsageLogsCard';

export default function AIAdminDashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [balances, setBalances] = useState<BalanceStatus[]>([]);
  const [usageStats, setUsageStats] = useState<any>(null);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardRes, balanceRes, usageRes, logsRes] = await Promise.all([
        getDashboard(),
        getBalanceStatus(),
        getUsageStats(),
        getRecentUsage(10)
      ]);
      setDashboard(dashboardRes.data);
      setBalances(balanceRes.data.balances || []);
      setUsageStats(usageRes.data);
      setRecentLogs(logsRes.data.logs || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 4,
      maximumFractionDigits: 4 
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={fetchData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">Quản lý API keys và theo dõi usage của Gemini & Claude</p>
        </div>
        <Button onClick={fetchData} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Requests Today</CardTitle>
            <Activity className="w-4 h-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(dashboard?.total_requests_today || 0)}</div>
            <p className="text-xs text-gray-600 mt-1">API calls hôm nay</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Cost Today</CardTitle>
            <DollarSign className="w-4 h-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboard?.total_cost_today || 0)}</div>
            <p className="text-xs text-gray-600 mt-1">Chi phí hôm nay</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Requests This Month</CardTitle>
            <TrendingUp className="w-4 h-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(dashboard?.total_requests_month || 0)}</div>
            <p className="text-xs text-gray-600 mt-1">Tổng requests tháng này</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Cost This Month</CardTitle>
            <DollarSign className="w-4 h-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboard?.total_cost_month || 0)}</div>
            <p className="text-xs text-gray-600 mt-1">Tổng chi phí tháng này</p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Statistics */}
      {usageStats && (
        <UsageStatsCard stats={usageStats} />
      )}

      {/* Recent Usage Logs */}
      <RecentUsageLogsCard logs={recentLogs} />

      {/* Balance Status */}
      <Card>
        <CardHeader>
          <CardTitle>Budget Status</CardTitle>
          <CardDescription>Trạng thái ngân sách cho từng provider</CardDescription>
        </CardHeader>
        <CardContent>
          {balances.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Chưa có API keys nào được cấu hình</p>
            </div>
          ) : (
            <div className="space-y-4">
              {balances.map((balance, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold capitalize">{balance.provider}</span>
                        <Badge className={getStatusColor(balance.status)}>
                          {balance.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{balance.key_name}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">{formatCurrency(balance.current_spend_usd)}</div>
                      <p className="text-xs text-gray-600">Đã sử dụng</p>
                    </div>
                  </div>
                  
                  {balance.monthly_limit_usd && (
                    <div className="mt-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Budget: {formatCurrency(balance.monthly_limit_usd)}</span>
                        <span className="font-medium">{balance.usage_percentage ? balance.usage_percentage.toFixed(1) : '0.0'}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            balance.usage_percentage! >= 90 ? 'bg-red-500' :
                            balance.usage_percentage! >= 70 ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(balance.usage_percentage || 0, 100)}%` }}
                        />
                      </div>
                      {balance.remaining_budget !== undefined && (
                        <p className="text-xs text-gray-600 mt-1">
                          Còn lại: {formatCurrency(balance.remaining_budget)}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Providers Summary */}
      {dashboard?.providers_summary && Object.keys(dashboard.providers_summary).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Provider Usage Summary</CardTitle>
            <CardDescription>Chi tiết sử dụng theo provider</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(dashboard.providers_summary).map(([provider, data]: [string, any]) => (
                <div key={provider} className="border-b pb-4 last:border-0">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold capitalize text-lg">{provider}</h3>
                    <Badge variant="outline">{formatNumber(data.requests || 0)} requests</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Total Tokens</p>
                      <p className="font-semibold">{formatNumber(data.total_tokens || 0)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Input Tokens</p>
                      <p className="font-semibold">{formatNumber(data.input_tokens || 0)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Output Tokens</p>
                      <p className="font-semibold">{formatNumber(data.output_tokens || 0)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Total Cost</p>
                      <p className="font-semibold text-green-600">{formatCurrency(data.total_cost || 0)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Usage */}
      {dashboard?.recent_usage && dashboard.recent_usage.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent API Calls</CardTitle>
            <CardDescription>10 API calls gần nhất</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr className="text-left">
                    <th className="pb-2 font-semibold">Time</th>
                    <th className="pb-2 font-semibold">Provider</th>
                    <th className="pb-2 font-semibold">Model</th>
                    <th className="pb-2 font-semibold">Operation</th>
                    <th className="pb-2 font-semibold text-right">Tokens</th>
                    <th className="pb-2 font-semibold text-right">Cost</th>
                    <th className="pb-2 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard.recent_usage.map((log, idx) => (
                    <tr key={idx} className="border-b last:border-0">
                      <td className="py-2 text-gray-600">
                        {new Date(log.created_at).toLocaleTimeString()}
                      </td>
                      <td className="py-2 capitalize">{log.provider}</td>
                      <td className="py-2 text-xs">{log.model}</td>
                      <td className="py-2">{log.operation}</td>
                      <td className="py-2 text-right">{formatNumber(log.total_tokens)}</td>
                      <td className="py-2 text-right text-green-600">{formatCurrency(log.total_cost)}</td>
                      <td className="py-2">
                        <Badge variant={log.status === 'success' ? 'default' : 'destructive'}>
                          {log.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
