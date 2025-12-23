import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart3, Loader2, Sparkles, Download, Image } from 'lucide-react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { TechnologyBadge } from '@/components/TechnologyBadge';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface DataVisualizationPageProps {}

// Sample data for different chart types
const SAMPLE_DATA = {
  bar: {
    title: 'So sánh Doanh thu Chi nhánh',
    text: `Báo cáo doanh thu các chi nhánh năm 2024

Doanh thu theo khu vực:
- Hà Nội: 500 triệu đồng
- TP. Hồ Chí Minh: 850 triệu đồng
- Đà Nẵng: 320 triệu đồng
- Cần Thơ: 180 triệu đồng
- Hải Phòng: 280 triệu đồng

Phân tích:
TP. Hồ Chí Minh dẫn đầu với 850 triệu, chiếm 42% tổng doanh thu. Hà Nội đứng thứ 2 với 500 triệu. Các chi nhánh miền Trung và Tây Nam Bộ còn tiềm năng phát triển.`,
    description: '📊 BAR CHART - So sánh giữa các mục'
  },
  line: {
    title: 'Xu hướng Tăng trưởng Doanh thu',
    text: `Báo cáo doanh thu theo thời gian

Doanh thu 6 tháng đầu năm 2024:
- Tháng 1: 180 triệu đồng
- Tháng 2: 195 triệu đồng
- Tháng 3: 210 triệu đồng
- Tháng 4: 205 triệu đồng
- Tháng 5: 230 triệu đồng
- Tháng 6: 250 triệu đồng

Nhận xét:
Xu hướng tăng trưởng ổn định với tốc độ trung bình 8% mỗi tháng. Tháng 6 đạt đỉnh 250 triệu, tăng 38% so với tháng 1. Chỉ có tháng 4 giảm nhẹ do nghỉ lễ.`,
    description: '📈 LINE CHART - Xu hướng theo thời gian'
  },
  pie: {
    title: 'Cơ cấu Thị phần Smartphone',
    text: `Thị phần smartphone Việt Nam Q4/2024

Phân tích thị trường:
- Samsung: 40%
- Apple: 25%
- Oppo: 20%
- Xiaomi: 15%

Tổng quan:
Samsung dẫn đầu với 40% thị phần, tiếp theo là Apple với 25%. Các thương hiệu Trung Quốc (Oppo, Xiaomi) chiếm 35% thị trường. Xu hướng người dùng Việt Nam ưa chuộng các thiết bị cao cấp và thương hiệu uy tín.`,
    description: '🥧 PIE CHART - Tỷ lệ phần trăm'
  },
  scatter: {
    title: 'Mối quan hệ Chi phí Marketing vs Doanh thu',
    text: `Phân tích hiệu quả marketing

Dữ liệu chi phí quảng cáo và doanh thu (đơn vị: triệu đồng):
- Chi tiêu 15 triệu → Doanh thu đạt 75 triệu
- Chi tiêu 25 triệu → Doanh thu đạt 110 triệu
- Chi tiêu 35 triệu → Doanh thu đạt 165 triệu
- Chi tiêu 45 triệu → Doanh thu đạt 200 triệu
- Chi tiêu 55 triệu → Doanh thu đạt 240 triệu
- Chi tiêu 65 triệu → Doanh thu đạt 270 triệu

Kết luận:
Có tương quan dương mạnh giữa chi phí marketing và doanh thu. ROI trung bình là 4.2x (mỗi 1 đồng chi ra mang về 4.2 đồng doanh thu). Điểm tối ưu nằm ở mức chi tiêu 45-55 triệu.`,
    description: '🔵 SCATTER PLOT - Quan hệ 2 biến số'
  },
  mixed: {
    title: 'Báo cáo Tổng hợp Kinh doanh Q4/2024',
    text: `Báo cáo kinh doanh quý 4 năm 2024

1. Doanh thu theo tháng:
- Tháng 10: 520 triệu đồng
- Tháng 11: 680 triệu đồng
- Tháng 12: 850 triệu đồng

2. Cơ cấu doanh thu theo kênh bán:
- Online: 45%
- Cửa hàng trực tiếp: 35%
- Đại lý phân phối: 20%

3. So sánh với các quý trước:
- Q1 2024: 1,200 triệu
- Q2 2024: 1,450 triệu
- Q3 2024: 1,680 triệu
- Q4 2024: 2,050 triệu

Tổng kết:
Q4 đạt doanh thu kỷ lục 2,050 triệu, tăng 22% so với Q3. Kênh online chiếm tỷ trọng cao nhất và tiếp tục tăng trưởng mạnh. Xu hướng tích cực cho năm 2025.`,
    description: '🎨 MULTIPLE CHARTS - AI tạo nhiều biểu đồ'
  }
};

