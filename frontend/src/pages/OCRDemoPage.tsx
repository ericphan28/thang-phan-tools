import { useState, useCallback } from 'react';
import { Upload, Loader2, Search, CheckCircle2, XCircle, Clock, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { QuotaWarning } from '../components/QuotaWarning';
import { useQuota } from '../hooks/useQuota';
import { Skeleton } from '../components/ui/skeleton';
import toast from 'react-hot-toast';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface OCRResult {
  engine: string;
  available: boolean;
  text?: string;
  confidence?: number;
  char_count?: number;
  word_count?: number;
  processing_time?: number;
  success?: boolean;
  error?: string;
  model?: string;
  ocr_engine?: string;
}

interface ComparisonResponse {
  filename: string;
  file_size: number;
  language: string;
  engines: Record<string, OCRResult>;
  comparison?: {
    available_engines: string[];
    fastest_engine?: string;
    most_detailed?: string;
    note?: string;
  };
}

export default function OCRDemoPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ComparisonResponse | null>(null);
  const [language, setLanguage] = useState('vi');
  
  // ✅ NEW: Fetch quota info
  const { quota, loading: quotaLoading, refetch: refetchQuota } = useQuota();

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      toast.error('Chỉ hỗ trợ ảnh PNG, JPG, JPEG, WebP');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Ảnh quá lớn. Tối đa 10MB');
      return;
    }

    setSelectedFile(file);
    setResults(null);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleCompare = async () => {
    if (!selectedFile) {
      toast.error('Vui lòng chọn ảnh');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', language);

    try {
      const response = await axios.post<ComparisonResponse>(
        `${API_BASE_URL}/ocr-compare/compare-engines`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000 // 60 seconds
        }
      );

      setResults(response.data);
      toast.success('So sánh OCR thành công!');
      
      // ✅ Refetch quota sau khi dùng AI
      refetchQuota();
    } catch (error: any) {
      console.error('OCR comparison error:', error);
      
      // ✅ Handle quota exceeded error
      if (error.response?.status === 403 && error.response?.data?.detail?.error_code === 'QUOTA_EXCEEDED') {
        const detail = error.response.data.detail;
        toast.error(
          <div>
            <p className="font-medium">{detail.message}</p>
            <p className="text-sm mt-1">{detail.suggestion}</p>
          </div>,
          { duration: 6000 }
        );
      } else {
        toast.error(error.response?.data?.detail || 'Lỗi khi so sánh OCR');
      }
    } finally {
      setLoading(false);
    }
  };

  const getEngineIcon = (engine: string) => {
    switch (engine.toLowerCase()) {
      case 'tesseract': return '🔤';
      case 'gemini': return '✨';
      case 'claude': return '🤖';
      case 'adobe': return '📄';
      default: return '🔍';
    }
  };

  const getEngineName = (engine: string) => {
    switch (engine.toLowerCase()) {
      case 'tesseract': return 'Tesseract OCR';
      case 'gemini': return 'Gemini Vision AI';
      case 'claude': return 'Claude AI';
      case 'adobe': return 'Adobe PDF Services';
      default: return engine;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🔍 OCR Comparison Demo</h1>
        <p className="text-gray-600">
          So sánh 4 công nghệ OCR: Tesseract, Gemini Vision AI, Claude AI, Adobe PDF Services
        </p>
      </div>

      {/* ✅ NEW: Quota Warning */}
      {quotaLoading ? (
        <Skeleton className="h-32 w-full mb-6" />
      ) : quota ? (
        <QuotaWarning quotaInfo={quota} className="mb-6" />
      ) : null}

      {/* Upload Section */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>📤 Upload Ảnh</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* File Input */}
            <div className="flex items-center gap-4">
              <label className="flex-1 cursor-pointer">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
                  {previewUrl ? (
                    <img src={previewUrl} alt="Preview" className="max-h-48 mx-auto rounded" />
                  ) : (
                    <>
                      <Upload className="w-12 h-12 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600">
                        Click để chọn ảnh hoặc kéo thả vào đây
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        PNG, JPG, JPEG, WebP • Tối đa 10MB
                      </p>
                    </>
                  )}
                </div>
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </label>
            </div>

            {/* Language Selection */}
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium">Ngôn ngữ:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-3 py-2 border rounded-md"
              >
                <option value="vi">🇻🇳 Tiếng Việt</option>
                <option value="en">🇬🇧 English</option>
                <option value="vi+en">🇻🇳🇬🇧 Vietnamese + English</option>
              </select>
            </div>

            {/* Action Button */}
            <Button
              onClick={handleCompare}
              disabled={!selectedFile || loading}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang so sánh...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  So sánh OCR
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle>📊 Kết quả tổng quan</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">File</p>
                  <p className="font-medium">{results.filename}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Kích thước</p>
                  <p className="font-medium">{(results.file_size / 1024).toFixed(1)} KB</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Ngôn ngữ</p>
                  <p className="font-medium">{results.language === 'vi' ? '🇻🇳 Tiếng Việt' : results.language}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Engines khả dụng</p>
                  <p className="font-medium">{results.comparison?.available_engines?.length || 0}/4</p>
                </div>
              </div>

              {results.comparison && results.comparison.fastest_engine && (
                <div className="mt-4 p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-800">
                    ⚡ Nhanh nhất: <strong>{getEngineName(results.comparison.fastest_engine)}</strong>
                    {results.comparison.most_detailed && (
                      <> • 📝 Chi tiết nhất: <strong>{getEngineName(results.comparison.most_detailed)}</strong></>
                    )}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Engine Results */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6">
            {Object.entries(results.engines).map(([engineName, result]) => (
              <Card key={engineName} className={result.available ? 'border-green-500' : 'border-red-300'}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <span className="text-2xl">{getEngineIcon(engineName)}</span>
                      {getEngineName(engineName)}
                    </span>
                    {result.available ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {result.available && result.success ? (
                    <div className="space-y-3">
                      {/* Metrics */}
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="p-2 bg-gray-50 rounded">
                          <p className="text-gray-600 text-xs">Thời gian</p>
                          <p className="font-medium flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {result.processing_time?.toFixed(2)}s
                          </p>
                        </div>
                        <div className="p-2 bg-gray-50 rounded">
                          <p className="text-gray-600 text-xs">Ký tự</p>
                          <p className="font-medium">{result.char_count}</p>
                        </div>
                        <div className="p-2 bg-gray-50 rounded">
                          <p className="text-gray-600 text-xs">Từ</p>
                          <p className="font-medium">{result.word_count}</p>
                        </div>
                        {result.confidence !== undefined && result.confidence > 0 && (
                          <div className="p-2 bg-gray-50 rounded">
                            <p className="text-gray-600 text-xs">Độ tin cậy</p>
                            <p className="font-medium">{(result.confidence * 100).toFixed(0)}%</p>
                          </div>
                        )}
                      </div>

                      {/* Extracted Text */}
                      <div>
                        <p className="text-sm font-medium mb-2 flex items-center gap-1">
                          <FileText className="w-4 h-4" />
                          Văn bản trích xuất:
                        </p>
                        <div className="p-3 bg-gray-50 rounded text-sm max-h-64 overflow-y-auto">
                          {result.text ? (
                            <p className="whitespace-pre-wrap">{result.text}</p>
                          ) : (
                            <p className="text-gray-400 italic">Không có văn bản</p>
                          )}
                        </div>
                      </div>

                      {/* Model Info */}
                      {result.model && (
                        <Badge variant="outline" className="text-xs">
                          Model: {result.model}
                        </Badge>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <XCircle className="w-12 h-12 mx-auto text-red-400 mb-2" />
                      <p className="text-sm text-gray-600 mb-2">
                        {result.available ? 'OCR thất bại' : 'Engine không khả dụng'}
                      </p>
                      {result.error && (
                        <p className="text-xs text-red-600 bg-red-50 p-2 rounded">
                          {result.error}
                        </p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Comparison Note */}
          {results.comparison?.note && (
            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="pt-6">
                <p className="text-sm text-yellow-800">{results.comparison.note}</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
