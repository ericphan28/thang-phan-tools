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
    request_metadata?: Record<string, any>;
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

  const formatModelName = (model: string) => {
    // Shorten long model names for better display
    const modelMap: Record<string, string> = {
      'claude-sonnet-4-20250514': 'Claude Sonnet 4',
      'claude-3-5-sonnet': 'Claude 3.5 Sonnet',
      'gemini-3-pro-preview': 'Gemini 3 Pro',
      'gemini-2.5-flash': 'Gemini 2.5 Flash',
      'gemini-2-5-flash': 'Gemini 2.5 Flash',
      'adobe-pdf-services': 'Adobe PDF'
    };
    return modelMap[model] || model;
  };

  const formatTime = (dateString: string) => {
    // Backend returns UTC time in ISO format WITHOUT 'Z' suffix
    // e.g., "2025-12-25T20:47:36.296509" is actually UTC, not local
    // Need to explicitly parse as UTC by adding 'Z' suffix
    const utcDateString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const date = new Date(utcDateString);
    
    // Now convert to Vietnam timezone (GMT+7) for display
    const formattedDate = new Intl.DateTimeFormat('vi-VN', {
      timeZone: 'Asia/Ho_Chi_Minh',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).format(date);
    
    // Add timezone indicator
    return `${formattedDate} (GMT+7)`;
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
                  <Badge variant="outline" className="font-mono text-xs" title={log.model}>
                    {formatModelName(log.model)}
                  </Badge>
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(log.status)}`} title={log.status} />
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="w-3 h-3" />
                  <span title={log.created_at}>{formatTime(log.created_at)}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                <div>
                  <p className="text-gray-600 text-xs">Operation</p>
                  <p className="font-medium capitalize">{log.operation.replace(/_/g, ' ').replace(/-/g, ' ')}</p>
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
                  <p className="font-medium">
                    {log.processing_time_ms != null ? `${log.processing_time_ms.toFixed(0)}ms` : 'N/A'}
                  </p>
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
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <strong className="text-red-700 text-xs font-semibold">Error:</strong>
                      <p className="text-red-600 text-xs mt-1 break-words">{log.error}</p>
                      
                      {/* Request Metadata for debugging */}
                      {log.request_metadata && Object.keys(log.request_metadata).length > 0 && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-800 font-medium">
                            📋 Request Details
                          </summary>
                          <div className="mt-2 p-2 bg-white rounded border border-red-100 text-xs space-y-1">
                            {Object.entries(log.request_metadata).map(([key, value]) => (
                              <div key={key} className="flex gap-2">
                                <span className="text-gray-500 font-mono">{key}:</span>
                                <span className="text-gray-700 font-mono break-all">{JSON.stringify(value)}</span>
                              </div>
                            ))}
                          </div>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              )}
              
              {/* Show metadata for successful requests too */}
              {!log.error && log.request_metadata && Object.keys(log.request_metadata).length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                    ℹ️ Metadata
                  </summary>
                  <div className="mt-1 p-2 bg-gray-50 rounded border border-gray-200 text-xs space-y-1">
                    {Object.entries(log.request_metadata).map(([key, value]) => (
                      <div key={key} className="flex gap-2">
                        <span className="text-gray-500 font-mono">{key}:</span>
                        <span className="text-gray-700 font-mono break-all text-xs">{JSON.stringify(value)}</span>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}