export default function DataVisualizationPage() {
  const [textInput, setTextInput] = useState('');
  const [documentTitle, setDocumentTitle] = useState('Báo cáo Trực quan hóa Dữ liệu');
  const [language, setLanguage] = useState<'vi' | 'en'>('vi');
  const [loading, setLoading] = useState(false);
  const [techInfo, setTechInfo] = useState<{ model?: string; feature?: string } | null>(null);
  const [selectedSample, setSelectedSample] = useState<string>('');

  const handleGenerate = async () => {
    if (!textInput.trim()) {
      toast.error('Vui lòng nhập dữ liệu để trực quan hóa');
      return;
    }

    setLoading(true);
    setTechInfo(null);

    try {
      const formData = new FormData();
      formData.append('text_input', textInput);
      if (documentTitle) {
        formData.append('document_title', documentTitle);
      }
      formData.append('language', language);

      const response = await axios.post(`${API_BASE}/documents/generate-visualization`, formData, {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      const model = response.headers?.['x-technology-model'];
      const feature = response.headers?.['x-technology-feature'];
      if (model || feature) {
        setTechInfo({ model, feature });
      }

      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${documentTitle || 'visualization'}_${Date.now()}.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('Đã tạo tài liệu với biểu đồ thành công!');
    } catch (error: any) {
      console.error('Visualization error:', error);
      if (error.response?.status === 401) {
        toast.error('Vui lòng đăng nhập để sử dụng tính năng này');
      } else {
        toast.error(error.response?.data?.detail || 'Không thể tạo trực quan hóa');
      }
    } finally {
      setLoading(false);
    }
  };

  const exampleText = `Doanh thu công ty theo quý:
Q1 2024: 150 triệu
Q2 2024: 180 triệu
Q3 2024: 165 triệu
Q4 2024: 200 triệu

Phân tích:
- Q4 có doanh thu cao nhất với 200 triệu
- Tăng trưởng đáng kể từ Q3 lên Q4 (+21%)
- Mức tăng trưởng ổn định qua các quý`;

  const handleLoadExample = () => {
    setTextInput(exampleText);
    setDocumentTitle('Báo cáo Doanh thu Q1-Q4 2024');
  };

  const handleLoadSample = (sampleKey: string) => {
    const sample = SAMPLE_DATA[sampleKey as keyof typeof SAMPLE_DATA];
    if (sample) {
      setTextInput(sample.text);
      setDocumentTitle(sample.title);
      setSelectedSample(sampleKey);
      toast.success(`Đã tải mẫu: ${sample.description}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-primary" />
            Trực quan hóa Dữ liệu AI
          </h1>
          <p className="text-muted-foreground mt-2">
            Tạo biểu đồ và tài liệu trực quan từ dữ liệu văn bản bằng AI
          </p>
        </div>
        <div className="flex items-center gap-2">
          <TechnologyBadge tech="matplotlib" size="lg" />
          <TechnologyBadge tech="gemini" size="lg" />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Nhập Dữ liệu
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Document Title */}
          <div>
            <label className="block text-sm font-medium mb-2">Tiêu đề tài liệu</label>
            <input
              type="text"
              value={documentTitle}
              onChange={(e) => setDocumentTitle(e.target.value)}
              placeholder="VD: Báo cáo Doanh thu Q1-Q4 2024"
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Text Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Dữ liệu (số liệu, bảng, hoặc mô tả dữ liệu)
            </label>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="VD: Doanh thu Q1: 150 triệu, Q2: 180 triệu..."
              className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[200px] font-mono"
            />
          </div>

          {/* Sample Data Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Hoặc chọn dữ liệu mẫu:</label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <button
                onClick={() => handleLoadSample('bar')}
                disabled={loading}
                className={`p-3 border rounded-lg text-left transition-all hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-950 ${selectedSample === 'bar' ? 'border-blue-500 bg-blue-50 dark:bg-blue-950' : 'border-border'}`}
              >
                <div className="font-semibold text-sm mb-1">📊 Biểu đồ cột (Bar)</div>
                <div className="text-xs text-muted-foreground">So sánh doanh thu chi nhánh</div>
              </button>

              <button
                onClick={() => handleLoadSample('line')}
                disabled={loading}
                className={`p-3 border rounded-lg text-left transition-all hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-950 ${selectedSample === 'line' ? 'border-green-500 bg-green-50 dark:bg-green-950' : 'border-border'}`}
              >
                <div className="font-semibold text-sm mb-1">📈 Biểu đồ đường (Line)</div>
                <div className="text-xs text-muted-foreground">Xu hướng tăng trưởng theo tháng</div>
              </button>

              <button
                onClick={() => handleLoadSample('pie')}
                disabled={loading}
                className={`p-3 border rounded-lg text-left transition-all hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-950 ${selectedSample === 'pie' ? 'border-purple-500 bg-purple-50 dark:bg-purple-950' : 'border-border'}`}
              >
                <div className="font-semibold text-sm mb-1">🥧 Biểu đồ tròn (Pie)</div>
                <div className="text-xs text-muted-foreground">Cơ cấu thị phần smartphone</div>
              </button>

              <button
                onClick={() => handleLoadSample('scatter')}
                disabled={loading}
                className={`p-3 border rounded-lg text-left transition-all hover:border-orange-500 hover:bg-orange-50 dark:hover:bg-orange-950 ${selectedSample === 'scatter' ? 'border-orange-500 bg-orange-50 dark:bg-orange-950' : 'border-border'}`}
              >
                <div className="font-semibold text-sm mb-1">🔵 Biểu đồ phân tán (Scatter)</div>
                <div className="text-xs text-muted-foreground">Quan hệ marketing vs doanh thu</div>
              </button>

              <button
                onClick={() => handleLoadSample('mixed')}
                disabled={loading}
                className={`p-3 border rounded-lg text-left transition-all hover:border-pink-500 hover:bg-pink-50 dark:hover:bg-pink-950 ${selectedSample === 'mixed' ? 'border-pink-500 bg-pink-50 dark:bg-pink-950' : 'border-border'}`}
              >
                <div className="font-semibold text-sm mb-1">🎨 Nhiều biểu đồ (Mixed)</div>
                <div className="text-xs text-muted-foreground">AI tự tạo nhiều loại biểu đồ</div>
              </button>

              <button
                onClick={() => {
                  setTextInput('');
                  setDocumentTitle('Báo cáo Trực quan hóa Dữ liệu');
                  setSelectedSample('');
                  toast.info('Đã xóa dữ liệu, bạn có thể nhập mới');
                }}
                disabled={loading}
                className="p-3 border border-dashed border-border rounded-lg text-left transition-all hover:border-gray-400 hover:bg-gray-50 dark:hover:bg-gray-900"
              >
                <div className="font-semibold text-sm mb-1">🗑️ Xóa & nhập mới</div>
                <div className="text-xs text-muted-foreground">Nhập dữ liệu của bạn</div>
              </button>
            </div>
          </div>

          {/* Language Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Ngôn ngữ tài liệu</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  value="vi"
                  checked={language === 'vi'}
                  onChange={() => setLanguage('vi')}
                  className="w-4 h-4"
                />
                <span>Tiếng Việt</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  value="en"
                  checked={language === 'en'}
                  onChange={() => setLanguage('en')}
                  className="w-4 h-4"
                />
                <span>English</span>
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button onClick={handleGenerate} disabled={loading || !textInput.trim()} className="flex-1">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang tạo biểu đồ...
                </>
              ) : (
                <>
                  <Image className="w-4 h-4 mr-2" />
                  Tạo Biểu đồ
                </>
              )}
            </Button>
          </div>

          {/* Info Message */}
          {selectedSample && (
            <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                💡 <strong>Mẫu đã chọn:</strong> {SAMPLE_DATA[selectedSample as keyof typeof SAMPLE_DATA].description}
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                AI sẽ tự động phân tích và tạo biểu đồ phù hợp. Bạn có thể chỉnh sửa dữ liệu trước khi tạo.
              </p>
            </div>
          )}

          {/* Technology Info */}
          {techInfo && (
            <div className="mt-4 p-4 bg-muted rounded-lg space-y-2">
              <p className="text-sm font-medium">Thông tin công nghệ:</p>
              {techInfo.model && (
                <div className="flex items-center gap-2">
                  <TechnologyBadge tech={techInfo.model as any} />
                  <span className="text-sm text-muted-foreground">AI Model</span>
                </div>
              )}
              {techInfo.feature && (
                <div className="flex items-center gap-2">
                  <TechnologyBadge tech={techInfo.feature as any} />
                  <span className="text-sm text-muted-foreground">Feature</span>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <BarChart3 className="w-8 h-8 text-blue-500 mb-2" />
            <h3 className="font-semibold mb-1">Tự động phân tích</h3>
            <p className="text-sm text-muted-foreground">
              AI nhận diện dữ liệu và tạo biểu đồ phù hợp
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <Image className="w-8 h-8 text-green-500 mb-2" />
            <h3 className="font-semibold mb-1">Nhiều loại biểu đồ</h3>
            <p className="text-sm text-muted-foreground">
              Bar chart, line chart, pie chart, scatter plot
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <Download className="w-8 h-8 text-purple-500 mb-2" />
            <h3 className="font-semibold mb-1">Xuất DOCX</h3>
            <p className="text-sm text-muted-foreground">
              Tài liệu Word với biểu đồ chất lượng cao
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
