import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';

interface QuotaInfo {
  subscription_tier: string;
  quota_monthly: number;
  usage_this_month: number;
  remaining: number;
  percentage_used: number;
  reset_date: string;
  is_warning_level: boolean;
}

interface QuotaWarningProps {
  quotaInfo: QuotaInfo;
  className?: string;
}

/**
 * QuotaWarning Component - Hiển thị quota AI với progress bar
 * 
 * Features:
 * - Progress bar màu dynamic (xanh/vàng/đỏ theo usage)
 * - Warning message khi >80%
 * - Upgrade button link to /pricing
 * - Responsive mobile-first
 */
export function QuotaWarning({ quotaInfo, className = '' }: QuotaWarningProps) {
  const navigate = useNavigate();
  const { subscription_tier, quota_monthly, usage_this_month, remaining, percentage_used } = quotaInfo;

  // Dynamic styling based on usage percentage
  const getStatusColor = () => {
    if (percentage_used >= 90) return 'red';
    if (percentage_used >= 70) return 'yellow';
    return 'blue';
  };

  const statusColor = getStatusColor();

  const colorClasses = {
    red: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      progress: 'bg-red-500',
      text: 'text-red-600',
      icon: 'text-red-600'
    },
    yellow: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      progress: 'bg-yellow-500',
      text: 'text-yellow-700',
      icon: 'text-yellow-600'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      progress: 'bg-blue-500',
      text: 'text-blue-700',
      icon: 'text-blue-600'
    }
  };

  const colors = colorClasses[statusColor];

  return (
    <div className={`rounded-lg p-4 border ${colors.bg} ${colors.border} ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">
          AI Quota tháng này: <strong>{usage_this_month}/{quota_monthly}</strong>
        </span>
        <span className="text-xs text-gray-500">
          {remaining} lần còn lại
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${colors.progress}`}
          style={{ width: `${Math.min(percentage_used, 100)}%` }}
        />
      </div>

      {/* Subscription tier badge */}
      <div className="mt-2 text-xs text-gray-600">
        Gói hiện tại: <span className="font-semibold">{subscription_tier}</span>
      </div>

      {/* Warning message (>80% usage) */}
      {percentage_used >= 80 && (
        <div className="mt-3 flex items-start gap-2">
          <AlertCircle className={`h-4 w-4 mt-0.5 flex-shrink-0 ${colors.icon}`} />
          <div className="flex-1">
            <p className={`text-sm ${colors.text}`}>
              {percentage_used >= 95 ? (
                <>
                  <strong>Sắp hết quota!</strong> Nâng cấp ngay để tiếp tục sử dụng AI.
                </>
              ) : (
                <>
                  Bạn sắp hết quota! Nâng cấp lên <strong>PRO</strong> để có 100 lần/tháng.
                </>
              )}
            </p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-2 w-full sm:w-auto"
              onClick={() => navigate('/pricing')}
            >
              {subscription_tier === 'FREE' 
                ? 'Xem gói PRO 399k/tháng →' 
                : 'Xem các gói nâng cao →'
              }
            </Button>
          </div>
        </div>
      )}

      {/* Success message (< 50% usage) */}
      {percentage_used < 50 && subscription_tier === 'PRO' && (
        <div className="mt-2 text-xs text-gray-600">
          ✅ Bạn đang dùng tốt quota. Tiếp tục như vậy!
        </div>
      )}
    </div>
  );
}


/**
 * Compact version - Chỉ hiển thị progress bar nhỏ gọn
 * Dùng cho header/navbar
 */
export function QuotaCompact({ quotaInfo }: QuotaWarningProps) {
  const { usage_this_month, quota_monthly, percentage_used } = quotaInfo;

  const getStatusColor = () => {
    if (percentage_used >= 90) return 'bg-red-500';
    if (percentage_used >= 70) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-gray-600 hidden sm:inline">
        AI: {usage_this_month}/{quota_monthly}
      </span>
      <div className="w-16 sm:w-24 bg-gray-200 rounded-full h-1.5">
        <div 
          className={`h-1.5 rounded-full transition-all ${getStatusColor()}`}
          style={{ width: `${Math.min(percentage_used, 100)}%` }}
        />
      </div>
      <span className="text-xs text-gray-500 sm:hidden">
        {Math.round(percentage_used)}%
      </span>
    </div>
  );
}
