import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { TrendingUp, Clock, DollarSign, CheckCircle } from 'lucide-react';

interface UsageStatsProps {
  stats: {
    period: string;
    summary: {
      total_requests: number;
      total_tokens: number;
      total_cost_usd: number;
      total_cost_vnd: number;
    };
    by_model: Array<{
      model: string;
      total_requests: number;
      total_input_tokens: number;
      total_output_tokens: number;
      total_cost_usd: number;
      avg_response_time_ms: number;
      success_rate: number;
    }>;
  };
}

export default function UsageStatsCard({ stats }: UsageStatsProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <TrendingUp className="w-4 h-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.summary.total_requests)}</div>
            <p className="text-xs text-gray-600">{stats.period}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            <Clock className="w-4 h-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.summary.total_tokens)}</div>
            <p className="text-xs text-gray-600">Input + Output tokens</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Cost (USD)</CardTitle>
            <DollarSign className="w-4 h-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.summary.total_cost_usd)}</div>
            <p className="text-xs text-gray-600">{formatNumber(stats.summary.total_cost_vnd)} VND</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="w-4 h-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.by_model.length > 0 ? `${stats.by_model[0].success_rate.toFixed(1)}%` : 'N/A'}
            </div>
            <p className="text-xs text-gray-600">API calls success</p>
          </CardContent>
        </Card>
      </div>

      {/* Models Breakdown */}
      {stats.by_model.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Usage by Model</CardTitle>
            <CardDescription>Chi tiết usage theo từng AI model</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.by_model.map((model, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono">
                        {model.model}
                      </Badge>
                      <Badge variant={model.success_rate >= 99 ? "default" : "secondary"}>
                        {model.success_rate.toFixed(1)}% success
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold">{formatCurrency(model.total_cost_usd)}</div>
                      <p className="text-xs text-gray-600">Total cost</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Requests</p>
                      <p className="font-semibold">{formatNumber(model.total_requests)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Input Tokens</p>
                      <p className="font-semibold">{formatNumber(model.total_input_tokens)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Output Tokens</p>
                      <p className="font-semibold">{formatNumber(model.total_output_tokens)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Avg Response</p>
                      <p className="font-semibold">{model.avg_response_time_ms.toFixed(0)}ms</p>
                    </div>
                  </div>

                  {/* Token Usage Bar */}
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Input vs Output Tokens</span>
                      <span>{formatNumber(model.total_input_tokens + model.total_output_tokens)} total</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 flex">
                      <div 
                        className="bg-blue-500 rounded-l-full h-2" 
                        style={{ 
                          width: `${(model.total_input_tokens / (model.total_input_tokens + model.total_output_tokens)) * 100}%` 
                        }}
                      />
                      <div 
                        className="bg-green-500 rounded-r-full h-2" 
                        style={{ 
                          width: `${(model.total_output_tokens / (model.total_input_tokens + model.total_output_tokens)) * 100}%` 
                        }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>🔵 Input ({((model.total_input_tokens / (model.total_input_tokens + model.total_output_tokens)) * 100).toFixed(1)}%)</span>
                      <span>🟢 Output ({((model.total_output_tokens / (model.total_input_tokens + model.total_output_tokens)) * 100).toFixed(1)}%)</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}