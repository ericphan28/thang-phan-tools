import { useState, useEffect } from 'react';
import api from '../services/api';

interface QuotaInfo {
  subscription_tier: string;
  quota_monthly: number;
  usage_this_month: number;
  remaining: number;
  percentage_used: number;
  reset_date: string;
  is_warning_level: boolean;
}

/**
 * Custom hook để fetch quota info của user hiện tại
 * 
 * Usage:
 * const { quota, loading, error, refetch } = useQuota();
 */
export function useQuota() {
  const [quota, setQuota] = useState<QuotaInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQuota = async () => {
    try {
      setLoading(true);
      const response = await api.get('/subscription/quota');
      setQuota(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch quota:', err);
      setError(err.response?.data?.detail || 'Không thể tải quota');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuota();
  }, []);

  return {
    quota,
    loading,
    error,
    refetch: fetchQuota
  };
}
