import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { subscriptionService } from '../../services/subscription';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { CreditCard, TrendingUp, Zap, ArrowRight, User, LogOut } from 'lucide-react';
import { formatCurrency, formatNumber } from '../../lib/utils';
import toast from 'react-hot-toast';

export default function UserDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const { data: subscription } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: () => subscriptionService.getMySubscription(),
  });

  const { data: usage } = useQuery({
    queryKey: ['my-usage'],
    queryFn: () => subscriptionService.getMyUsage(),
  });

  const premiumUsed = subscription?.premium_requests_used || 0;
  const premiumLimit = subscription?.premium_requests_limit || 0;
  const premiumPercent = premiumLimit > 0 ? (premiumUsed / premiumLimit) * 100 : 0;

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Đăng xuất thành công');
      navigate('/login');
    } catch (error) {
      toast.error('Đăng xuất thất bại');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">My Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              Xin chào, <strong>{user?.full_name || user?.username}</strong>
            </span>
            <Link to="/user/profile">
              <Button variant="outline" size="sm">
                <User className="h-4 w-4 mr-2" />
                Hồ sơ
              </Button>
            </Link>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Đăng xuất
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Subscription Status */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Gói đăng ký của bạn</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Gói hiện tại
                </CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold capitalize">
                  {subscription?.plan_type || 'Free'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {subscription?.status === 'active' ? '✅ Đang hoạt động' : 
                   subscription?.status === 'trial' ? '🎁 Đang dùng thử' : 
                   '⚠️ Không hoạt động'}
                </p>
                <Link to="/user/subscription">
                  <Button variant="link" className="px-0 mt-2" size="sm">
                    Xem chi tiết <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Lượt AI đã dùng
                </CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(premiumUsed)}/{formatNumber(premiumLimit)}
                </div>
                <div className="w-full bg-secondary rounded-full h-2 mt-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(premiumPercent, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {premiumPercent > 80 ? '⚠️ Gần hết quota' : '✅ Còn nhiều'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Tổng chi tiêu
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(usage?.total_cost || 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Tháng này
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Công cụ thường dùng</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* KIỂM TRA THỂ THỨC - NEW FEATURE */}
            <Link to="/user/kiem-tra-the-thuc">
              <Card className="hover:border-primary transition-colors cursor-pointer border-2 border-green-300 bg-green-50/50">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl mb-2">📋</div>
                    <h3 className="font-semibold text-green-700">Kiểm tra thể thức VB</h3>
                    <p className="text-xs text-green-600 mt-1 font-medium">⚡ Nghị định 30/2020</p>
                    <span className="inline-block mt-2 text-xs bg-green-600 text-white px-2 py-1 rounded-full">
                      MỚI
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>

            {/* DOCUMENT TOOLS - NEW FEATURE */}
            <Link to="/user/document-tools">
              <Card className="hover:border-primary transition-colors cursor-pointer border-2 border-purple-300 bg-purple-50/50">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl mb-2">🛠️</div>
                    <h3 className="font-semibold text-purple-700">Công cụ xử lý file</h3>
                    <p className="text-xs text-purple-600 mt-1 font-medium">✨ Word, PDF, Excel, Ảnh</p>
                  </div>
                </CardContent>
              </Card>
            </Link>

            {/* OCR TO WORD - FEATURE */}
            <Link to="/user/ocr-to-word">
              <Card className="hover:border-primary transition-colors cursor-pointer border-2 border-blue-300 bg-blue-50/50">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl mb-2">🇻🇳</div>
                    <h3 className="font-semibold text-blue-700">Trích xuất văn bản PDF</h3>
                    <p className="text-xs text-blue-600 mt-1 font-medium">⚡ AI OCR 98% chính xác</p>
                  </div>
                </CardContent>
              </Card>
            </Link>
            
            <Link to="/user/tools/word-to-pdf">
              <Card className="hover:border-primary transition-colors cursor-pointer">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl mb-2">📄</div>
                    <h3 className="font-semibold">Word → PDF</h3>
                    <p className="text-xs text-muted-foreground mt-1">Miễn phí không giới hạn</p>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link to="/user/tools/ocr">
              <Card className="hover:border-primary transition-colors cursor-pointer">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl mb-2">🔍</div>
                    <h3 className="font-semibold">Đọc chữ từ ảnh</h3>
                    <p className="text-xs text-muted-foreground mt-1">OCR tiếng Việt</p>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link to="/user/tools/ai-text">
              <Card className="hover:border-primary transition-colors cursor-pointer">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl mb-2">🤖</div>
                    <h3 className="font-semibold">Phân tích AI</h3>
                    <p className="text-xs text-muted-foreground mt-1">Dùng lượt AI</p>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>

        {/* Upgrade CTA */}
        {subscription?.plan_type === 'free' && (
          <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold mb-2">Nâng cấp lên gói Cá nhân</h3>
                  <p className="text-muted-foreground mb-4">
                    300 lượt AI/tháng, tặng 50k credits, chỉ 99,000đ
                  </p>
                </div>
                <Link to="/user/pricing">
                  <Button size="lg">
                    Nâng cấp ngay
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
