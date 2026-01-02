import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Check } from 'lucide-react';
import { subscriptionService } from '../../services/subscription';
import { formatCurrency } from '../../lib/utils';

export default function PublicPricingPage() {
  const { data: plans, isLoading } = useQuery({
    queryKey: ['pricing-plans-public'],
    queryFn: () => subscriptionService.getPricingPlans(),
  });

  const parseFeatures = (featuresJson: string | null): string[] => {
    if (!featuresJson) return [];
    try {
      const parsed = JSON.parse(featuresJson);
      return parsed.features || [];
    } catch {
      return [];
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/">
            <h1 className="text-2xl font-bold text-primary">AI Tools Platform</h1>
          </Link>
          <div className="flex gap-4">
            <Link to="/">
              <Button variant="ghost">Trang chủ</Button>
            </Link>
            <Link to="/login">
              <Button>Đăng nhập</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="text-center space-y-4 mb-12">
          <h1 className="text-4xl font-bold">Chọn gói phù hợp với bạn</h1>
          <p className="text-lg text-muted-foreground">
            Xử lý file miễn phí không giới hạn • Dùng AI thông minh khi cần
          </p>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Đang tải...</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 max-w-7xl mx-auto">
            {plans?.map((plan) => {
              const features = parseFeatures(plan.features);
              const isPopular = plan.plan_type === 'individual';

              return (
                <Card
                  key={plan.id}
                  className={isPopular ? 'border-primary border-2 relative' : ''}
                >
                  {isPopular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground px-3 py-1 rounded-full text-xs font-semibold">
                      Phổ biến nhất
                    </div>
                  )}

                  <CardHeader className="text-center">
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-2">
                      {plan.description}
                    </p>
                  </CardHeader>

                  <CardContent className="space-y-6">
                    {/* Price */}
                    <div className="text-center">
                      <div className="text-4xl font-bold">
                        {plan.monthly_price === 0 ? 'Miễn phí' : formatCurrency(plan.monthly_price)}
                      </div>
                      {plan.monthly_price > 0 && (
                        <div className="text-sm text-muted-foreground mt-1">/tháng</div>
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

                    {/* CTA */}
                    <Link to="/login">
                      <Button
                        className="w-full"
                        variant={isPopular ? 'default' : 'outline'}
                      >
                        {plan.trial_days > 0 ? `Dùng thử ${plan.trial_days} ngày` : 'Đăng ký ngay'}
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* FAQ */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Câu hỏi thường gặp</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">Tôi có cần thẻ thanh toán để dùng thử không?</h3>
              <p className="text-muted-foreground">
                Không! Gói miễn phí không cần thẻ. Gói trả phí có dùng thử 7-14 ngày miễn phí, cũng không cần thẻ.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">"Lượt AI" là gì?</h3>
              <p className="text-muted-foreground">
                Lượt AI là số lần bạn sử dụng các tính năng AI nâng cao như phân tích văn bản, 
                đọc chữ Việt từ ảnh, xử lý PDF phức tạp. Các tính năng cơ bản như chuyển đổi file 
                thì không giới hạn và luôn miễn phí.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Tôi có thể đổi gói sau không?</h3>
              <p className="text-muted-foreground">
                Có! Bạn có thể nâng cấp hoặc hạ cấp gói bất cứ lúc nào. Chúng tôi sẽ tính phí theo tỷ lệ.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t bg-muted/50 mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2025 AI Tools Platform. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
