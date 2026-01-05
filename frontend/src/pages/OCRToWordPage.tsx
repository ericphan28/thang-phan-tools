import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Download, AlertCircle, Loader2, Eye, X } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import api from '../services/api';
import toast from 'react-hot-toast';
import { QuotaWarning } from '../components/QuotaWarning';
import { useQuota } from '../hooks/useQuota';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import { config } from '../config';

/**
 * OCR TO WORD PAGE - Vietnamese Document Text Extraction
 * 
 * 4-Step Workflow:
 * 1. Upload PDF
 * 2. Auto-detect type (Text-based / Scanned)
 * 3. Process with AI OCR
 * 4. Download Word result
 * 
 * Mobile-First Responsive Design:
 * - Desktop: 3-column layout
 * - Tablet: 2-column layout
 * - Mobile: Stacked vertical layout
 * 
 * Modes:
 * - Public Demo: No login required, show upgrade CTA after
 * - User Mode: Logged in, use quota system
 */

interface ProcessingStep {
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  message?: string;
}

interface DetectionResult {
  isScanned: boolean;
  method: string;
  confidence: string;
  totalPages: number;
}

interface ExtractionMetadata {
  isScanned: boolean;
  detectionMethod: string;
  totalPages: number;
  textLength: number;
  confidence: string;
  aiUsed: boolean;
  processingTime: number;
}

