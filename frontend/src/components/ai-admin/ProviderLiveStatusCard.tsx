import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Activity, TrendingUp, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import api from '../../services/api';

interface ProviderStatus {
  provider: string;
  status: string;
  plan_type?: string;
  message?: string;
  rate_limits?: {
    requests_per_minute: number;
    requests_per_day: number;
    tokens_per_minute: number;
  };
  daily_usage?: {
    requests_today: number;
    remaining_requests: number;
    usage_percentage: number;
    tokens_today: number;
    tokens_per_minute_limit: number;
    resets_in_hours: number;
  };
  pricing_info?: {
    current_plan: string;
    total_estimated_cost_if_paid: number;
    note: string;
  };
  models_breakdown?: Record<string, {
    requests: number;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    estimated_cost: number;
    pricing: {
      input: string;
      output: string;
    };
  }>;
  note?: string;
  credits_remaining?: number;
  credits_used?: number;
  estimated_monthly_quota?: number;
  last_updated: string;
}

interface LiveStatusData {
  success: boolean;
  providers: Record<string, ProviderStatus | null>;
  fetched_at: string;
  note: string;
}

export default function ProviderLiveStatusCard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<LiveStatusData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchLiveStatus = async () => {
    try {
      setLoading(true);
      const response = await api.get<LiveStatusData>('/ai-admin/providers/live-status');
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch live status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveStatus();
    // Refresh every 5 minutes
    const interval = setInterval(fetchLiveStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getProviderColor = (provider: string) => {
    switch (provider) {
      case 'gemini': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'claude': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'adobe': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string | undefined) => {
    if (!status) return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'limited_info': return <Info className="w-4 h-4 text-blue-500" />;
      default: return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
  };

  if (loading && !data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 animate-pulse" />
            Provider Live Status
          </CardTitle>
          <CardDescription>Fetching real-time data from providers...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Activity className="w-12 h-12 mx-auto mb-2 opacity-50 animate-pulse" />
            <p className="text-gray-500">Loading...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Provider Live Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-red-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-2" />
            <p>{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const providers = Object.entries(data.providers);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Provider Live Status
            </CardTitle>
            <CardDescription>
              Real-time limits & balance from provider APIs
            </CardDescription>
          </div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Badge variant="outline" className="text-xs">
                  Updated {new Date(data.fetched_at).toLocaleTimeString('vi-VN')}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                <p>Auto-refreshes every 5 minutes</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {providers.map(([providerName, providerData]) => (
            <div key={providerName} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Badge className={getProviderColor(providerName)}>
                    {providerName}
                  </Badge>
                  {providerData && (
                    <span className="text-xs text-gray-600">
                      {providerData.plan_type || 'Unknown Plan'}
                    </span>
                  )}
                </div>
                {getStatusIcon(providerData?.status)}
              </div>

              {!providerData ? (
                <div className="text-sm text-gray-500 italic">
                  ❌ Unable to fetch data - API key may lack permissions
                </div>
              ) : (
                <div className="space-y-2">
                  {/* Rate Limits */}
                  {providerData.rate_limits && (
                    <div className="grid grid-cols-3 gap-2 text-sm">
                      <div className="bg-gray-50 p-2 rounded">
                        <p className="text-xs text-gray-600">Req/Min</p>
                        <p className="font-semibold">{providerData.rate_limits.requests_per_minute}</p>
                      </div>
                      <div className="bg-gray-50 p-2 rounded">
                        <p className="text-xs text-gray-600">Req/Day</p>
                        <p className="font-semibold">{providerData.rate_limits.requests_per_day.toLocaleString()}</p>
                      </div>
                      <div className="bg-gray-50 p-2 rounded">
                        <p className="text-xs text-gray-600">Tokens/Min</p>
                        <p className="font-semibold">{(providerData.rate_limits.tokens_per_minute / 1000).toFixed(0)}K</p>
                      </div>
                    </div>
                  )}

                  {/* Daily Usage (Gemini Free Tier) */}
                  {providerData.daily_usage && (
                    <>
                      <div className={`p-3 rounded border ${
                        providerData.daily_usage.usage_percentage >= 90 ? 'bg-red-50 border-red-200' :
                        providerData.daily_usage.usage_percentage >= 70 ? 'bg-yellow-50 border-yellow-200' :
                        'bg-green-50 border-green-200'
                      }`}>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">📊 Requests hôm nay</span>
                          <span className={`text-lg font-bold ${
                            providerData.daily_usage.usage_percentage >= 90 ? 'text-red-700' :
                            providerData.daily_usage.usage_percentage >= 70 ? 'text-yellow-700' :
                            'text-green-700'
                          }`}>
                            {providerData.daily_usage.remaining_requests} / {providerData.rate_limits?.requests_per_day}
                          </span>
                        </div>
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs text-gray-600">
                            <span>Đã dùng: {providerData.daily_usage.requests_today} requests</span>
                            <span>{providerData.daily_usage.usage_percentage.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all ${
                                providerData.daily_usage.usage_percentage >= 90 ? 'bg-red-500' :
                                providerData.daily_usage.usage_percentage >= 70 ? 'bg-yellow-500' :
                                'bg-green-500'
                              }`}
                              style={{ width: `${Math.min(providerData.daily_usage.usage_percentage, 100)}%` }}
                            />
                          </div>
                          <div className="text-xs text-gray-600 mt-1">
                            🔄 Reset sau {providerData.daily_usage.resets_in_hours} giờ
                          </div>
                        </div>
                      </div>

                      {/* Token Usage */}
                      <div className="bg-blue-50 p-3 rounded border border-blue-200">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium">🎯 Tokens hôm nay</span>
                          <span className="text-lg font-bold text-blue-700">
                            {(providerData.daily_usage.tokens_today / 1000).toFixed(1)}K
                          </span>
                        </div>
                        <div className="text-xs text-gray-600">
                          Limit: {(providerData.daily_usage.tokens_per_minute_limit / 1000).toFixed(0)}K tokens/min
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          ℹ️ Free tier: Không giới hạn tổng tokens
                        </div>
                      </div>
                    </>
                  )}

                  {/* Pricing Info (for Gemini) */}
                  {providerData.pricing_info && (
                    <div className="bg-purple-50 p-3 rounded border border-purple-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium">💰 Pricing Comparison</span>
                        <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                          {providerData.pricing_info.current_plan}
                        </span>
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Nếu dùng Paid:</span>
                          <span className="font-semibold text-purple-700">
                            ${providerData.pricing_info.total_estimated_cost_if_paid.toFixed(4)}
                          </span>
                        </div>
                        {providerData.pricing_info.note && (
                          <div className="text-gray-600 pt-1 border-t border-purple-200 italic">
                            {providerData.pricing_info.note}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Models Breakdown */}
                  {providerData.models_breakdown && Object.keys(providerData.models_breakdown).length > 0 && (
                    <div className="bg-indigo-50 p-3 rounded border border-indigo-200">
                      <div className="text-sm font-medium mb-2">📊 Models Used Today</div>
                      <div className="space-y-2">
                        {Object.entries(providerData.models_breakdown).map(([modelName, modelData]) => (
                          <div key={modelName} className="bg-white p-2 rounded border border-indigo-100">
                            <div className="flex justify-between items-start mb-1">
                              <span className="text-xs font-semibold text-indigo-700">{modelName}</span>
                              <span className="text-xs font-bold text-indigo-900">
                                ${modelData.estimated_cost.toFixed(4)}
                              </span>
                            </div>
                            <div className="grid grid-cols-2 gap-1 text-xs text-gray-600">
                              <div>Requests: {modelData.requests}</div>
                              <div>Tokens: {(modelData.total_tokens / 1000).toFixed(1)}K</div>
                              <div>Input: {modelData.pricing.input}</div>
                              <div>Output: {modelData.pricing.output}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Note */}
                  {providerData.note && (
                    <div className="text-xs text-gray-600 italic bg-blue-50 p-2 rounded border border-blue-200">
                      ℹ️ {providerData.note}
                    </div>
                  )}

                  {/* Credits */}
                  {providerData.credits_remaining !== undefined && (
                    <div className="bg-blue-50 p-3 rounded border border-blue-200">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Credits Remaining</span>
                        <span className="text-lg font-bold text-blue-700">
                          ${providerData.credits_remaining.toFixed(2)}
                        </span>
                      </div>
                      {providerData.credits_used !== undefined && (
                        <div className="text-xs text-gray-600 mt-1">
                          Used: ${providerData.credits_used.toFixed(2)}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Monthly Quota */}
                  {providerData.estimated_monthly_quota && (
                    <div className="bg-amber-50 p-3 rounded border border-amber-200">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Monthly Quota</span>
                        <span className="text-lg font-bold text-amber-700">
                          {providerData.estimated_monthly_quota.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Message */}
                  {providerData.message && (
                    <div className="text-xs text-gray-600 italic bg-gray-50 p-2 rounded">
                      ℹ️ {providerData.message}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
