import React, { useState } from 'react';
import { FileText, Sparkles, Download, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const API_BASE = API_BASE_URL;

interface AIProvider {
  id: string;
  name: string;
  description: string;
  status: string;
  models: AIModel[];
  recommended: boolean;
}

interface AIModel {
  id: string;
  name: string;
  quality: number;
  speed: number;
  pricing: {
    input: number;
    output: number;
  };
}

export default function TextToWordPage() {
  const [text, setText] = useState('');
  const [provider, setProvider] = useState<string>('gemini');
  const [model, setModel] = useState<string>('');
  const [language, setLanguage] = useState<string>('vi');
  const [loading, setLoading] = useState(false);
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [selectedProviderInfo, setSelectedProviderInfo] = useState<AIProvider | null>(null);

  // Load providers on mount
  React.useEffect(() => {
    loadProviders();
  }, []);

  // Update selected provider info when provider changes
  React.useEffect(() => {
    if (providers.length > 0) {
      const providerInfo = providers.find(p => p.id === provider);
      setSelectedProviderInfo(providerInfo || null);
      // Auto-select first model when provider changes
      if (providerInfo && providerInfo.models.length > 0) {
        setModel(providerInfo.models[0].id);
      }
    }
  }, [provider, providers]);

  const loadProviders = async () => {
    try {
      console.log('🔍 Loading providers from:', `${API_BASE}/documents/ai-providers`);
      const response = await axios.get(`${API_BASE}/documents/ai-providers`);
      console.log('✅ Providers response:', response.data);
      console.log('📦 Providers array:', response.data.providers);
      setProviders(response.data.providers);
    } catch (error: any) {
      console.error('❌ Failed to load providers:', error);
      toast.error('Không thể tải danh sách AI providers');
    }
  };

  const handleGenerate = async () => {
    if (!text.trim()) {
      toast.error('Vui lòng nhập nội dung văn bản');
      return;
    }

    if (text.trim().length < 10) {
      toast.error('Văn bản phải có ít nhất 10 ký tự');
      return;
    }

    setLoading(true);
    const loadingToast = toast.loading('AI đang phân tích và tạo Word document...');

    try {
      const formData = new FormData();
      formData.append('text', text);
      formData.append('provider', provider);
      if (model) formData.append('model', model);
      formData.append('language', language);

      const response = await axios.post(
        `${API_BASE}/documents/text-to-word-smart`,
        formData,
        {
          responseType: 'blob',
          timeout: 300000, // 5 minutes - increased for AI processing
        }
      );

      // Get metadata from headers
      const providerName = response.headers['x-technology-name'] || provider;
      const modelName = response.headers['x-technology-model'] || 'unknown';
      const inputTokens = response.headers['x-input-tokens'] || '0';
      const outputTokens = response.headers['x-output-tokens'] || '0';
      const processingTime = response.headers['x-processing-time-ms'] || '0';

      // Download file
      const blob = new Blob([response.data], { type: 'application/msword' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document_${Date.now()}.doc`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.dismiss(loadingToast);
      toast.success(
        <div>
          <p className="font-semibold">✅ Tạo thành công!</p>
          <p className="text-xs mt-1">
            🤖 {providerName} ({modelName})
          </p>
          <p className="text-xs">
            📊 {inputTokens} → {outputTokens} tokens
          </p>
          <p className="text-xs">
            ⏱️ {Math.round(parseFloat(processingTime) / 1000)}s
          </p>
        </div>,
        { duration: 5000 }
      );
    } catch (error: any) {
      toast.dismiss(loadingToast);
      
      // Detailed error handling
      let errorMsg = 'Có lỗi xảy ra';
      
      if (error.code === 'ECONNABORTED') {
        errorMsg = '⏱️ Timeout: AI xử lý quá lâu (>5 phút). Thử text ngắn hơn hoặc provider khác.';
      } else if (error.response?.status === 400) {
        const detail = error.response?.data?.detail || '';
        if (detail.includes('budget')) {
          errorMsg = '💰 Vượt ngân sách AI. Kiểm tra AI Admin → Balance.';
        } else if (detail.includes('API key')) {
          errorMsg = '🔑 Chưa có API key. Vào AI Keys → Add key cho ' + provider;
        } else {
          errorMsg = detail || 'Invalid request';
        }
      } else if (error.response?.status === 500) {
        errorMsg = '🔥 Server error. Check backend logs.';
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      // Log full error details for debugging
      console.error('❌ Generate error:', error);
      console.error('📦 Response data:', error.response?.data);
      console.error('📊 Response status:', error.response?.status);
      
      // If response data is Blob, read it as text
      if (error.response?.data instanceof Blob) {
        const blobText = await error.response.data.text();
        console.error('📄 Blob content:', blobText);
        try {
          const errorJson = JSON.parse(blobText);
          console.error('🔍 Parsed error:', errorJson);
          if (errorJson.detail) {
            errorMsg = errorJson.detail;
          }
        } catch (e) {
          console.error('Failed to parse blob as JSON');
        }
      }
      
      toast.error(
        <div>
          <p className="font-semibold">❌ Lỗi</p>
          <p className="text-xs mt-1">{errorMsg}</p>
        </div>,
        { duration: 8000 }
      );
      
      console.error('Generate error:', error);
    } finally {
      setLoading(false);
    }
  };

  const exampleText = `Báo cáo dự án Website Thương mại điện tử

Giới thiệu: Dự án phát triển website thương mại điện tử cho công ty ABC được khởi động từ tháng 1/2025. Mục tiêu chính là tạo ra một nền tảng mua sắm trực tuyến hiện đại, thân thiện với người dùng.

Các tính năng chính:
- Tìm kiếm và lọc sản phẩm thông minh
- Giỏ hàng và thanh toán đa phương thức
- Quản lý đơn hàng realtime
- Hệ thống đánh giá và phản hồi

Tiến độ thực hiện:
Giai đoạn 1 (Tháng 1-2): Phân tích yêu cầu và thiết kế UI/UX đã hoàn thành 100%.
Giai đoạn 2 (Tháng 3-4): Phát triển backend API đạt 85%, frontend đạt 70%.

Kết luận: Dự án đang đi đúng tiến độ. Dự kiến hoàn thành và đưa vào sử dụng vào cuối tháng 4/2025.`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-2xl p-8 mb-6 text-white">
          <div className="flex items-center gap-4 mb-4">
            <Sparkles className="w-12 h-12" />
            <div>
              <h1 className="text-3xl font-bold">AI Text to Word</h1>
              <p className="text-purple-100 text-lg">
                Biến văn bản thành tài liệu Word đẹp mắt với AI
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5" />
                <span className="font-semibold">Smart Formatting</span>
              </div>
              <p className="text-sm text-purple-100">
                AI tự động nhận diện cấu trúc và định dạng phù hợp
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-5 h-5" />
                <span className="font-semibold">Professional Output</span>
              </div>
              <p className="text-sm text-purple-100">
                File .docx chuẩn OpenXML - 100% Word compatible
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-5 h-5" />
                <span className="font-semibold">Multi Provider</span>
              </div>
              <p className="text-sm text-purple-100">
                Chọn Gemini hoặc Claude theo nhu cầu
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Input */}
          <div className="lg:col-span-2 space-y-6">
            {/* Text Input */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <label className="text-lg font-semibold text-gray-800">
                  📝 Nhập văn bản
                </label>
                <button
                  onClick={() => setText(exampleText)}
                  className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                >
                  Dùng ví dụ
                </button>
              </div>
              
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Nhập nội dung văn bản của bạn tại đây...

AI sẽ tự động:
• Nhận diện tiêu đề và các phần
• Tạo danh sách có đầu mục
• Định dạng thông tin quan trọng
• Thêm hộp highlight cho kết luận"
                className="w-full h-[500px] p-4 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all resize-none font-mono text-sm"
              />
              
              <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                <span>{text.length} ký tự</span>
                {text.length > 0 && text.length < 10 && (
                  <span className="text-red-500 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    Cần ít nhất 10 ký tự
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Settings */}
          <div className="space-y-6">
            {/* AI Provider Selection */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                🤖 AI Provider
              </h3>
              
              {providers.length === 0 ? (
                <div className="text-center py-4 text-gray-500">
                  <p>Đang tải providers...</p>
                  <p className="text-xs mt-2">Nếu không hiện, check console logs</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {providers.map((p) => (
                  <div
                    key={p.id}
                    onClick={() => setProvider(p.id)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      provider === p.id
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">
                            {p.name}
                          </span>
                          {p.recommended && (
                            <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
                              Khuyên dùng
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          {p.description}
                        </p>
                      </div>
                      <div
                        className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          provider === p.id
                            ? 'border-purple-500 bg-purple-500'
                            : 'border-gray-300'
                        }`}
                      >
                        {provider === p.id && (
                          <div className="w-2 h-2 bg-white rounded-full" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                </div>
              )}

              {/* Model Selection */}
              {selectedProviderInfo && selectedProviderInfo.models.length > 0 && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model
                  </label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
                  >
                    {selectedProviderInfo.models.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name} (Quality: {m.quality}/10, Speed: {m.speed}/10)
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Language */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                🌍 Ngôn ngữ
              </h3>
              
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
              >
                <option value="vi">🇻🇳 Tiếng Việt</option>
                <option value="en">🇬🇧 English</option>
                <option value="zh">🇨🇳 中文</option>
                <option value="ja">🇯🇵 日本語</option>
                <option value="ko">🇰🇷 한국어</option>
                <option value="fr">🇫🇷 Français</option>
                <option value="de">🇩🇪 Deutsch</option>
                <option value="es">🇪🇸 Español</option>
              </select>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={loading || !text.trim() || text.trim().length < 10}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  Đang tạo...
                </>
              ) : (
                <>
                  <Download className="w-6 h-6" />
                  Tạo Word Document
                </>
              )}
            </button>

            {/* Info Box */}
            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
              <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Output Format
              </h4>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>✅ File .doc (MHTML)</li>
                <li>✅ A4 size (21cm × 29.7cm)</li>
                <li>✅ Times New Roman 13pt</li>
                <li>✅ Thụt đầu dòng 1cm</li>
                <li>✅ Màu sắc và borders đẹp</li>
                <li>✅ Mở được bằng Word/Docs</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Features Info */}
        <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            ✨ AI tự động nhận diện
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl mb-2">📑</div>
              <h4 className="font-semibold text-gray-900 mb-1">Tiêu đề</h4>
              <p className="text-sm text-gray-600">
                H1, H2, H3 với định dạng riêng
              </p>
            </div>
            
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">📝</div>
              <h4 className="font-semibold text-gray-900 mb-1">Đoạn văn</h4>
              <p className="text-sm text-gray-600">
                Căn đều 2 bên, thụt đầu dòng
              </p>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="text-2xl mb-2">📋</div>
              <h4 className="font-semibold text-gray-900 mb-1">Danh sách</h4>
              <p className="text-sm text-gray-600">
                Bullet points hoặc số thứ tự
              </p>
            </div>
            
            <div className="p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl mb-2">💡</div>
              <h4 className="font-semibold text-gray-900 mb-1">Info Box</h4>
              <p className="text-sm text-gray-600">
                Thông tin quan trọng, kết luận
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