export default function OCRToWordPage() {
  // Auth check
  const { isAuthenticated, user } = useAuth();
  const isPublicDemo = !isAuthenticated;
  
  // State management
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline' | null>(null);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [processingTime, setProcessingTime] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [showUpgradeCTA, setShowUpgradeCTA] = useState(false);
  const [extractionMetadata, setExtractionMetadata] = useState<ExtractionMetadata | null>(null);
  
  // Quota tracking (only for logged in users)
  const { quota, loading: quotaLoading, refetch: refetchQuota } = useQuota();
  
  // Refs
  const fileInputRef = useRef<HTMLInputElement>(null);
  const downloadLinkRef = useRef<HTMLAnchorElement>(null);
  
  // Processing steps for UI - Use state to trigger re-render
  const [steps, setSteps] = useState<ProcessingStep[]>([
    { name: 'Tải file lên', status: 'pending' },
    { name: 'Phát hiện loại file', status: 'pending' },
    { name: 'Trích xuất văn bản', status: 'pending' },
    { name: 'Tạo file Word', status: 'pending' },
  ]);
  
  // Update step status
  const updateStepStatus = (index: number, status: ProcessingStep['status'], message?: string) => {
    setSteps(prevSteps => {
      const newSteps = [...prevSteps];
      newSteps[index] = {
        ...newSteps[index],
        status,
        message
      };
      return newSteps;
    });
    setCurrentStep(index);
  };
  
  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Validate PDF
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('❌ Chỉ hỗ trợ file PDF');
      return;
    }
    
    // Validate size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      toast.error('❌ File quá lớn. Giới hạn 50MB.');
      return;
    }
    
    setSelectedFile(file);
    setError(null);
    setDownloadUrl(null);
    setDetectionResult(null);
    toast.success(`✅ Đã chọn file: ${file.name}`);
  };
  
  // Handle drag & drop
  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    
    if (file && file.name.toLowerCase().endsWith('.pdf')) {
      setSelectedFile(file);
      toast.success(`✅ Đã thả file: ${file.name}`);
    } else {
      toast.error('❌ Chỉ hỗ trợ file PDF');
    }
  };
  
  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };
  
  // Check backend health
  const checkBackendHealth = async () => {
    setBackendStatus('checking');
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout
      
      // Use config API URL instead of hardcoded localhost
      const healthUrl = config.apiUrl.replace('/api/v1', '') + '/health';
      await fetch(healthUrl, { 
        signal: controller.signal,
        method: 'GET'
      });
      
      clearTimeout(timeoutId);
      setBackendStatus('online');
      return true;
    } catch (error) {
      setBackendStatus('offline');
      toast.error(
        <div>
          <p className="font-semibold">🔴 Backend không kết nối được</p>
          <p className="text-sm mt-1">Vui lòng khởi động backend server</p>
        </div>,
        { duration: 8000 }
      );
      return false;
    }
  };

  // Handle OCR processing
  const handleProcess = async () => {
    if (!selectedFile) {
      toast.error('Vui lòng chọn file PDF');
      return;
    }
    
    // Check backend first
    const isBackendOnline = await checkBackendHealth();
    if (!isBackendOnline) {
      return;
    }
    
    // Check quota (only for logged in users)
    if (!isPublicDemo && quota && quota.usage_this_month >= quota.quota_monthly) {
      toast.error('❌ Bạn đã hết quota. Vui lòng nâng cấp gói.');
      return;
    }
    
    setIsProcessing(true);
    setError(null);
    const startTime = Date.now();
    
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Debug: Log FormData entries
      console.log('📤 FormData entries:');
      for (const [key, value] of formData.entries()) {
        console.log(`  ${key}:`, value);
      }
      
      // Step 1: Upload (start)
      updateStepStatus(0, 'processing', 'Đang tải file...');
      
      // Setup timeout controller
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        throw new Error('TIMEOUT');
      }, 120000); // 120 giây timeout (cho file nhiều trang)
      
      // Track timeouts to clear them when API responds
      const stepTimeouts: number[] = [];
      
      const endpoint = isPublicDemo ? '/documents/ocr-to-word-demo' : '/documents/ocr-to-word';
      const response = await api.post(endpoint, formData, {
        responseType: 'blob',
        headers: isPublicDemo ? { 'X-Skip-Auth': 'true' } : undefined,
        signal: controller.signal,
        // Don't set Content-Type - browser auto-sets with boundary for FormData
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          if (percentCompleted < 100) {
            updateStepStatus(0, 'processing', `Đang tải lên... ${percentCompleted}%`);
          } else if (percentCompleted === 100) {
            // Upload done - Now backend is processing (REAL work happens here!)
            updateStepStatus(0, 'completed', 'Tải file thành công');
            updateStepStatus(1, 'processing', 'Đang phát hiện loại file...');
            
            // After upload, show real processing status
            // Backend is now: detecting → uploading to Gemini → extracting → creating Word
            setTimeout(() => {
              updateStepStatus(1, 'completed', 'Phát hiện hoàn tất');
              updateStepStatus(2, 'processing', 'Đang gửi PDF lên Gemini AI...');
            }, 2000);
            
            // Show long processing message
            setTimeout(() => {
              updateStepStatus(2, 'processing', 'Gemini đang trích xuất văn bản... (10-20s)');
            }, 5000);
          }
        },
      });
      
      // Clear all step timeouts and timeout controller
      stepTimeouts.forEach(t => clearTimeout(t));
      clearTimeout(timeoutId);
      
      // Extract metadata from headers
      const quotaUsed = response.headers['x-quota-used'];
      const quotaTotal = response.headers['x-quota-total'];
      const processTime = response.headers['x-processing-time'];
      const isScanned = response.headers['x-is-scanned'] === 'true';
      const detectionMethod = response.headers['x-detection-method'] || 'unknown';
      const totalPages = parseInt(response.headers['x-total-pages'] || '0');
      const textLength = parseInt(response.headers['x-text-length'] || '0');
      const confidence = response.headers['x-confidence'] || 'low';
      const aiUsed = response.headers['x-ai-used'] === 'true';
      
      if (processTime) {
        setProcessingTime(parseFloat(processTime));
      }
      
      // Save extraction metadata
      setExtractionMetadata({
        isScanned,
        detectionMethod,
        totalPages,
        textLength,
        confidence,
        aiUsed,
        processingTime: processTime ? parseFloat(processTime) : 0
      });
      
      // Create download URL
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);
      
      // Backend done - Update UI to reflect actual steps
      // Step 2: Extraction (Gemini) - already completed
      updateStepStatus(2, 'completed', 'Trích xuất văn bản hoàn tất');
      
      // Step 3: Word creation - fast, backend already did it
      updateStepStatus(3, 'completed', 'Tạo file Word thành công');
      
      // Show success toast
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      toast.success(`✅ Hoàn thành trong ${elapsed}s!`);
      
      // Refetch quota (for logged in users)
      if (!isPublicDemo) {
        refetchQuota();
      } else {
        // Public demo: Show upgrade CTA after successful processing
        setShowUpgradeCTA(true);
      }
      
      // Auto-download after 1 second
      setTimeout(() => {
        if (downloadLinkRef.current) {
          downloadLinkRef.current.click();
        }
      }, 1000);
      
    } catch (err: any) {
      console.error('OCR error:', err);
      console.error('Response data:', err.response?.data);
      console.error('Response status:', err.response?.status);
      
      // Update steps to error
      updateStepStatus(currentStep, 'error', 'Có lỗi xảy ra');
      
      // Show friendly error với hướng dẫn cụ thể
      let errorMessage = 'Không thể xử lý file. Vui lòng thử lại.';
      let errorDetail = '';

      // If responseType is 'blob', backend errors often come back as JSON Blob.
      const tryExtractBlobDetail = async (): Promise<string | null> => {
        const data = err?.response?.data;
        if (data instanceof Blob && data.type?.includes('application/json')) {
          try {
            const text = await data.text();
            const json = JSON.parse(text);
            if (typeof json?.detail === 'string') {
              return json.detail;
            }
          } catch {
            return null;
          }
        }
        return null;
      };
      
      if (err.message === 'TIMEOUT') {
        errorMessage = '⏱️ Xử lý quá lâu (>60 giây)';
        errorDetail = 'File quá lớn hoặc backend quá tải. Vui lòng thử lại hoặc chọn file nhỏ hơn.';
      } else if (err.code === 'ERR_NETWORK' || err.message.includes('Network')) {
        errorMessage = '🔴 Không kết nối được backend';
        errorDetail = 'Backend server chưa khởi động. Vui lòng restart backend.';
      } else if (err.response?.status === 401 && isPublicDemo) {
        errorMessage = '❌ Vui lòng đăng nhập để sử dụng tính năng này.';
      } else if (err.response?.status === 403) {
        const blobDetail = await tryExtractBlobDetail();
        errorMessage = blobDetail || '❌ Bạn đã hết quota. Vui lòng nâng cấp gói.';
        errorDetail = blobDetail ? 'Bạn có thể nâng cấp để tiếp tục sử dụng.' : errorDetail;
      } else if (err.response?.status === 400) {
        const blobDetail = await tryExtractBlobDetail();
        errorMessage = blobDetail || err.response?.data?.detail || 'File không hợp lệ.';
      } else if (err.response?.status === 500) {
        const blobDetail = await tryExtractBlobDetail();
        errorMessage = blobDetail || 'Lỗi server. Vui lòng thử lại sau.';
      }
      
      setError(errorMessage);
      toast.error(
        <div>
          <p className="font-semibold">{errorMessage}</p>
          {errorDetail && <p className="text-sm mt-1">{errorDetail}</p>}
          <div className="flex gap-2 mt-3">
            <button 
              onClick={() => handleProcess()} 
              className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition"
            >
              🔄 Thử lại
            </button>
            <button 
              onClick={() => handleReset()} 
              className="px-3 py-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700 transition"
            >
              📄 Chọn file khác
            </button>
          </div>
        </div>,
        { duration: 15000 }
      );
      
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Reset to upload new file
  const handleReset = () => {
    setSelectedFile(null);
    setDownloadUrl(null);
    setDetectionResult(null);
    setError(null);
    setCurrentStep(0);
    setExtractionMetadata(null);
    setSteps([
      { name: 'Tải file lên', status: 'pending' },
      { name: 'Phát hiện loại file', status: 'pending' },
      { name: 'Trích xuất văn bản', status: 'pending' },
      { name: 'Tạo file Word', status: 'pending' },
    ]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-4 md:p-6 lg:p-8">
      {/* Container */}
      <div className="container mx-auto max-w-7xl">
        
        {/* Header */}
        <div className="text-center mb-6 md:mb-8">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-3 md:mb-4">
            🇻🇳 Trích xuất văn bản PDF sang Word
          </h1>
          <p className="text-base md:text-lg text-gray-600">
            Chuyển đổi PDF sang Word với AI - Độ chính xác 98% tiếng Việt
          </p>
          
          {/* Backend Status */}
          {backendStatus && (
            <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium">
              {backendStatus === 'checking' && (
                <>
                  <Loader2 className="h-3 w-3 animate-spin text-blue-600" />
                  <span className="text-blue-700">Đang kiểm tra kết nối...</span>
                </>
              )}
              {backendStatus === 'online' && (
                <>
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-green-700">Backend sẵn sàng</span>
                </>
              )}
              {backendStatus === 'offline' && (
                <>
                  <div className="h-2 w-2 rounded-full bg-red-500" />
                  <span className="text-red-700">Backend không phản hồi</span>
                </>
              )}
            </div>
          )}
          
          {/* Public demo banner */}
          {isPublicDemo && (
            <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-2xl mx-auto">
              <p className="text-sm text-yellow-800">
                ⚡ Bạn đang dùng thử miễn phí. <Link to="/login" className="font-semibold underline">Đăng nhập</Link> để lưu lịch sử và không giới hạn.
              </p>
            </div>
          )}
        </div>
        
        {/* Quota Warning (only for logged in users) */}
        {!isPublicDemo && quota && quota.is_warning_level && <QuotaWarning quotaInfo={quota} />}
        
        {/* Main Content - Responsive Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-6">
          
          {/* Column 1: Upload Zone */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg md:text-xl">
                <Upload className="h-5 w-5" />
                Bước 1: Chọn File
              </CardTitle>
              <CardDescription>
                Kéo thả hoặc chọn file PDF (tối đa 50MB)
              </CardDescription>
            </CardHeader>
            <CardContent>
              
              {/* Drop Zone */}
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
                className={`
                  border-2 border-dashed rounded-lg p-6 md:p-8 text-center cursor-pointer
                  transition-all duration-200
                  ${selectedFile 
                    ? 'border-green-500 bg-green-50' 
                    : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                  }
                `}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                {selectedFile ? (
                  <div className="space-y-3">
                    <FileText className="h-12 w-12 md:h-16 md:w-16 text-green-600 mx-auto" />
                    <div>
                      <p className="font-semibold text-gray-900 break-words">
                        {selectedFile.name}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReset();
                      }}
                      className="mt-2"
                    >
                      <X className="h-4 w-4 mr-2" />
                      Chọn file khác
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Upload className="h-12 w-12 md:h-16 md:w-16 text-gray-400 mx-auto" />
                    <div>
                      <p className="font-semibold text-gray-700">
                        Kéo thả file PDF vào đây
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        hoặc nhấn để chọn file
                      </p>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Process Button */}
              <Button
                onClick={handleProcess}
                disabled={!selectedFile || isProcessing || (quota ? quota.usage_this_month >= quota.quota_monthly : false)}
                className="w-full mt-4 min-h-[44px]"
                size="lg"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    {currentStep === 0 && 'Đang tải lên...'}
                    {currentStep === 1 && 'Đang phát hiện...'}
                    {currentStep === 2 && 'Đang trích xuất...'}
                    {currentStep === 3 && 'Đang tạo Word...'}
                    {currentStep > 3 && 'Hoàn tất!'}
                  </>
                ) : (
                  <>
                    <FileText className="h-5 w-5 mr-2" />
                    Bắt đầu trích xuất
                  </>
                )}
              </Button>
              
            </CardContent>
          </Card>
          
          {/* Column 2: Processing Status */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg md:text-xl">
                <Loader2 className={`h-5 w-5 ${isProcessing ? 'animate-spin' : ''}`} />
                Bước 2-3: Xử Lý
              </CardTitle>
              <CardDescription>
                Tiến trình trích xuất văn bản
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              
              {/* Progress Steps */}
              {steps.map((step, index) => (
                <div key={index} className="flex items-start gap-3">
                  {/* Status Icon */}
                  <div className="flex-shrink-0 mt-1">
                    {step.status === 'completed' && (
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    )}
                    {step.status === 'processing' && (
                      <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
                    )}
                    {step.status === 'pending' && (
                      <div className="h-6 w-6 rounded-full border-2 border-gray-300" />
                    )}
                    {step.status === 'error' && (
                      <AlertCircle className="h-6 w-6 text-red-600" />
                    )}
                  </div>
                  
                  {/* Step Info */}
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium ${
                      step.status === 'completed' ? 'text-green-700' :
                      step.status === 'processing' ? 'text-blue-700' :
                      step.status === 'error' ? 'text-red-700' :
                      'text-gray-500'
                    }`}>
                      {step.name}
                    </p>
                    {step.message && (
                      <p className="text-sm text-gray-600 mt-1">
                        {step.message}
                      </p>
                    )}
                  </div>
                  
                  {/* Badge */}
                  {step.status === 'completed' && (
                    <Badge variant="secondary" className="flex-shrink-0">
                      Xong
                    </Badge>
                  )}
                </div>
              ))}
              
              {/* Processing Time */}
              {processingTime > 0 && (
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Thời gian xử lý:</span>
                    <span className="font-semibold text-blue-600">
                      {processingTime}s
                    </span>
                  </div>
                </div>
              )}
              
              {/* Error Message with Retry */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-red-900">{error}</p>
                      <div className="flex gap-2 mt-3">
                        <Button
                          onClick={handleProcess}
                          size="sm"
                          variant="outline"
                          className="border-red-300 hover:bg-red-100"
                        >
                          🔄 Thử lại
                        </Button>
                        <Button
                          onClick={handleReset}
                          size="sm"
                          variant="outline"
                          className="border-gray-300"
                        >
                          📄 File khác
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
            </CardContent>
          </Card>
          
          {/* Column 3: Download Result */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg md:text-xl">
                <Download className="h-5 w-5" />
                Bước 4: Tải Xuống
              </CardTitle>
              <CardDescription>
                File Word kết quả
              </CardDescription>
            </CardHeader>
            <CardContent>
              
              {downloadUrl ? (
                <div className="space-y-4">
                  {/* Success Message */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
                      <div>
                        <p className="font-semibold text-green-900">
                          Trích xuất thành công!
                        </p>
                        <p className="text-sm text-green-700 mt-1">
                          File Word đã sẵn sàng để tải xuống
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Extraction Metadata */}
                  {extractionMetadata && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
                      <h4 className="font-semibold text-blue-900 text-sm mb-2">
                        📊 Thông tin chi tiết
                      </h4>
                      
                      {/* PDF Type */}
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Loại file:</span>
                        <Badge 
                          variant={extractionMetadata.isScanned ? "default" : "secondary"}
                          className={extractionMetadata.isScanned ? "bg-orange-500" : "bg-green-600"}
                        >
                          {extractionMetadata.isScanned ? '📸 PDF Scan (Ảnh)' : '📄 PDF Thông thường'}
                        </Badge>
                      </div>
                      
                      {/* AI Usage */}
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Xử lý bằng AI:</span>
                        <span className="font-medium text-blue-700">
                          ✅ Có (Gemini 2.5 Flash)
                        </span>
                      </div>
                      
                      <div className="text-xs text-blue-600 mt-1 bg-blue-100 rounded px-2 py-1">
                        💡 Luôn dùng Gemini để đảm bảo dấu tiếng Việt chính xác 98%
                      </div>
                      
                      {/* Detection Method */}
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Phương thức phát hiện:</span>
                        <span className="font-medium text-gray-900 text-right">
                          {extractionMetadata.detectionMethod === 'text_extraction' && '📝 Trích xuất văn bản'}
                          {extractionMetadata.detectionMethod === 'image_ratio' && '🖼️ Tỷ lệ hình ảnh'}
                          {extractionMetadata.detectionMethod === 'ambiguous_fallback' && '🔍 Phân tích chi tiết'}
                          {!['text_extraction', 'image_ratio', 'ambiguous_fallback'].includes(extractionMetadata.detectionMethod) && extractionMetadata.detectionMethod}
                        </span>
                      </div>
                      
                      {/* Confidence */}
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Độ tin cậy:</span>
                        <Badge 
                          variant="secondary"
                          className={
                            extractionMetadata.confidence === 'high' ? 'bg-green-100 text-green-800' :
                            extractionMetadata.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-orange-100 text-orange-800'
                          }
                        >
                          {extractionMetadata.confidence === 'high' && '🎯 Cao'}
                          {extractionMetadata.confidence === 'medium' && '📊 Trung bình'}
                          {extractionMetadata.confidence === 'low' && '⚠️ Thấp'}
                        </Badge>
                      </div>
                      
                      {/* Total Pages */}
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Số trang:</span>
                        <span className="font-medium text-gray-900">
                          {extractionMetadata.totalPages} trang
                        </span>
                      </div>
                      
                      {/* Text Length */}
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Văn bản trích xuất:</span>
                        <span className="font-medium text-gray-900">
                          {extractionMetadata.textLength.toLocaleString()} ký tự
                        </span>
                      </div>
                      
                      {/* Processing Time */}
                      <div className="flex justify-between items-center text-sm pt-2 border-t border-blue-300">
                        <span className="text-gray-600">Thời gian xử lý:</span>
                        <span className="font-semibold text-blue-600">
                          {extractionMetadata.processingTime.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {/* Download Button */}
                  <a
                    ref={downloadLinkRef}
                    href={downloadUrl}
                    download={`OCR_${selectedFile?.name.replace('.pdf', '')}.docx`}
                    className="hidden"
                  >
                    Download
                  </a>
                  
                  <Button
                    onClick={() => downloadLinkRef.current?.click()}
                    className="w-full min-h-[44px]"
                    size="lg"
                  >
                    <Download className="h-5 w-5 mr-2" />
                    Tải xuống file Word
                  </Button>
                  
                  {/* Upgrade CTA for public demo */}
                  {isPublicDemo && showUpgradeCTA && (
                    <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300 mt-4">
                      <CardContent className="pt-4">
                        <h3 className="font-bold text-blue-900 mb-2 text-center">
                          ⭐ Nâng cấp để không giới hạn
                        </h3>
                        <p className="text-sm text-blue-700 mb-3 text-center">
                          Chỉ 299k/tháng - Unlimited OCR + Lưu lịch sử + Hỗ trợ ưu tiên
                        </p>
                        <div className="flex gap-2">
                          <Link to="/pricing" className="flex-1">
                            <Button className="w-full bg-blue-600 hover:bg-blue-700">
                              Xem bảng giá
                            </Button>
                          </Link>
                          <Link to="/login" className="flex-1">
                            <Button variant="outline" className="w-full">
                              Đăng nhập
                            </Button>
                          </Link>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                  
                  {/* Process Another File */}
                  <Button
                    onClick={handleReset}
                    variant="outline"
                    className="w-full min-h-[44px]"
                    size="lg"
                  >
                    <Upload className="h-5 w-5 mr-2" />
                    Xử lý file mới
                  </Button>
                  
                </div>
              ) : (
                <div className="text-center py-12">
                  <Download className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">
                    Kết quả sẽ hiển thị sau khi xử lý
                  </p>
                </div>
              )}
              
            </CardContent>
          </Card>
          
        </div>
        
        {/* Features Info */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
              
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                  98%
                </div>
                <p className="text-sm text-gray-600">
                  Độ chính xác tiếng Việt
                </p>
              </div>
              
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-purple-600 mb-2">
                  {'<30s'}
                </div>
                <p className="text-sm text-gray-600">
                  Tốc độ xử lý/trang
                </p>
              </div>
              
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-green-600 mb-2">
                  AI
                </div>
                <p className="text-sm text-gray-600">
                  Gemini 2.0 Flash Vision
                </p>
              </div>
              
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-orange-600 mb-2">
                  Auto
                </div>
                <p className="text-sm text-gray-600">
                  Phát hiện thông minh
                </p>
              </div>
              
            </div>
          </CardContent>
        </Card>
        
      </div>
    </div>
  );
}
