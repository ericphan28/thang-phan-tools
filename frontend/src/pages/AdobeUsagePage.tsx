/**
 * Adobe PDF Services Usage Tracker
 * Component để hiển thị usage thông tin của Adobe API
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  Activity, 
  BarChart3, 
  AlertCircle, 
  CheckCircle, 
  AlertTriangle,
  RefreshCw,
  ExternalLink,
  TrendingUp
} from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

interface AdobeUsage {
  total_transactions: number;
  transactions_this_month: number;
  monthly_limit: number;
  remaining: number;
  percentage_used: number;
  reset_date: string;
  breakdown_by_operation: Record<string, number>;
  recent_transactions: Array<{
    timestamp: string;
    endpoint: string;
    operation: string;
    duration_ms: number;
    user: string;
  }>;
}

export default function AdobeUsagePage() {
  const [usage, setUsage] = useState<AdobeUsage | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUsage = async () => {
    setLoading(true);
    try {
      const response = await api.get<AdobeUsage>('/api/v1/adobe/usage');
      setUsage(response.data);
    } catch (error: any) {
      console.error('Failed to fetch Adobe usage:', error);
      toast.error('❌ Không thể tải thông tin Adobe usage');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsage();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-600">Đang tải usage data...</p>
        </div>
      </div>
    );
  }

  if (!usage) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Không có dữ liệu Adobe usage</p>
          <Button onClick={fetchUsage} className="mt-4">
            <RefreshCw className="h-4 w-4 mr-2" />
            Thử lại
          </Button>
        </div>
      </div>
    );
  }

  const getStatusColor = () => {
    if (usage.percentage_used >= 100) return 'bg-red-500';
    if (usage.percentage_used >= 90) return 'bg-orange-500';
    if (usage.percentage_used >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusIcon = () => {
    if (usage.percentage_used >= 100) return <AlertCircle className="h-5 w-5 text-red-500" />;
    if (usage.percentage_used >= 90) return <AlertTriangle className="h-5 w-5 text-orange-500" />;
    return <CheckCircle className="h-5 w-5 text-green-500" />;
  };

  const getStatusText = () => {
    if (usage.percentage_used >= 100) return 'Hết quota';
    if (usage.percentage_used >= 90) return 'Sắp hết quota';
    if (usage.percentage_used >= 70) return 'Cảnh báo';
    return 'Bình thường';
  };

  const resetDate = new Date(usage.reset_date);
  const daysUntilReset = Math.ceil((resetDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-3">
            📊 Adobe PDF Services Usage
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Theo dõi usage của Adobe API (Free Tier: 500 transactions/tháng)
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Đã dùng tháng này</p>
                  <p className="text-2xl font-bold text-blue-600">{usage.transactions_this_month}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Còn lại</p>
                  <p className="text-2xl font-bold text-green-600">{usage.remaining}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Tổng cộng (all time)</p>
                  <p className="text-2xl font-bold text-purple-600">{usage.total_transactions}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-purple-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Reset sau</p>
                  <p className="text-2xl font-bold text-orange-600">{daysUntilReset} ngày</p>
                </div>
                {getStatusIcon()}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Progress Bar */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {getStatusIcon()}
                Quota Status: <Badge variant={usage.percentage_used >= 90 ? 'destructive' : 'default'}>
                  {getStatusText()}
                </Badge>
              </CardTitle>
              <Button variant="outline" size="sm" onClick={fetchUsage}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Làm mới
              </Button>
            </div>
            <CardDescription>
              {usage.transactions_this_month} / {usage.monthly_limit} transactions ({usage.percentage_used.toFixed(1)}%)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative w-full h-8 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getStatusColor()} transition-all duration-500 flex items-center justify-center text-white text-sm font-bold`}
                style={{ width: `${Math.min(usage.percentage_used, 100)}%` }}
              >
                {usage.percentage_used >= 10 && `${usage.percentage_used.toFixed(1)}%`}
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
              <span>Reset: {resetDate.toLocaleDateString('vi-VN')}</span>
              <a 
                href="https://developer.adobe.com/console" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-blue-600 hover:underline"
              >
                Xem trên Adobe Console
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Breakdown by Operation */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>📊 Phân tích theo tính năng</CardTitle>
            <CardDescription>Usage tháng này theo từng operation</CardDescription>
          </CardHeader>
          <CardContent>
            {Object.keys(usage.breakdown_by_operation).length === 0 ? (
              <p className="text-gray-500 text-center py-8">Chưa có transactions nào tháng này</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(usage.breakdown_by_operation)
                  .sort(([, a], [, b]) => b - a)
                  .map(([operation, count]) => (
                    <div key={operation} className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <Badge variant="outline">{operation}</Badge>
                        <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500"
                            style={{ 
                              width: `${(count / usage.transactions_this_month) * 100}%` 
                            }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-bold text-gray-700 dark:text-gray-300 ml-4">
                        {count} ({((count / usage.transactions_this_month) * 100).toFixed(1)}%)
                      </span>
                    </div>
                  ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>🕒 Transactions gần đây</CardTitle>
            <CardDescription>10 lần sử dụng Adobe API gần nhất</CardDescription>
          </CardHeader>
          <CardContent>
            {usage.recent_transactions.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Chưa có transactions nào</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b dark:border-gray-700">
                    <tr className="text-left">
                      <th className="pb-2 font-semibold">Thời gian</th>
                      <th className="pb-2 font-semibold">Operation</th>
                      <th className="pb-2 font-semibold">Endpoint</th>
                      <th className="pb-2 font-semibold text-right">Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usage.recent_transactions.map((tx, idx) => (
                      <tr key={idx} className="border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="py-2">
                          {new Date(tx.timestamp).toLocaleString('vi-VN')}
                        </td>
                        <td className="py-2">
                          <Badge variant="secondary">{tx.operation}</Badge>
                        </td>
                        <td className="py-2 text-gray-600 dark:text-gray-400 text-xs">
                          {tx.endpoint}
                        </td>
                        <td className="py-2 text-right text-gray-600">
                          {tx.duration_ms.toFixed(0)}ms
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Warning Banner */}
        {usage.percentage_used >= 90 && (
          <Card className="mt-8 border-orange-500 bg-orange-50 dark:bg-orange-900/20">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <AlertTriangle className="h-6 w-6 text-orange-500 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-orange-800 dark:text-orange-200 mb-2">
                    ⚠️ Sắp hết quota Adobe API
                  </h3>
                  <p className="text-orange-700 dark:text-orange-300 text-sm mb-3">
                    Bạn đã dùng {usage.percentage_used.toFixed(1)}% quota tháng này ({usage.transactions_this_month}/{usage.monthly_limit} transactions).
                    Còn {daysUntilReset} ngày nữa sẽ reset.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => window.open('https://developer.adobe.com/console', '_blank')}
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Nâng cấp plan
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => toast.info('💡 Hệ thống sẽ tự động fallback sang PyPDF2 khi hết quota Adobe')}
                    >
                      Xem fallback options
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
