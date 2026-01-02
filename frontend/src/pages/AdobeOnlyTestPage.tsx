import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText, Upload, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ConversionResult {
  success: boolean;
  message: string;
  filename?: string;
  size?: number;
  technology?: string;
  ocr?: boolean;
  error?: string;
}

type ConversionMode = 'adobe' | 'pdf2docx' | 'hybrid';

export default function AdobeOnlyTestPage() {
  const [file, setFile] = useState<File | null>(null);
  const [enableOCR, setEnableOCR] = useState(false);
  const [ocrLanguage, setOcrLanguage] = useState('en-US');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [conversionMode, setConversionMode] = useState<ConversionMode>('adobe');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        toast.error('Chỉ chấp nhận file PDF');
        return;
      }
      if (selectedFile.size > 50 * 1024 * 1024) {
        toast.error('File quá lớn. Giới hạn 50MB');
        return;
      }
      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleConvert = async () => {
    if (!file) {
      toast.error('Vui lòng chọn file PDF');
      return;
    }

    setIsProcessing(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Endpoint based on mode
      let endpoint: string;
      if (conversionMode === 'adobe') {
        endpoint = `${API_BASE}/api/v1/documents/convert/pdf-to-word-adobe-only`;
        formData.append('enable_ocr', enableOCR.toString());
        formData.append('ocr_language', ocrLanguage);
      } else if (conversionMode === 'pdf2docx') {
        endpoint = `${API_BASE}/api/v1/documents/convert/pdf-to-word-pdf2docx-only`;
      } else {
        // Hybrid mode
        endpoint = `${API_BASE}/api/v1/documents/convert/pdf-to-word-hybrid-vietnamese`;
      }

      const response = await axios.post(endpoint, formData, {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        }
      });

      // Get metadata from headers
      const technology = response.headers['x-technology-engine'] || conversionMode;
      const ocr = response.headers['x-technology-ocr'] === 'true';
      const quality = response.headers['x-technology-quality'] || '10/10';
      const textSource = response.headers['x-text-source'] || '';
      const layoutSource = response.headers['x-layout-source'] || '';

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = file.name.replace('.pdf', '.docx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      let message = `✅ Chuyển đổi thành công (Quality: ${quality})`;
      if (conversionMode === 'hybrid') {
        message = `✅ Hybrid: ${textSource} text + ${layoutSource} layout (Quality: ${quality})`;
      }

      setResult({
        success: true,
        message,
        filename: link.download,
        size: response.data.size,
        technology,
        ocr
      });

      toast.success('✅ Đã chuyển đổi và tải xuống thành công!');
    } catch (error: any) {
      console.error('Conversion error:', error);
      
      const errorMsg = error.response?.data?.detail || error.message || 'Lỗi không xác định';
      
      setResult({
        success: false,
        message: '❌ Chuyển đổi thất bại',
        error: errorMsg
      });

      toast.error(`Lỗi: ${errorMsg}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold mb-2">🔵 Technology Test Tool</h1>
        <p className="text-gray-600">
          Test riêng biệt từng công nghệ chuyển đổi PDF → Word - Không có fallback, không có mixing
        </p>
      </div>

      {/* Mode Selection */}
      <Card className="mb-6 bg-gradient-to-r from-blue-50 via-green-50 to-yellow-50">
        <CardHeader>
          <CardTitle>Chọn công nghệ test</CardTitle>
          <CardDescription>Select one technology to test in isolation</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Adobe */}
            <button
              onClick={() => {
                setConversionMode('adobe');
                setResult(null);
              }}
              className={`p-4 rounded-lg border-2 transition-all ${
                conversionMode === 'adobe'
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              <div className="text-left">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-3 h-3 rounded-full ${conversionMode === 'adobe' ? 'bg-blue-500' : 'bg-gray-300'}`} />
                  <span className="font-semibold text-blue-700">Adobe PDF Services</span>
                </div>
                <p className="text-sm text-gray-600">
                  🔷 AI-powered, 10/10 quality
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  ⚠️ NO Vietnamese OCR
                </p>
              </div>
            </button>

            {/* pdf2docx */}
            <button
              onClick={() => {
                setConversionMode('pdf2docx');
                setResult(null);
              }}
              className={`p-4 rounded-lg border-2 transition-all ${
                conversionMode === 'pdf2docx'
                  ? 'border-green-500 bg-green-50 shadow-md'
                  : 'border-gray-200 hover:border-green-300'
              }`}
            >
              <div className="text-left">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-3 h-3 rounded-full ${conversionMode === 'pdf2docx' ? 'bg-green-500' : 'bg-gray-300'}`} />
                  <span className="font-semibold text-green-700">pdf2docx Library</span>
                </div>
                <p className="text-sm text-gray-600">
                  💻 Python local, 7/10 quality
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  ❌ NO OCR support
                </p>
              </div>
            </button>

            {/* Hybrid */}
            <button
              onClick={() => {
                setConversionMode('hybrid');
                setResult(null);
              }}
              className={`p-4 rounded-lg border-2 transition-all ${
                conversionMode === 'hybrid'
                  ? 'border-yellow-500 bg-yellow-50 shadow-md'
                  : 'border-gray-200 hover:border-yellow-300'
              }`}
            >
              <div className="text-left">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-3 h-3 rounded-full ${conversionMode === 'hybrid' ? 'bg-yellow-500' : 'bg-gray-300'}`} />
                  <span className="font-semibold text-yellow-700">🌟 Hybrid</span>
                </div>
                <p className="text-sm text-gray-600">
                  Gemini text + Adobe layout
                </p>
                <p className="text-xs text-green-600 mt-1">
                  ✅ Best for Vietnamese scan!
                </p>
              </div>
            </button>
          </div>

          {/* Technology descriptions */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            {conversionMode === 'adobe' && (
              <div>
                <h4 className="font-semibold text-blue-700 mb-2">🔷 Adobe PDF Services</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• AI-powered conversion (cloud)</li>
                  <li>• 10/10 quality for layout & images</li>
                  <li>• Supports 50+ languages OCR</li>
                  <li className="text-red-600">• ⚠️ Does NOT support Vietnamese OCR</li>
                </ul>
              </div>
            )}
            {conversionMode === 'pdf2docx' && (
              <div>
                <h4 className="font-semibold text-green-700 mb-2">💻 pdf2docx Library</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Python library (local processing)</li>
                  <li>• 7/10 quality (good for simple docs)</li>
                  <li>• Fast, no cloud dependency</li>
                  <li className="text-red-600">• ❌ Cannot do OCR (text-based PDFs only)</li>
                </ul>
              </div>
            )}
            {conversionMode === 'hybrid' && (
              <div>
                <h4 className="font-semibold text-yellow-700 mb-2">🌟 Hybrid Approach</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li className="text-green-600">• ✅ <strong>Best solution for Vietnamese scanned PDFs!</strong></li>
                  <li>• <strong>Gemini AI OCR:</strong> 98% Vietnamese text accuracy</li>
                  <li>• <strong>Adobe layout:</strong> 100% image preservation</li>
                  <li>• <strong>Result:</strong> Perfect text + Perfect images</li>
                  <li className="text-blue-600 mt-2">• Automatically combines both technologies</li>
                  <li className="text-gray-500">• Takes longer (2 steps) but highest quality</li>
                </ul>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Main Conversion Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            PDF → Word ({conversionMode === 'adobe' ? 'Adobe Only' : conversionMode === 'hybrid' ? 'Hybrid' : 'pdf2docx Only'})
          </CardTitle>
          <CardDescription>
            {conversionMode === 'adobe' && 'Direct Adobe API call - 10/10 quality, AI-powered layout preservation'}
            {conversionMode === 'pdf2docx' && 'Pure Python library - 7/10 quality, fast & free, local processing'}
            {conversionMode === 'hybrid' && 'Gemini Vietnamese OCR + Adobe layout preservation = Perfect result'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Upload */}
          <div>
            <Label htmlFor="file">Chọn file PDF</Label>
            <Input
              id="file"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="mt-2"
            />
            {file && (
              <p className="text-sm text-gray-600 mt-2">
                📄 {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </p>
            )}
          </div>

          {/* OCR Settings - Only for Adobe */}
          {conversionMode === 'adobe' && (
            <div className="space-y-4 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="enable-ocr"
                  checked={enableOCR}
                  onChange={(e) => setEnableOCR(e.target.checked)}
                  className="w-4 h-4"
                />
                <Label htmlFor="enable-ocr">Enable OCR (cho PDF scan)</Label>
              </div>

              {enableOCR && (
                <div>
                  <Label htmlFor="ocr-language">OCR Language</Label>
                  <Select value={ocrLanguage} onValueChange={setOcrLanguage}>
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en-US">English (US)</SelectItem>
                      <SelectItem value="fr-FR">French</SelectItem>
                      <SelectItem value="de-DE">German</SelectItem>
                      <SelectItem value="es-ES">Spanish</SelectItem>
                      <SelectItem value="ja-JP">Japanese</SelectItem>
                      <SelectItem value="ko-KR">Korean</SelectItem>
                      <SelectItem value="zh-CN">Chinese (Simplified)</SelectItem>
                      <SelectItem value="zh-TW">Chinese (Traditional)</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-red-600 mt-2">
                    ⚠️ Vietnamese not supported by Adobe. Use Hybrid mode for Vietnamese.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Hybrid note */}
          {conversionMode === 'hybrid' && (
            <Alert className="bg-yellow-50 border-yellow-200">
              <AlertDescription>
                <p className="font-semibold mb-2">🌟 Hybrid Mode Active</p>
                <p className="text-sm">
                  This will automatically:
                </p>
                <ol className="text-sm mt-2 space-y-1 list-decimal list-inside">
                  <li>Use Gemini AI to extract Vietnamese text (98% accuracy)</li>
                  <li>Use Adobe to preserve images and layout (100%)</li>
                  <li>Combine both for perfect result</li>
                </ol>
                <p className="text-sm mt-2 text-gray-600">
                  Processing time: ~30-60 seconds for typical documents
                </p>
              </AlertDescription>
            </Alert>
          )}

          {/* Convert Button */}
          <Button
            onClick={handleConvert}
            disabled={!file || isProcessing}
            className="w-full"
            size="lg"
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                {conversionMode === 'hybrid' ? 'Processing hybrid approach...' : 'Converting...'}
              </>
            ) : (
              <>
                <Upload className="mr-2 h-5 w-5" />
                Convert PDF → Word
              </>
            )}
          </Button>

          {/* Result */}
          {result && (
            <Alert className={result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
              <AlertDescription>
                <div className="flex items-start gap-2">
                  {result.success ? (
                    <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-1" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-1" />
                  )}
                  <div className="flex-1">
                    <p className="font-semibold mb-2">{result.message}</p>
                    {result.success && (
                      <div className="text-sm text-gray-700 space-y-1">
                        <p>📄 File: {result.filename}</p>
                        <p>💾 Size: {result.size ? (result.size / 1024).toFixed(2) + ' KB' : 'N/A'}</p>
                        <p>🔧 Technology: {result.technology}</p>
                        {result.ocr !== undefined && <p>🔍 OCR: {result.ocr ? 'Enabled' : 'Disabled'}</p>}
                      </div>
                    )}
                    {!result.success && result.error && (
                      <div className="mt-2">
                        <p className="font-mono text-xs bg-red-100 p-2 rounded">{result.error}</p>
                      </div>
                    )}
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Technical Info */}
      <Card>
        <CardHeader>
          <CardTitle>Technical Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div>
              <strong className="text-blue-700">Adobe Mode:</strong> Direct call to <code>/api/v1/documents/convert/pdf-to-word-adobe-only</code>
            </div>
            <div>
              <strong className="text-green-700">pdf2docx Mode:</strong> Direct call to <code>/api/v1/documents/convert/pdf-to-word-pdf2docx-only</code>
            </div>
            <div>
              <strong className="text-yellow-700">Hybrid Mode:</strong> Direct call to <code>/api/v1/documents/convert/pdf-to-word-hybrid-vietnamese</code>
              <ul className="mt-2 ml-4 list-disc text-gray-600">
                <li>Step 1: Gemini AI extracts Vietnamese text from PDF</li>
                <li>Step 2: Adobe OCR creates searchable PDF with images preserved</li>
                <li>Step 3: Adobe exports to Word with layout intact</li>
                <li>Result: Perfect Vietnamese text + Perfect images/layout</li>
              </ul>
            </div>
            <div className="mt-4 p-3 bg-gray-100 rounded">
              <p className="font-semibold mb-2">Why Hybrid is Best for Vietnamese:</p>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>Adobe: NO Vietnamese OCR → English text only</li>
                <li>Gemini: Perfect Vietnamese → But loses images/layout</li>
                <li>Hybrid: Combines strengths → Perfect everything! ✅</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
