import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Clock, Activity, AlertCircle } from 'lucide-react';

interface RecentUsageLogsProps {
  logs: Array<{
    id: number;
    provider: string;
    model: string;
    operation: string;
    input_tokens: number;
    output_tokens: number;
    total_cost_usd: number;
    processing_time_ms: number;
    status: string;
    error?: string;
    created_at: string;
  }>;
}

export default function RecentUsageLogsCard({ logs }: RecentUsageLogsProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 6
    }).format(amount);
  };

  const formatTime = (dateString: string) => {
    return new Intl.DateTimeFormat('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(dateString));
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      case 'timeout': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getProviderColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'gemini': return 'bg-blue-100 text-blue-800';
      case 'claude': return 'bg-purple-100 text-purple-800';
      case 'adobe': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (!logs || logs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Usage</CardTitle>
          <CardDescription>Các lần gọi API gần đây</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p className="text-gray-500">Chưa có usage logs nào</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Usage</CardTitle>
        <CardDescription>
          {logs.length} lần gọi API gần đây nhất
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {logs.map((log) => (
            <div key={log.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Badge className={getProviderColor(log.provider)}>
                    {log.provider}
                  </Badge>
                  <Badge variant="outline" className="font-mono text-xs">
                    {log.model}
                  </Badge>
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(log.status)}`} title={log.status} />
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="w-3 h-3" />
                  {formatTime(log.created_at)}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                <div>
                  <p className="text-gray-600 text-xs">Operation</p>
                  <p className="font-medium capitalize">{log.operation.replace('_', ' ')}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-xs">Tokens</p>
                  <p className="font-medium">
                    {log.input_tokens.toLocaleString()} → {log.output_tokens.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-xs">Cost</p>
                  <p className="font-medium">{formatCurrency(log.total_cost_usd)}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-xs">Processing</p>
                  <p className="font-medium">{log.processing_time_ms.toFixed(0)}ms</p>
                </div>
                <div>
                  <p className="text-gray-600 text-xs">Status</p>
                  <div className="flex items-center gap-1">
                    {log.status === 'success' ? (
                      <span className="text-green-600 font-medium capitalize">{log.status}</span>
                    ) : (
                      <div className="flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 text-red-500" />
                        <span className="text-red-600 font-medium capitalize">{log.status}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {log.error && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs">
                  <strong className="text-red-700">Error:</strong>
                  <span className="text-red-600 ml-1">{log.error}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}