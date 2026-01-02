/**
 * User Subscription Dashboard
 * Main page for users to manage their subscription and view usage
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { subscriptionService } from '../services';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  CreditCard, TrendingUp, DollarSign, Activity, 
  AlertCircle, CheckCircle, Clock, Zap 
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { formatCurrency, formatNumber } from '../lib/utils';

export default function UserSubscriptionPage() {
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  // Queries
  const { data: subscription, isLoading: subLoading } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: subscriptionService.getMySubscription,
  });

  const { data: usage, isLoading: usageLoading } = useQuery({
    queryKey: ['my-usage'],
    queryFn: subscriptionService.getMyUsage,
  });

  const { data: detailedUsage, isLoading: detailedLoading } = useQuery({
    queryKey: ['my-usage-detailed', selectedPeriod],
    queryFn: () => subscriptionService.getMyUsageDetailed(selectedPeriod),
  });

  const isLoading = subLoading || usageLoading || detailedLoading;

  // Get plan badge color
  const getPlanBadgeClass = (planType: string) => {
    switch (planType) {
      case 'free':
        return 'bg-gray-100 text-gray-800';
      case 'individual':
        return 'bg-blue-100 text-blue-800';
      case 'organization':
        return 'bg-purple-100 text-purple-800';
      case 'pay_as_you_go':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get status badge
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="flex items-center gap-1 text-green-600"><CheckCircle className="h-4 w-4" /> Active</span>;
      case 'trial':
        return <span className="flex items-center gap-1 text-blue-600"><Clock className="h-4 w-4" /> Trial</span>;
      case 'cancelled':
        return <span className="flex items-center gap-1 text-red-600"><AlertCircle className="h-4 w-4" /> Cancelled</span>;
      default:
        return status;
    }
  };

  // Calculate usage percentage
  const usagePercentage = usage?.usage_percentage || 0;
  const getUsageColor = (percent: number) => {
    if (percent < 50) return 'bg-green-500';
    if (percent < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">My Subscription</h1>
          <p className="text-muted-foreground mt-1">
            Manage your plan and track AI usage
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/pricing">
            <Button variant="outline">
              <Zap className="h-4 w-4 mr-2" />
              Upgrade Plan
            </Button>
          </Link>
          <Link to="/billing">
            <Button variant="outline">
              <CreditCard className="h-4 w-4 mr-2" />
              Billing History
            </Button>
          </Link>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading subscription...</p>
        </div>
      ) : (
        <>
          {/* Subscription Overview */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Current Plan */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Current Plan</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold capitalize">
                  {subscription?.plan_type.replace('_', ' ')}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {getStatusBadge(subscription?.status || '')}
                </p>
                <div className="mt-3">
                  <span className={`inline-block px-2 py-1 text-xs font-medium rounded ${getPlanBadgeClass(subscription?.plan_type || '')}`}>
                    {formatCurrency(subscription?.monthly_price || 0)}/month
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Monthly Budget */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Monthly Budget</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {usage?.monthly_limit ? formatCurrency(usage.monthly_limit) : 'Unlimited'}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Used: {formatCurrency(usage?.total_cost || 0)}
                </p>
                {usage?.monthly_limit && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getUsageColor(usagePercentage)}`}
                        style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {usagePercentage.toFixed(1)}% used
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Total Requests */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(usage?.total_requests || 0)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  This billing period
                </p>
                {subscription?.premium_requests_limit && (
                  <p className="text-xs text-muted-foreground mt-2">
                    Premium limit: {formatNumber(subscription.premium_requests_limit)}/month
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Remaining Budget */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Remaining</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {usage?.remaining_budget !== null && usage?.remaining_budget !== undefined
                    ? formatCurrency(usage.remaining_budget)
                    : 'Unlimited'}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Available this month
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Usage Breakdown */}
          <div className="grid gap-4 md:grid-cols-2">
            {/* Provider Costs */}
            <Card>
              <CardHeader>
                <CardTitle>Cost by Provider</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {detailedUsage?.provider_breakdown.map((provider) => (
                    <div key={provider.provider}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium capitalize">{provider.provider}</span>
                        <span>{formatCurrency(provider.cost)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="h-2 rounded-full bg-blue-500"
                          style={{ width: `${provider.percentage}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>{formatNumber(provider.requests)} requests</span>
                        <span>{provider.percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Top Operations */}
            <Card>
              <CardHeader>
                <CardTitle>Top Operations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {detailedUsage?.top_operations.map((op, idx) => (
                    <div key={idx} className="flex justify-between items-center">
                      <div>
                        <div className="font-medium text-sm">{op.operation}</div>
                        <div className="text-xs text-muted-foreground">{op.count} calls</div>
                      </div>
                      <div className="text-sm font-medium">{formatCurrency(op.cost)}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Daily Usage Chart */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Usage Trend</CardTitle>
                <select
                  value={selectedPeriod}
                  onChange={(e) => setSelectedPeriod(Number(e.target.value))}
                  className="border rounded px-2 py-1 text-sm"
                >
                  <option value={7}>Last 7 days</option>
                  <option value={14}>Last 14 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={90}>Last 90 days</option>
                </select>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {detailedUsage?.daily_usage.slice(-14).map((day) => (
                  <div key={day.date} className="flex items-center gap-2">
                    <div className="w-24 text-sm text-muted-foreground">
                      {new Date(day.date).toLocaleDateString('vi-VN', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </div>
                    <div className="flex-1">
                      <div className="w-full bg-gray-200 rounded-full h-6 flex items-center">
                        <div
                          className="h-6 rounded-full bg-blue-500 flex items-center justify-end px-2"
                          style={{
                            width: `${Math.max(
                              5,
                              (day.cost / Math.max(...(detailedUsage?.daily_usage.map((d) => d.cost) || [1]))) * 100
                            )}%`,
                          }}
                        >
                          <span className="text-xs text-white font-medium">
                            {day.requests}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="w-20 text-sm text-right font-medium">
                      {formatCurrency(day.cost)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Billing Period Info */}
          {subscription && (
            <Card>
              <CardHeader>
                <CardTitle>Billing Period</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <div className="text-sm text-muted-foreground">Period Start</div>
                    <div className="text-lg font-medium">
                      {subscription.current_period_start
                        ? new Date(subscription.current_period_start).toLocaleDateString('vi-VN')
                        : 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Period End</div>
                    <div className="text-lg font-medium">
                      {subscription.current_period_end
                        ? new Date(subscription.current_period_end).toLocaleDateString('vi-VN')
                        : 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Days Remaining</div>
                    <div className="text-lg font-medium">
                      {subscription.current_period_end
                        ? Math.max(
                            0,
                            Math.ceil(
                              (new Date(subscription.current_period_end).getTime() - Date.now()) /
                                (1000 * 60 * 60 * 24)
                            )
                          )
                        : 'N/A'}
                    </div>
                  </div>
                </div>

                {subscription.cancel_at_period_end && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <div className="flex items-center gap-2 text-yellow-800">
                      <AlertCircle className="h-5 w-5" />
                      <div>
                        <div className="font-medium">Subscription Cancelled</div>
                        <div className="text-sm">
                          Your subscription will end on{' '}
                          {new Date(subscription.current_period_end!).toLocaleDateString('vi-VN')}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {subscription.status === 'trial' && subscription.trial_end && (
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                    <div className="flex items-center gap-2 text-blue-800">
                      <Clock className="h-5 w-5" />
                      <div>
                        <div className="font-medium">Trial Period</div>
                        <div className="text-sm">
                          Your trial ends on{' '}
                          {new Date(subscription.trial_end).toLocaleDateString('vi-VN')}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
