import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart3, Loader2, Sparkles, Download, Image } from 'lucide-react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import TechnologyBadge from '@/components/TechnologyBadge';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface DataVisualizationPageProps {}

export default function DataVisualizationPage() {
  const [textInput, setTextInput] = useState('');
  const [documentTitle, setDocumentTitle] = useState('Báo cáo Trực quan hóa Dữ liệu');
  const [language, setLanguage] = useState<'vi' | 'en'>('vi');
  const [loading, setLoading] = useState(false);
  const [techInfo, setTechInfo] = useState<{ model?: string; feature?: string } | null>(null);

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
          <TechnologyBadge technology="matplotlib" size="lg" />
          <TechnologyBadge technology="gemini" size="lg" />
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
            <Button onClick={handleGenerate} disabled={loading} className="flex-1">
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
            <Button onClick={handleLoadExample} variant="outline" disabled={loading}>
              Tải ví dụ
            </Button>
          </div>

          {/* Technology Info */}
          {techInfo && (
            <div className="mt-4 p-4 bg-muted rounded-lg space-y-2">
              <p className="text-sm font-medium">Thông tin công nghệ:</p>
              {techInfo.model && (
                <div className="flex items-center gap-2">
                  <TechnologyBadge technology={techInfo.model} />
                  <span className="text-sm text-muted-foreground">AI Model</span>
                </div>
              )}
              {techInfo.feature && (
                <div className="flex items-center gap-2">
                  <TechnologyBadge technology={techInfo.feature} />
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
