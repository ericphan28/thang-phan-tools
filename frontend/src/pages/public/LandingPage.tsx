import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Check, Zap, Shield, TrendingUp } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-accent/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">AI Tools Platform</h1>
          <div className="flex gap-4">
            <Link to="/pricing">
              <Button variant="ghost">Bảng giá</Button>
            </Link>
            <Link to="/login">
              <Button>Đăng nhập</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold mb-6">
          🇻🇳 Công cụ hỗ trợ Cán bộ Nhà nước
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
          Trích xuất văn bản từ PDF, soạn thảo công văn chuẩn, phân tích số liệu.
          <br />
          <strong className="text-primary">Tiết kiệm 97% thời gian</strong> bằng AI tiếng Việt.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link to="/demo/ocr">
            <Button size="lg" className="text-lg px-8">
              🚀 Dùng thử OCR miễn phí
            </Button>
          </Link>
          <Link to="/pricing">
            <Button size="lg" variant="outline" className="text-lg px-8">
              Xem bảng giá
            </Button>
          </Link>
          <Link to="/login">
            <Button size="lg" variant="secondary" className="text-lg px-8">
              Đăng nhập
            </Button>
          </Link>
        </div>
        
        {/* New Feature Highlight */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300 rounded-lg p-6 max-w-3xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-3">
            <span className="text-3xl">✨</span>
            <h3 className="text-2xl font-bold text-blue-900">
              Tính năng mới: OCR Tiếng Việt AI
            </h3>
          </div>
          <p className="text-blue-700 text-base mb-4">
            Trích xuất văn bản từ PDF scan (fax, ảnh chụp) với độ chính xác <strong>98%</strong> dấu tiếng Việt.
            <br />
            Tự động phát hiện loại file, giữ nguyên format, xuất Word chỉ trong <strong>30 giây/trang</strong>.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <div className="text-2xl font-bold text-blue-600">98%</div>
              <div className="text-xs text-gray-600">Độ chính xác</div>
            </div>
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <div className="text-2xl font-bold text-purple-600">&lt;30s</div>
              <div className="text-xs text-gray-600">Tốc độ/trang</div>
            </div>
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <div className="text-2xl font-bold text-green-600">AI</div>
              <div className="text-xs text-gray-600">Gemini Vision</div>
            </div>
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <div className="text-2xl font-bold text-orange-600">Auto</div>
              <div className="text-xs text-gray-600">Phát hiện thông minh</div>
            </div>
          </div>
          <Link to="/demo/ocr">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white font-semibold">
              🎯 Dùng thử ngay không cần đăng ký
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Tính năng nổi bật
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <Zap className="h-12 w-12 text-primary mb-4" />
              <CardTitle>Xử lý file không giới hạn</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Chuyển đổi Word, Excel, PDF miễn phí không giới hạn. 
                Không cần lo về quota hay chi phí ẩn.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Shield className="h-12 w-12 text-primary mb-4" />
              <CardTitle>AI thông minh</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Phân tích văn bản, đọc chữ Việt từ ảnh chuẩn xác, 
                xử lý PDF nâng cao với công nghệ AI hiện đại.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <TrendingUp className="h-12 w-12 text-primary mb-4" />
              <CardTitle>Giá rẻ, minh bạch</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Chỉ từ 99k/tháng. Không ẩn chi phí, không ràng buộc. 
                Dùng thử 7 ngày miễn phí.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-4">
          Bảng giá đơn giản
        </h2>
        <p className="text-center text-muted-foreground mb-12">
          Chọn gói phù hợp với nhu cầu của bạn
        </p>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {/* Free */}
          <Card>
            <CardHeader>
              <CardTitle>Miễn phí</CardTitle>
              <div className="text-3xl font-bold mt-4">0đ</div>
              <p className="text-sm text-muted-foreground">Mãi mãi</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Xử lý file không giới hạn</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">OCR cơ bản</span>
                </div>
              </div>
              <Link to="/pricing">
                <Button variant="outline" className="w-full">Bắt đầu</Button>
              </Link>
            </CardContent>
          </Card>

          {/* Individual */}
          <Card className="border-primary border-2 relative">
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-semibold">
              Phổ biến nhất
            </div>
            <CardHeader>
              <CardTitle>Cá nhân</CardTitle>
              <div className="text-3xl font-bold mt-4">99,000đ</div>
              <p className="text-sm text-muted-foreground">Mỗi tháng</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Mọi tính năng miễn phí</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">300 lượt AI/tháng</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Tặng 50k AI credits</span>
                </div>
              </div>
              <Link to="/pricing">
                <Button className="w-full">Chọn gói này</Button>
              </Link>
            </CardContent>
          </Card>

          {/* Organization */}
          <Card>
            <CardHeader>
              <CardTitle>Doanh nghiệp</CardTitle>
              <div className="text-3xl font-bold mt-4">299,000đ</div>
              <p className="text-sm text-muted-foreground">Mỗi người/tháng</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">1,000 lượt AI/tháng</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Quản lý team</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Hỗ trợ 24/7</span>
                </div>
              </div>
              <Link to="/pricing">
                <Button variant="outline" className="w-full">Liên hệ</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-3xl font-bold mb-6">
          Sẵn sàng bắt đầu?
        </h2>
        <p className="text-xl text-muted-foreground mb-8">
          Dùng thử miễn phí, không cần thẻ thanh toán
        </p>
        <Link to="/pricing">
          <Button size="lg" className="text-lg px-8">
            Đăng ký ngay
          </Button>
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted/50">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2025 AI Tools Platform. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
