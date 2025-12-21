import api from './api';

export interface AIProvider {
  name: string;
  description: string;
  models: { name: string; description: string; pricing: { input: number; output: number } }[];
}

export interface AIProviderKey {
  id: number;
  provider: string;
  key_name: string;
  api_key_masked: string;
  is_active: boolean;
  is_primary: boolean;
  monthly_limit?: number;
  rate_limit_rpm?: number;
  created_at: string;
  last_used_at?: string;
  error_count: number;
}

export interface AIUsageLog {
  id: number;
  provider: string;
  model: string;
  operation: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  total_cost: number;
  processing_time_ms: number;
  status: string;
  created_at: string;
}

export interface UsageStats {
  period: string;
  start_date: string;
  end_date: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  total_tokens: number;
  total_cost: number;
  by_provider: Record<string, any>;
}

export interface BalanceStatus {
  provider: string;
  key_name: string;
  monthly_limit_usd?: number;
  current_spend_usd: number;
  remaining_usd?: number;
  usage_percentage?: number | null;
  status: string;
  is_primary: boolean;
  last_used?: string | null;
}

export interface DashboardData {
  total_requests_today: number;
  total_requests_month: number;
  total_cost_today: number;
  total_cost_month: number;
  active_providers: number;
  providers_summary: Record<string, any>;
  recent_usage: AIUsageLog[];
}

// API Keys Management
export const getProviders = () => api.get<AIProvider[]>('/ai-admin/providers');

export const getAPIKeys = (provider?: string, activeOnly: boolean = true) => 
  api.get<AIProviderKey[]>('/ai-admin/keys', { params: { provider, active_only: activeOnly } });

export const createAPIKey = (data: {
  provider: string;
  key_name: string;
  api_key: string;
  org_id?: string;
  client_id?: string;
  client_secret?: string;
  is_primary?: boolean;
  monthly_limit?: number;
  rate_limit_rpm?: number;
}) => api.post<AIProviderKey>('/ai-admin/keys', data);

export const updateAPIKey = (id: number, data: {
  key_name?: string;
  is_active?: boolean;
  is_primary?: boolean;
  monthly_limit?: number;
  rate_limit_rpm?: number;
}) => api.put<AIProviderKey>(`/ai-admin/keys/${id}`, data);

export const deleteAPIKey = (id: number) => 
  api.delete(`/ai-admin/keys/${id}`);

export const testAPIKey = (id: number) => 
  api.post(`/ai-admin/keys/${id}/test`);

// Usage Statistics
export const getUsageStats = (provider?: string, period: string = 'current_month') => 
  api.get<UsageStats>('/ai-admin/usage/stats', { params: { provider, period } });

export const getBalanceStatus = () => 
  api.get<{ balances: BalanceStatus[] }>('/ai-admin/usage/balance');

export const getRecentUsage = (limit: number = 50, provider?: string) => 
  api.get<{ count: number; logs: AIUsageLog[] }>('/ai-admin/usage/recent', { 
    params: { limit, provider } 
  });

export const getDashboard = () => 
  api.get<DashboardData>('/ai-admin/dashboard');
