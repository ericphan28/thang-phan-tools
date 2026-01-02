/**
 * Pricing Plans Page
 * Display available subscription plans (GitHub Copilot style)
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { subscriptionService, type PricingPlan } from '../services';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Check, Zap, Users, CreditCard, Sparkles } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

export default function PricingPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  // Query pricing plans
  const { data: plans, isLoading } = useQuery({
    queryKey: ['pricing-plans'],
    queryFn: subscriptionService.getPricingPlans,
  });

  // Query current subscription
  const { data: currentSubscription } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: subscriptionService.getMySubscription,
  });

  // Subscribe mutation
  const subscribeMutation = useMutation({
    mutationFn: (planType: string) =>
      subscriptionService.createSubscription({ plan_type: planType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-subscription'] });
      toast.success('Subscription created successfully!');
      navigate('/subscription');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create subscription');
    },
  });

  // Update subscription mutation
  const updateMutation = useMutation({
    mutationFn: (planType: string) =>
      subscriptionService.updateSubscription({ plan_type: planType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-subscription'] });
      toast.success('Subscription updated successfully!');
      navigate('/subscription');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update subscription');
    },
  });

  const handleSelectPlan = (planType: string) => {
    if (currentSubscription) {
      if (currentSubscription.plan_type === planType) {
        toast('You are already on this plan', { icon: 'ℹ️' });
        return;
      }
      updateMutation.mutate(planType);
    } else {
      subscribeMutation.mutate(planType);
    }
  };

  const getPlanIcon = (planType: string) => {
    switch (planType) {
      case 'free':
        return <Sparkles className="h-6 w-6" />;
      case 'individual':
        return <Zap className="h-6 w-6" />;
      case 'organization':
        return <Users className="h-6 w-6" />;
      case 'pay_as_you_go':
        return <CreditCard className="h-6 w-6" />;
      default:
        return <Zap className="h-6 w-6" />;
    }
  };

  const parseFeatures = (featuresJson: string | null, plan: PricingPlan): string[] => {
    // Parse from backend JSON first
    if (featuresJson) {
      try {
        const parsed = JSON.parse(featuresJson);
        if (parsed.features && Array.isArray(parsed.features)) {
          return parsed.features;
        }
      } catch (e) {
        // Fall through to default
      }
    }
    
    // Fallback default features
    const features = ['✅ Chuyển đổi file không giới hạn'];
    if (plan.premium_requests_limit && plan.premium_requests_limit > 0) {
      features.push(`🤖 ${plan.premium_requests_limit} lượt AI/tháng`);
    }
    return features;
  };

  const isCurrentPlan = (planType: string) => {
    return currentSubscription?.plan_type === planType;
  };

  const getPrice = (plan: PricingPlan) => {
    if (billingCycle === 'annual' && plan.annual_price) {
      return {
        price: plan.annual_price / 12,
        billedAs: `Billed annually at ${formatCurrency(plan.annual_price)}`,
      };
    }
    return {
      price: plan.monthly_price,
      billedAs: plan.monthly_price > 0 ? 'Billed monthly' : '',
    };
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">Chọn gói phù hợp với bạn</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Xử lý file miễn phí không giới hạn • Dùng AI thông minh khi cần
        </p>
        <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
          ✅ Chuyển đổi Word/Excel/PDF luôn miễn phí | 🤖 AI nâng cao theo gói bạn chọn
        </p>

        {/* Billing Cycle Toggle */}
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              billingCycle === 'monthly'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            Thanh toán hàng tháng
          </button>
          <button
            onClick={() => setBillingCycle('annual')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              billingCycle === 'annual'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            Thanh toán hàng năm
            <span className="ml-2 text-xs bg-green-500 text-white px-2 py-0.5 rounded">
              Tiết kiệm 20%
            </span>
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading plans...</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 max-w-7xl mx-auto">
          {plans?.map((plan) => {
            const pricing = getPrice(plan);
            const features = parseFeatures(plan.features, plan);
            const isCurrent = isCurrentPlan(plan.plan_type);
            const isPopular = plan.plan_type === 'individual';

            return (
              <Card
                key={plan.id}
                className={`relative ${
                  isPopular ? 'border-primary border-2 shadow-lg' : ''
                } ${isCurrent ? 'bg-accent' : ''}`}
              >
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full">
                      POPULAR
                    </span>
                  </div>
                )}

                {isCurrent && (
                  <div className="absolute -top-3 right-4">
                    <span className="bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                      CURRENT
                    </span>
                  </div>
                )}

                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 text-primary">
                    {getPlanIcon(plan.plan_type)}
                  </div>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <p className="text-sm text-muted-foreground mt-2">
                    {plan.description}
                  </p>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* Price */}
                  <div className="text-center">
                    <div className="text-4xl font-bold">
                      {formatCurrency(pricing.price)}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {plan.monthly_price === 0 ? 'Miễn phí mãi mãi' : '/tháng'}
                    </div>
                    {pricing.billedAs && (
                      <div className="text-xs text-muted-foreground mt-1">
                        {pricing.billedAs}
                      </div>
                    )}
                  </div>

                  {/* Features */}
                  <div className="space-y-3">
                    {features.map((feature, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Button */}
                  <Button
                    onClick={() => handleSelectPlan(plan.plan_type)}
                    disabled={isCurrent || subscribeMutation.isPending || updateMutation.isPending}
                    className="w-full"
                    variant={isPopular ? 'default' : 'outline'}
                  >
                    {isCurrent
                      ? 'Gói hiện tại'
                      : currentSubscription
                      ? 'Chuyển gói'
                      : plan.trial_days > 0
                      ? `Dùng thử ${plan.trial_days} ngày`
                      : 'Đăng ký ngay'}
                  </Button>

                  {plan.trial_days > 0 && !isCurrent && (
                    <p className="text-xs text-center text-muted-foreground">
                      Dùng thử {plan.trial_days} ngày miễn phí, không cần thẻ thanh toán
                    </p>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
