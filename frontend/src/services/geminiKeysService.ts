/**
 * Gemini Keys Management API Service
 */
import api from './api';

export interface GeminiAPIKey {
  id: number;
  key_name: string;
  account_email?: string | null;
  api_key_masked: string;
  provider: string;
  status: 'active' | 'inactive' | 'revoked' | 'quota_exceeded';
  priority: number;
  created_at: string;
  last_used_at: string | null;
  notes: string | null;
  monthly_quota_limit: number | null;
  monthly_quota_used: number | null;
  monthly_quota_remaining: number | null;
  monthly_usage_percentage: number | null;
  is_near_limit: boolean | null;
}

export interface GeminiAPIKeyCreate {
  key_name: string;
  account_email?: string;
  api_key: string;
  priority?: number;
  monthly_quota_limit?: number;
  notes?: string;
}

export interface GeminiAPIKeyUpdate {
  key_name?: string;
  status?: 'active' | 'inactive' | 'revoked' | 'quota_exceeded';
  priority?: number;
  notes?: string;
}

export interface Quota {
  id: number;
  key_id: number;
  quota_type: 'monthly' | 'daily' | 'per_minute';
  quota_limit: number;
  quota_used: number;
  quota_remaining: number;
  usage_percentage: number;
  is_near_limit: boolean;
  reset_at: string;
  last_updated: string;
}

export interface UsageLog {
  id: number;
  key_id: number;
  key_name: string | null;
  user_id: number | null;
  username: string | null;
  model: string;
  total_tokens: number;
  cost_usd: number;
  request_type: string | null;
  status: 'success' | 'failed' | 'quota_exceeded' | 'rate_limited' | 'key_error';
  error_message: string | null;
  response_time_ms: number | null;
  created_at: string;
}

export interface RotationLog {
  id: number;
  from_key_id: number | null;
  from_key_name: string | null;
  to_key_id: number | null;
  to_key_name: string | null;
  reason: string;
  rotated_at: string;
  rotated_by: string;
}

export interface KeyHealthOverview {
  total_keys: number;
  active_keys: number;
  inactive_keys: number;
  quota_exceeded_keys: number;
  revoked_keys: number;
  total_quota_remaining: number;
  keys_near_limit: string[];
}

export interface UsageTrend {
  date: string;
  total_requests: number;
  total_tokens: number;
  total_cost_usd: number;
  success_rate: number;
}

export interface ModelUsageStats {
  model: string;
  total_requests: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_response_time_ms: number | null;
}

export interface UserUsageStats {
  user_id: number;
  username: string;
  total_requests: number;
  total_tokens: number;
  total_cost_usd: number;
}

export interface DashboardMetrics {
  overview: KeyHealthOverview;
  usage_trends_7d: UsageTrend[];
  top_models: ModelUsageStats[];
  top_users: UserUsageStats[];
  recent_rotations: RotationLog[];
}

const BASE_PATH = '/admin/gemini-keys';

export const geminiKeysService = {
  // ========== KEYS CRUD ==========
  
  async getAllKeys(includeInactive: boolean = false): Promise<GeminiAPIKey[]> {
    const response = await api.get(`${BASE_PATH}/keys`, {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  },

  async getKey(keyId: number): Promise<GeminiAPIKey> {
    const response = await api.get(`${BASE_PATH}/keys/${keyId}`);
    return response.data;
  },

  async createKey(data: GeminiAPIKeyCreate): Promise<GeminiAPIKey> {
    const response = await api.post(`${BASE_PATH}/keys`, data);
    return response.data;
  },

  async updateKey(keyId: number, data: GeminiAPIKeyUpdate): Promise<GeminiAPIKey> {
    const response = await api.patch(`${BASE_PATH}/keys/${keyId}`, data);
    return response.data;
  },

  async deleteKey(keyId: number): Promise<void> {
    await api.delete(`${BASE_PATH}/keys/${keyId}`);
  },

  async rotateKey(keyId: number, reason: string = 'manual_rotation'): Promise<{
    message: string;
    new_key_id: number;
    new_key_name: string;
    quota_remaining: number;
  }> {
    const response = await api.post(`${BASE_PATH}/keys/${keyId}/rotate`, null, {
      params: { reason }
    });
    return response.data;
  },

  // ========== QUOTAS & USAGE ==========

  async getKeyQuotas(keyId: number): Promise<Quota[]> {
    const response = await api.get(`${BASE_PATH}/keys/${keyId}/quotas`);
    return response.data;
  },

  async getUsageLogs(params?: {
    key_id?: number;
    user_id?: number;
    limit?: number;
  }): Promise<UsageLog[]> {
    const response = await api.get(`${BASE_PATH}/usage-logs`, { params });
    return response.data;
  },

  async getRotationLogs(limit: number = 50): Promise<RotationLog[]> {
    const response = await api.get(`${BASE_PATH}/rotation-logs`, {
      params: { limit }
    });
    return response.data;
  },

  // ========== DASHBOARD ==========

  async getDashboard(): Promise<DashboardMetrics> {
    const response = await api.get(`${BASE_PATH}/dashboard`);
    return response.data;
  },

  // ========== MANUAL ACTIONS ==========

  async resetMonthlyQuotas(): Promise<{ message: string; reset_count: number }> {
    const response = await api.post(`${BASE_PATH}/quotas/reset-monthly`);
    return response.data;
  },
};
