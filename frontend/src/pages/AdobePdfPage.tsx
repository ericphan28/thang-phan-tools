import { useState } from 'react';
import { Upload, FileText, Shield, Layers, Scissors, Lock, Eye, Sparkles, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import toast from 'react-hot-toast';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { TechnologyBadge } from '../components/TechnologyBadge';
import { AdobeFeatureGuide, HelpButton } from '../components/AdobeFeatureGuide';

const API_BASE = API_BASE_URL;

// Helper function to format error messages (async to handle Blob responses)
const getErrorMessage = async (error: any): Promise<string> => {
  // Handle Blob error responses (from responseType: 'blob')
  if (error.response?.data instanceof Blob) {
    try {
      const text = await error.response.data.text();
      const json = JSON.parse(text);
      if (json.detail) {
        return json.detail;
      }
    } catch (e) {
      // If parsing fails, fall through to generic messages
    }
  }
  
  // Handle JSON error responses
  const detail = error.response?.data?.detail;
  if (detail) {
    return detail;
  }
  
  // Fallback for other errors
  if (error.response?.status === 400) {
    return '❌ Yêu cầu không hợp lệ. Vui lòng kiểm tra lại thông tin.';
  } else if (error.response?.status === 429) {
    return '⏸️ Đã vượt quá giới hạn. Vui lòng thử lại sau.';
  } else if (error.response?.status === 500) {
    return '😔 Có lỗi xảy ra trên server. Vui lòng thử lại sau.';
  }
  
  return error.message || 'Đã có lỗi xảy ra';
};

// Helper to show error toast (handles async)
const showErrorToast = async (error: any) => {
  const errorMsg = await getErrorMessage(error);
  toast.error(errorMsg, { duration: 6000 });
};

export default function AdobePdfPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]); // For combine
  const [watermarkFile, setWatermarkFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentOperation, setCurrentOperation] = useState<string>('');
  
  // Form state
  const [pageRanges, setPageRanges] = useState<string>(''); // For split/combine
  const [password, setPassword] = useState<string>('');
  const [ownerPassword, setOwnerPassword] = useState<string>('');
  const [permissions, setPermissions] = useState<string[]>([]);
  const [generateReport, setGenerateReport] = useState<boolean>(true);
  
  // Document Generation state
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [jsonData, setJsonData] = useState<string>('');
  const [outputFormat, setOutputFormat] = useState<'pdf' | 'docx'>('pdf');
  const [batchMode, setBatchMode] = useState<boolean>(false);
  const [mergeOutput, setMergeOutput] = useState<boolean>(true);
  const [jsonFile, setJsonFile] = useState<File | null>(null);
  const [recordCount, setRecordCount] = useState<number>(0);
  
  // Electronic Seal state
  const [sealPdfFile, setSealPdfFile] = useState<File | null>(null);
  const [sealImageFile, setSealImageFile] = useState<File | null>(null);
  const [providerName, setProviderName] = useState<string>('');
  const [accessToken, setAccessToken] = useState<string>('');
  const [credentialId, setCredentialId] = useState<string>('');
  const [sealPin, setSealPin] = useState<string>('');
  const [sealVisible, setSealVisible] = useState<boolean>(true);

  // Help modal state
  const [showGuide, setShowGuide] = useState<boolean>(false);
  const [currentFeature, setCurrentFeature] = useState<string>('');

  const openGuide = (featureId: string) => {
    setCurrentFeature(featureId);
    setShowGuide(true);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleMultipleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleWatermarkChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setWatermarkFile(e.target.files[0]);
    }
  };

  const togglePermission = (perm: string) => {
    setPermissions(prev => 
      prev.includes(perm) 
        ? prev.filter(p => p !== perm)
        : [...prev, perm]
    );
  };

  const handleWatermark = async () => {
    if (!selectedFile || !watermarkFile) {
      toast.error('Vui lòng upload cả PDF gốc và PDF dấu mờ');
      return;
    }

    setLoading(true);
    setCurrentOperation('Đang đóng dấu mờ...');

    try {
      const formData = new FormData();
      formData.append('pdf_file', selectedFile);
      formData.append('watermark_file', watermarkFile);

      const response = await axios.post(`${API_BASE}/documents/pdf/watermark`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `watermarked_${selectedFile.name}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Đã đóng dấu mờ thành công!');
    } catch (error: any) {
      console.error('Watermark error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  const handleCombine = async () => {
    if (selectedFiles.length < 2) {
      toast.error('Vui lòng upload ít nhất 2 file PDF để gộp');
      return;
    }

    setLoading(true);
    setCurrentOperation('Đang gộp PDF...');

    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      if (pageRanges.trim()) {
        formData.append('page_ranges', pageRanges);
      }

      const response = await axios.post(`${API_BASE}/documents/pdf/combine`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'combined.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã gộp ${selectedFiles.length} file PDF!`);
    } catch (error: any) {
      console.error('Combine error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  const handleSplit = async () => {
    if (!selectedFile) {
      toast.error('Vui lòng upload file PDF');
      return;
    }

    if (!pageRanges.trim()) {
      toast.error('Vui lòng nhập khoảng trang cần tách (VD: 1-3,4-6,7-10)');
      return;
    }

    setLoading(true);
    setCurrentOperation('Đang tách PDF...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('page_ranges', pageRanges);

      const response = await axios.post(`${API_BASE}/documents/pdf/split`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `split_${selectedFile.name}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Đã tách PDF thành công!');
    } catch (error: any) {
      console.error('Split error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  const handleProtect = async () => {
    if (!selectedFile) {
      toast.error('Vui lòng upload file PDF');
      return;
    }

    if (!password.trim()) {
      toast.error('Vui lòng nhập mật khẩu');
      return;
    }

    setLoading(true);
    setCurrentOperation('Đang bảo vệ PDF...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('user_password', password);
      
      if (ownerPassword.trim()) {
        formData.append('owner_password', ownerPassword);
      }
      
      if (permissions.length > 0) {
        formData.append('permissions', permissions.join(','));
      }

      const response = await axios.post(`${API_BASE}/documents/pdf/protect`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `protected_${selectedFile.name}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('🔒 Đã bảo vệ PDF thành công!');
    } catch (error: any) {
      console.error('Protect error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  const handleLinearize = async () => {
    if (!selectedFile) {
      toast.error('Vui lòng upload file PDF');
      return;
    }

    setLoading(true);
    setCurrentOperation('Đang tối ưu PDF cho web...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`${API_BASE}/documents/pdf/linearize`, formData, {
        responseType: 'blob',
        onDownloadProgress: (progressEvent) => {
          // Show progress
        }
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `web_optimized_${selectedFile.name}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      const originalSize = response.headers['x-original-size'];
      const optimizedSize = response.headers['x-optimized-size'];

      toast.success(`⚡ Đã tối ưu PDF! Kích thước: ${(parseInt(optimizedSize) / 1024 / 1024).toFixed(2)}MB`);
    } catch (error: any) {
      console.error('Linearize error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  const handleAutoTag = async () => {
    if (!selectedFile) {
      toast.error('Vui lòng upload file PDF');
      return;
    }

    setLoading(true);
    setCurrentOperation('Đang gắn thẻ accessibility...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('generate_report', generateReport.toString());

      const response = await axios.post(`${API_BASE}/documents/pdf/autotag`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = generateReport ? `tagged_${selectedFile.name}.zip` : `tagged_${selectedFile.name}`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      if (generateReport) {
        toast.success('✅ Đã gắn thẻ + tạo báo cáo accessibility!');
      } else {
        toast.success('✅ Đã gắn thẻ PDF thành công!');
      }
    } catch (error: any) {
      console.error('AutoTag error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  const handleGenerateDocument = async () => {
    if (!templateFile) {
      toast.error('Vui lòng upload file template Word (.docx)');
      return;
    }
    
    if (!jsonData.trim()) {
      toast.error('Vui lòng nhập dữ liệu JSON');
      return;
    }
    
    // Validate JSON
    try {
      const parsed = JSON.parse(jsonData);
      
      // Validate structure based on mode
      if (batchMode) {
        if (!Array.isArray(parsed)) {
          toast.error('❌ Batch mode yêu cầu JSON phải là mảng [...]');
          return;
        }
        if (parsed.length === 0) {
          toast.error('❌ JSON array không được rỗng');
          return;
        }
        if (parsed.length > 100) {
          toast.error('❌ Tối đa 100 bản ghi mỗi batch');
          return;
        }
      } else {
        if (Array.isArray(parsed)) {
          toast.error('❌ Single mode yêu cầu JSON phải là object {...}, không phải array');
          return;
        }
      }
    } catch (e) {
      toast.error('Dữ liệu JSON không hợp lệ');
      return;
    }

    setLoading(true);
    setCurrentOperation(batchMode ? `Đang tạo ${recordCount} tài liệu...` : 'Đang tạo tài liệu...');

    try {
      const formData = new FormData();
      formData.append('template_file', templateFile);
      formData.append('json_data', jsonData);
      formData.append('output_format', outputFormat);

      let response;
      if (batchMode) {
        // Call batch endpoint
        formData.append('merge_output', mergeOutput.toString());
        response = await axios.post(`${API_BASE}/documents/pdf/generate-batch`, formData, {
          responseType: 'blob',
        });
      } else {
        // Call single endpoint
        response = await axios.post(`${API_BASE}/documents/pdf/generate`, formData, {
          responseType: 'blob',
        });
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      let filename;
      if (batchMode) {
        if (mergeOutput && outputFormat === 'pdf') {
          filename = `batch_${recordCount}_merged.pdf`;
        } else {
          // ZIP for both PDF separate and DOCX
          const ext = outputFormat === 'pdf' ? 'pdf' : 'docx';
          filename = `batch_${recordCount}_${ext}_files.zip`;
        }
      } else {
        const extension = outputFormat === 'pdf' ? 'pdf' : 'docx';
        filename = `generated_${templateFile.name.replace('.docx', `.${extension}`)}`;
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      if (batchMode) {
        if (mergeOutput && outputFormat === 'pdf') {
          toast.success(`✅ Đã tạo ${recordCount} tài liệu và gộp thành 1 PDF!`, { duration: 5000 });
        } else {
          const fileType = outputFormat === 'pdf' ? 'PDF' : 'Word';
          toast.success(`✅ Đã tạo ${recordCount} file ${fileType} riêng lẻ (ZIP)!`, { duration: 5000 });
        }
      } else {
        toast.success(`✅ Đã tạo tài liệu ${outputFormat.toUpperCase()} thành công!`);
      }
    } catch (error: any) {
      console.error('Document generation error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // Handle JSON file upload (for batch mode)
  const handleJsonFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setJsonFile(file);
      
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const content = event.target?.result as string;
          const parsed = JSON.parse(content);
          
          if (batchMode) {
            if (!Array.isArray(parsed)) {
              toast.error('❌ Batch mode yêu cầu JSON array');
              setJsonData('');
              setRecordCount(0);
              return;
            }
            setRecordCount(parsed.length);
          } else {
            if (Array.isArray(parsed)) {
              toast.error('❌ Single mode yêu cầu JSON object, không phải array');
              setJsonData('');
              return;
            }
            setRecordCount(1);
          }
          
          setJsonData(content);
          toast.success(batchMode ? `✅ Đã load ${parsed.length} bản ghi` : '✅ Đã load JSON');
        } catch (err) {
          toast.error('❌ File JSON không hợp lệ');
          setJsonData('');
          setRecordCount(0);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleElectronicSeal = async () => {
    if (!sealPdfFile) {
      toast.error('Vui lòng upload file PDF');
      return;
    }
    
    if (!providerName || !accessToken || !credentialId || !sealPin) {
      toast.error('Vui lòng nhập đầy đủ TSP credentials');
      return;
    }

    setLoading(true);
    setCurrentOperation('Đang ký số PDF...');

    try {
      const formData = new FormData();
      formData.append('pdf_file', sealPdfFile);
      if (sealImageFile) {
        formData.append('seal_image', sealImageFile);
      }
      formData.append('provider_name', providerName);
      formData.append('access_token', accessToken);
      formData.append('credential_id', credentialId);
      formData.append('pin', sealPin);
      formData.append('visible', sealVisible.toString());

      const response = await axios.post(`${API_BASE}/documents/pdf/seal`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sealed_${sealPdfFile.name}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Đã ký số PDF thành công!');
    } catch (error: any) {
      console.error('Electronic seal error:', error);
      await showErrorToast(error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-red-600" />
          Adobe PDF Services 
          <TechnologyBadge tech="adobe" />
        </h1>
        <p className="text-gray-600">
          Tính năng PDF cao cấp được hỗ trợ bởi Adobe AI - Chất lượng 10/10
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Watermark PDF */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('watermark')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Đóng Dấu Mờ (Watermark)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">File PDF Gốc:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">File PDF Dấu Mờ:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleWatermarkChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-purple-50 file:text-purple-700
                  hover:file:bg-purple-100"
              />
              <p className="text-xs text-gray-500 mt-1">
                Dấu mờ phải là file PDF (có thể tạo từ image)
              </p>
            </div>

            <Button
              onClick={handleWatermark}
              disabled={loading || !selectedFile || !watermarkFile}
              className="w-full"
            >
              {loading && currentOperation.includes('dấu mờ') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  Đóng Dấu Mờ
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Combine PDFs */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('combine')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-green-600" />
              Gộp PDF (Combine)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Chọn Nhiều File PDF:</label>
              <input
                type="file"
                accept=".pdf"
                multiple
                onChange={handleMultipleFilesChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-green-50 file:text-green-700
                  hover:file:bg-green-100"
              />
              {selectedFiles.length > 0 && (
                <p className="text-sm text-green-600 mt-1">
                  ✓ Đã chọn {selectedFiles.length} file(s)
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Page Ranges (Optional):
              </label>
              <input
                type="text"
                value={pageRanges}
                onChange={(e) => setPageRanges(e.target.value)}
                placeholder="all,1-3,all (cách nhau bởi dấu phẩy)"
                className="w-full px-3 py-2 border rounded-md"
              />
              <p className="text-xs text-gray-500 mt-1">
                Ví dụ: all,1-3,5-10 (all = toàn bộ trang)
              </p>
            </div>

            <Button
              onClick={handleCombine}
              disabled={loading || selectedFiles.length < 2}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              {loading && currentOperation.includes('gộp') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Layers className="w-4 h-4 mr-2" />
                  Gộp {selectedFiles.length} File
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Split PDF */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('split')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Scissors className="w-5 h-5 text-orange-600" />
              Tách PDF (Split)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">File PDF:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-orange-50 file:text-orange-700
                  hover:file:bg-orange-100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Khoảng Trang (Page Ranges):
              </label>
              <input
                type="text"
                value={pageRanges}
                onChange={(e) => setPageRanges(e.target.value)}
                placeholder="1-3,4-6,7-10"
                className="w-full px-3 py-2 border rounded-md"
              />
              <p className="text-xs text-gray-500 mt-1">
                Mỗi khoảng sẽ tạo 1 file riêng. Output: ZIP
              </p>
            </div>

            <Button
              onClick={handleSplit}
              disabled={loading || !selectedFile || !pageRanges.trim()}
              className="w-full bg-orange-600 hover:bg-orange-700"
            >
              {loading && currentOperation.includes('tách') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Scissors className="w-4 h-4 mr-2" />
                  Tách PDF
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Protect PDF */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('protect')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="w-5 h-5 text-red-600" />
              Bảo Mật PDF (Protect)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">File PDF:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-red-50 file:text-red-700
                  hover:file:bg-red-100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Mật Khẩu Người Dùng:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mật khẩu để mở file"
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Mật Khẩu Chủ Sở Hữu (Optional):</label>
              <input
                type="password"
                value={ownerPassword}
                onChange={(e) => setOwnerPassword(e.target.value)}
                placeholder="Mật khẩu để thay đổi quyền"
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Quyền Hạn:</label>
              <div className="space-y-2">
                {['print', 'copy', 'edit', 'fill_forms'].map(perm => (
                  <label key={perm} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={permissions.includes(perm)}
                      onChange={() => togglePermission(perm)}
                      className="rounded"
                    />
                    <span className="text-sm">{perm.replace('_', ' ').toUpperCase()}</span>
                  </label>
                ))}
              </div>
            </div>

            <Button
              onClick={handleProtect}
              disabled={loading || !selectedFile || !password.trim()}
              className="w-full bg-red-600 hover:bg-red-700"
            >
              {loading && currentOperation.includes('bảo vệ') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4 mr-2" />
                  Bảo Vệ PDF
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Linearize PDF */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('linearize')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5 text-purple-600" />
              Tối Ưu Web (Linearize)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">File PDF:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm font-semibold
                  file:bg-purple-50 file:text-purple-700
                  hover:file:bg-purple-100"
              />
            </div>

            <div className="p-3 bg-purple-50 border border-purple-200 rounded-md">
              <p className="text-sm text-purple-800">
                <strong>Fast Web Viewing:</strong> Tối ưu PDF để xem nhanh trên web. 
                Tải từng trang thay vì đợi cả file.
              </p>
            </div>

            <Button
              onClick={handleLinearize}
              disabled={loading || !selectedFile}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              {loading && currentOperation.includes('tối ưu') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4 mr-2" />
                  Tối Ưu PDF
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Auto-Tag PDF */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('autotag')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-600" />
              Accessibility (Auto-Tag)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">File PDF:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-50 file:text-indigo-700
                  hover:file:bg-indigo-100"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="generateReport"
                checked={generateReport}
                onChange={(e) => setGenerateReport(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="generateReport" className="text-sm">
                Tạo báo cáo accessibility (Excel)
              </label>
            </div>

            <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-md">
              <p className="text-sm text-indigo-800">
                <strong>WCAG Compliant:</strong> AI tự động gắn thẻ cấu trúc cho 
                screen reader. Tuân thủ Section 508.
              </p>
            </div>

            <Button
              onClick={handleAutoTag}
              disabled={loading || !selectedFile}
              className="w-full bg-indigo-600 hover:bg-indigo-700"
            >
              {loading && currentOperation.includes('gắn thẻ') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Gắn Thẻ PDF
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Document Generation */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('generate')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-teal-600" />
              Document Generation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Mode Toggle */}
            <div className="flex gap-2 p-1 bg-gray-100 rounded-lg">
              <button
                onClick={() => {
                  setBatchMode(false);
                  setJsonData('');
                  setRecordCount(0);
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  !batchMode
                    ? 'bg-white text-teal-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📄 Single Document
              </button>
              <button
                onClick={() => {
                  setBatchMode(true);
                  setJsonData('');
                  setRecordCount(0);
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  batchMode
                    ? 'bg-white text-teal-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📦 Batch Generation
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Template Word (.docx):</label>
              <input
                type="file"
                accept=".docx"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setTemplateFile(e.target.files[0]);
                  }
                }}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-teal-50 file:text-teal-700
                  hover:file:bg-teal-100"
              />
            </div>

            {/* JSON File Upload Option */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Upload JSON File {batchMode && '(Array required)'}:
              </label>
              <input
                type="file"
                accept=".json"
                onChange={handleJsonFileUpload}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-teal-50 file:text-teal-700
                  hover:file:bg-teal-100"
              />
              <p className="text-xs text-gray-500 mt-1">
                {batchMode 
                  ? 'Chọn file JSON chứa array: thiep_khai_truong_batch.json'
                  : 'Chọn file JSON chứa object: thiep_khai_truong_sample1.json'
                }
              </p>
            </div>

            {/* Or Manual JSON Input */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Hoặc nhập JSON thủ công:
              </label>
              <textarea
                value={jsonData}
                onChange={(e) => {
                  setJsonData(e.target.value);
                  // Try to parse and count records
                  try {
                    const parsed = JSON.parse(e.target.value);
                    if (batchMode && Array.isArray(parsed)) {
                      setRecordCount(parsed.length);
                    } else if (!batchMode && !Array.isArray(parsed)) {
                      setRecordCount(1);
                    }
                  } catch (err) {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder={
                  batchMode
                    ? '[\n  {"name": "Guest 1", "company": "ABC"},\n  {"name": "Guest 2", "company": "XYZ"}\n]'
                    : '{\n  "name": "John Doe",\n  "company": "ACME"\n}'
                }
                rows={batchMode ? 8 : 6}
                className="block w-full text-sm border border-gray-300 rounded-md p-2 font-mono"
              />
            </div>

            {/* Batch Info Display */}
            {batchMode && recordCount > 0 && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800 font-medium">
                  📊 Số lượng bản ghi: <strong>{recordCount}</strong>
                </p>
              </div>
            )}

            {/* Batch Options */}
            {batchMode && (
              <div className="p-4 bg-teal-50 border border-teal-200 rounded-md space-y-3">
                <p className="text-sm font-semibold text-teal-900">⚙️ Batch Options:</p>
                
                {/* PDF Options */}
                {outputFormat === 'pdf' && (
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={mergeOutput}
                      onChange={(e) => setMergeOutput(e.target.checked)}
                      className="mt-1 rounded"
                    />
                    <div>
                      <span className="text-sm font-medium text-teal-900">
                        🔗 Gộp tất cả thành 1 file PDF
                      </span>
                      <p className="text-xs text-teal-700 mt-1">
                        {mergeOutput 
                          ? `✅ Tạo 1 file PDF duy nhất với ${recordCount} trang (1 trang = 1 bản ghi)`
                          : `📦 Tạo ${recordCount} file PDF riêng lẻ trong 1 file ZIP`
                        }
                      </p>
                    </div>
                  </label>
                )}

                {/* DOCX Options */}
                {outputFormat === 'docx' && (
                  <div className="flex items-start gap-3">
                    <div className="mt-1 text-blue-600">📦</div>
                    <div>
                      <span className="text-sm font-medium text-teal-900">
                        File ZIP với {recordCount} file DOCX riêng lẻ
                      </span>
                      <p className="text-xs text-teal-700 mt-1">
                        ✅ Mỗi bản ghi sẽ tạo thành 1 file Word riêng
                      </p>
                      <p className="text-xs text-teal-600 mt-1">
                        💡 Merge không khả dụng cho Word (chỉ PDF)
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">Định dạng output:</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="outputFormat"
                    value="pdf"
                    checked={outputFormat === 'pdf'}
                    onChange={() => setOutputFormat('pdf')}
                    className="rounded"
                  />
                  <span className="text-sm">PDF</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="outputFormat"
                    value="docx"
                    checked={outputFormat === 'docx'}
                    onChange={() => {
                      setOutputFormat('docx');
                      if (batchMode) setMergeOutput(false); // Disable merge for DOCX
                    }}
                    className="rounded"
                  />
                  <span className="text-sm">Word (.docx)</span>
                </label>
              </div>
            </div>

            <div className="p-3 bg-teal-50 border border-teal-200 rounded-md">
              <p className="text-sm text-teal-800">
                <strong>Template syntax:</strong> {'{{variable}}'} cho biến đơn, 
                {'{{#array}}...{{/array}}'} cho vòng lặp
              </p>
              {batchMode && (
                <p className="text-sm text-teal-800 mt-2">
                  <strong>Batch mode:</strong> Mỗi object trong array sẽ tạo 1 tài liệu riêng
                </p>
              )}
            </div>

            <Button
              onClick={handleGenerateDocument}
              disabled={loading || !templateFile || !jsonData.trim()}
              className="w-full bg-teal-600 hover:bg-teal-700"
            >
              {loading && currentOperation.includes('tài liệu') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {currentOperation}
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  {batchMode 
                    ? `Tạo ${recordCount > 0 ? recordCount : ''} Tài Liệu` 
                    : 'Tạo Tài Liệu'
                  }
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Electronic Seal */}
        <Card className="relative">
          <HelpButton onClick={() => openGuide('seal')} />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-amber-600" />
              Electronic Seal (Chữ Ký Số)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">File PDF:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSealPdfFile(e.target.files[0]);
                  }
                }}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-amber-50 file:text-amber-700
                  hover:file:bg-amber-100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Seal Image (PNG/JPG - Tùy chọn):</label>
              <input
                type="file"
                accept=".png,.jpg,.jpeg"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSealImageFile(e.target.files[0]);
                  }
                }}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-amber-50 file:text-amber-700
                  hover:file:bg-amber-100"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium mb-1">Provider Name:</label>
                <input
                  type="text"
                  value={providerName}
                  onChange={(e) => setProviderName(e.target.value)}
                  placeholder="GlobalSign, DigiCert..."
                  className="w-full text-sm border border-gray-300 rounded-md p-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Credential ID:</label>
                <input
                  type="text"
                  value={credentialId}
                  onChange={(e) => setCredentialId(e.target.value)}
                  placeholder="Your credential ID"
                  className="w-full text-sm border border-gray-300 rounded-md p-2"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Access Token:</label>
              <input
                type="password"
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                placeholder="Your TSP access token"
                className="w-full text-sm border border-gray-300 rounded-md p-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">PIN:</label>
              <input
                type="password"
                value={sealPin}
                onChange={(e) => setSealPin(e.target.value)}
                placeholder="Your PIN"
                className="w-full text-sm border border-gray-300 rounded-md p-2"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="sealVisible"
                checked={sealVisible}
                onChange={(e) => setSealVisible(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="sealVisible" className="text-sm">
                Chữ ký hiển thị (visible seal)
              </label>
            </div>

            <div className="p-3 bg-amber-50 border border-amber-200 rounded-md">
              <p className="text-sm text-amber-800">
                <strong>⚠️ Enterprise Feature:</strong> Cần TSP (Trust Service Provider) 
                credentials. Liên hệ GlobalSign, DigiCert để đăng ký.
              </p>
            </div>

            <Button
              onClick={handleElectronicSeal}
              disabled={loading || !sealPdfFile || !providerName || !accessToken || !credentialId || !sealPin}
              className="w-full bg-amber-600 hover:bg-amber-700"
            >
              {loading && currentOperation.includes('ký số') ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Đang ký số...
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4 mr-2" />
                  Ký Số PDF
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Adobe Info Banner */}
      <Card className="mt-6 border-red-200 bg-gradient-to-r from-red-50 to-pink-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-900 mb-2">
                Adobe PDF Services - Chất Lượng 10/10
              </h3>
              <p className="text-sm text-red-800 mb-3">
                Được hỗ trợ bởi Adobe Sensei AI - Công nghệ xử lý PDF hàng đầu thế giới.
                Tất cả các tính năng trên đều sử dụng Adobe PDF Services API.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-white rounded-full text-xs font-medium text-red-700 border border-red-200">
                  ✓ Chất lượng cao nhất
                </span>
                <span className="px-3 py-1 bg-white rounded-full text-xs font-medium text-red-700 border border-red-200">
                  ✓ AI-powered
                </span>
                <span className="px-3 py-1 bg-white rounded-full text-xs font-medium text-red-700 border border-red-200">
                  ✓ Enterprise-grade
                </span>
                <span className="px-3 py-1 bg-white rounded-full text-xs font-medium text-red-700 border border-red-200">
                  ✓ 500 giao dịch miễn phí/tháng
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Feature Guide Modal */}
      <AdobeFeatureGuide 
        open={showGuide}
        onClose={() => setShowGuide(false)}
        featureId={currentFeature}
      />
    </div>
  );
}
