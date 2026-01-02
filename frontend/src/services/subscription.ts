/**
 * Subscription & Billing API Service
 */
import api from './api';

// Types
export interface PlanType {
  FREE: 'free';
  INDIVIDUAL: 'individual';
  ORGANIZATION: 'organization';
  PAY_AS_YOU_GO: 'pay_as_you_go';
}

export interface SubscriptionStatus {
  ACTIVE: 'active';
  CANCELLED: 'cancelled';
  EXPIRED: 'expired';
  TRIAL: 'trial';
  SUSPENDED: 'suspended';
}

export interface PricingPlan {
  id: number;
  plan_type: string;
  name: string;
  description: string | null;
  monthly_price: number;
  annual_price: number | null;
  premium_requests_limit: number | null;  // AI requests limit
  monthly_spending_limit: number | null;  // AI credits
  features: string | null;
  is_active: boolean;
  is_public: boolean;
  trial_days: number;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: number;
  user_id: number | null;
  organization_id: number | null;
  plan_type: string;
  status: string;
  monthly_price: number;
  monthly_limit_usd: number | null;
  premium_requests_used: number;  // Used this period
  premium_requests_limit: number | null;  // From pricing plan
  current_period_start: string | null;
  current_period_end: string | null;
  trial_start: string | null;
  trial_end: string | null;
  cancel_at_period_end: boolean;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UsageSummary {
  period_start: string;
  period_end: string;
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  gemini_cost: number;
  claude_cost: number;
  adobe_cost: number;
  monthly_limit: number | null;
  remaining_budget: number | null;
  usage_percentage: number | null;
}

export interface DailyUsage {
  date: string;
  requests: number;
  tokens: number;
  cost: number;
}

export interface ProviderUsage {
  provider: string;
  requests: number;
  tokens: number;
  cost: number;
  percentage: number;
}

export interface UsageStats {
  summary: UsageSummary;
  daily_usage: DailyUsage[];
  provider_breakdown: ProviderUsage[];
  top_operations: Array<{
    operation: string;
    count: number;
    cost: number;
  }>;
}

export interface BillingRecord {
  id: number;
  subscription_id: number;
  billing_month: string;
  period_start: string;
  period_end: string;
  total_requests: number;
  total_tokens: number;
  gemini_cost: number;
  claude_cost: number;
  adobe_cost: number;
  total_cost: number;
  subscription_fee: number;
  total_amount: number;
  status: string;
  paid_at: string | null;
  invoice_number: string | null;
  invoice_url: string | null;
  created_at: string;
}

export interface BillingListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  records: BillingRecord[];
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  owner_id: number;
  max_members: number;
  is_active: boolean;
  billing_email: string | null;
  created_at: string;
  updated_at: string;
}

// API Service
export const subscriptionService = {
  // Pricing Plans
  getPricingPlans: async (): Promise<PricingPlan[]> => {
    const response = await api.get('/subscription/pricing-plans');
    return response.data;
  },

  getPricingPlan: async (planType: string): Promise<PricingPlan> => {
    const response = await api.get(`/subscription/pricing-plans/${planType}`);
    return response.data;
  },

  // User Subscription
  getMySubscription: async (): Promise<Subscription> => {
    const response = await api.get('/subscription/my-subscription');
    return response.data;
  },

  createSubscription: async (data: {
    plan_type: string;
    organization_id?: number;
    monthly_limit_usd?: number;
  }): Promise<Subscription> => {
    const response = await api.post('/subscription/subscribe', data);
    return response.data;
  },

  updateSubscription: async (data: {
    plan_type?: string;
    monthly_limit_usd?: number;
    cancel_at_period_end?: boolean;
  }): Promise<Subscription> => {
    const response = await api.put('/subscription/my-subscription', data);
    return response.data;
  },

  cancelSubscription: async (): Promise<{ message: string; cancellation_date: string }> => {
    const response = await api.delete('/subscription/my-subscription');
    return response.data;
  },

  // Usage
  getMyUsage: async (): Promise<UsageSummary> => {
    const response = await api.get('/subscription/my-usage');
    return response.data;
  },

  getMyUsageDetailed: async (days: number = 30): Promise<UsageStats> => {
    const response = await api.get(`/subscription/my-usage/detailed?days=${days}`);
    return response.data;
  },

  // Billing
  getMyBilling: async (page: number = 1, pageSize: number = 12): Promise<BillingListResponse> => {
    const response = await api.get(`/subscription/my-billing?page=${page}&page_size=${pageSize}`);
    return response.data;
  },

  getBillingDetail: async (billingId: number): Promise<BillingRecord> => {
    const response = await api.get(`/subscription/my-billing/${billingId}`);
    return response.data;
  },

  // Organizations
  createOrganization: async (data: {
    name: string;
    slug: string;
    description?: string;
    billing_email?: string;
    max_members?: number;
  }): Promise<Organization> => {
    const response = await api.post('/subscription/organizations', data);
    return response.data;
  },

  getMyOrganizations: async (): Promise<Organization[]> => {
    const response = await api.get('/subscription/organizations/my');
    return response.data;
  },

  getOrganization: async (orgId: number): Promise<Organization> => {
    const response = await api.get(`/subscription/organizations/${orgId}`);
    return response.data;
  },
};

export default subscriptionService;
