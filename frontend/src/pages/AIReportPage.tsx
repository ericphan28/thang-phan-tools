import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Loader2, Sparkles } from 'lucide-react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { TechnologyBadge } from '@/components/TechnologyBadge';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface AIReportPageProps {}

export default function AIReportPage() {
  const [textInput, setTextInput] = useState('');
  const [reportTitle, setReportTitle] = useState('');
  const [language, setLanguage] = useState<'vi' | 'en'>('vi');
  const [loading, setLoading] = useState(false);
  const [techInfo, setTechInfo] = useState<{ model?: string; feature?: string } | null>(null);

  const handleGenerate = async () => {
    if (!textInput.trim()) {
      toast.error('Vui lòng nhập nội dung văn bản');
      return;
    }

    setLoading(true);
    setTechInfo(null);

    try {
      const formData = new FormData();
      formData.append('text_input', textInput);
      if (reportTitle) {
        formData.append('report_title', reportTitle);
      }
      formData.append('language', language);

      const response = await axios.post(`${API_BASE}/documents/generate-report`, formData, {
        responseType: 'blob',
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
      link.setAttribute('download', `AI_Report_${Date.now()}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('✅ Báo cáo đã được tạo thành công!');
    } catch (error: any) {
      console.error('Report generation error:', error);
      const errorMsg = error.response?.data?.detail || 'Lỗi khi tạo báo cáo';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const exampleText = `So sánh Microsoft Graph API và REST API truyền thống

Microsoft Graph API là một endpoint thống nhất cung cấp quyền truy cập vào dữ liệu và dịch vụ của Microsoft 365. 

Ưu điểm của Graph API:
- Một endpoint duy nhất cho tất cả dịch vụ
- Hỗ trợ OData query mạnh mẽ
- Tích hợp sẵn authentication với Azure AD
- Tài liệu phong phú và SDK đầy đủ

REST API truyền thống:
- Mỗi dịch vụ có endpoint riêng
- Linh hoạt hơn về implementation
- Dễ customize cho nhu cầu cụ thể
- Không phụ thuộc vào Microsoft ecosystem

Kết luận: Graph API phù hợp cho ứng dụng Microsoft 365, còn REST API truyền thống tốt hơn cho hệ thống đa nền tảng.`;

  return (
    <div className="container mx-auto p-6 max-w-5xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Sparkles className="w-8 h-8 text-purple-600" />
          AI Report Generator
        </h1>
        <p className="text-gray-600 mt-2">
          Nhập văn bản → AI phân tích & tạo báo cáo Word đẹp với bảng, màu sắc, định dạng chuyên nghiệp
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-600" />
            Tạo Báo cáo So sánh
            <TechnologyBadge tech="gemini" />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Info Box */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-sm">
            <p className="text-purple-800 font-medium mb-2">✨ Tính năng:</p>
            <ul className="text-purple-700 space-y-1">
              <li>📊 Bảng so sánh với header màu xanh</li>
              <li>🎨 Heading và tiêu đề có màu sắc</li>
              <li>📝 Sections rõ ràng với bullet points</li>
              <li>✅ Định dạng chuyên nghiệp như trong ví dụ Claude</li>
            </ul>
          </div>

          {/* Title Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Tiêu đề báo cáo (tùy chọn):
            </label>
            <input
              type="text"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              placeholder="VD: So sánh Microsoft Graph API và REST API"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Text Input */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium">
                Nội dung văn bản:
              </label>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setTextInput(exampleText)}
                className="text-xs"
              >
                Dùng ví dụ mẫu
              </Button>
            </div>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Nhập văn bản cần phân tích và tạo báo cáo..."
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">
              {textInput.length} ký tự
            </p>
          </div>

          {/* Language Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Ngôn ngữ:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as 'vi' | 'en')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="vi">Tiếng Việt</option>
                <option value="en">English</option>
              </select>
            </div>

            {/* Generate Button */}
            <div className="flex items-end">
              <Button
                onClick={handleGenerate}
                disabled={loading || !textInput.trim()}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Đang tạo báo cáo...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Tạo Báo cáo Word
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Tech Info */}
          {techInfo && (
            <div className="bg-gray-50 border border-gray-200 rounded p-3 text-sm">
              <p className="text-gray-700 font-medium mb-1">Thông tin công nghệ:</p>
              {techInfo.model && <p className="text-gray-600">• Model: {techInfo.model}</p>}
              {techInfo.feature && <p className="text-gray-600">• Feature: {techInfo.feature}</p>}
            </div>
          )}

          {/* Example Output */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
            <p className="text-blue-800 font-medium mb-2">📄 Ví dụ output:</p>
            <ul className="text-blue-700 space-y-1">
              <li>• Title màu xanh, căn giữa, font lớn</li>
              <li>• Bảng so sánh với header có background xanh, text trắng</li>
              <li>• Sections với heading màu xanh, bullet points rõ ràng</li>
              <li>• Spacing và layout chuyên nghiệp</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
