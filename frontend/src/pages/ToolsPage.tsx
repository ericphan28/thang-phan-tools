import { useState } from 'react';
import { Upload, FileText, Image, FileType, Loader2, Settings, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import toast from 'react-hot-toast';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { TechnologyBadge, ConversionProgress, ConversionResult, type TechnologyType } from '../components/TechnologyBadge';
import SettingsPanel from '../components/SettingsPanel';
import { GeminiModelSelector } from '../components/GeminiModelSelector';

// API Base URL with /v1 prefix - Updated 2025-11-24
const API_BASE = API_BASE_URL;

// Debug: Log API base URL on component load
console.log('🔧 ToolsPage API_BASE:', API_BASE);
console.log('🔧 Expected: /api/v1');

// Operations database for search and display - NEW
const ALL_OPERATIONS = [
  // Popular operations
  { id: 'word-to-pdf', name: 'Word to PDF', icon: '📝', category: 'convert', keywords: ['word', 'docx', 'pdf', 'convert'], tech: 'gotenberg', popular: true, color: 'blue' },
  { id: 'pdf-to-word', name: 'PDF to Word', icon: '📄', category: 'convert', keywords: ['pdf', 'word', 'docx', 'convert', 'editable'], tech: 'gemini', popular: true, color: 'blue' },
  { id: 'merge-pdf', name: 'Merge PDFs', icon: '🔗', category: 'edit', keywords: ['merge', 'combine', 'join', 'pdf'], tech: 'pypdf', popular: true, color: 'green' },
  { id: 'compress-pdf', name: 'Compress PDF', icon: '🗜️', category: 'edit', keywords: ['compress', 'reduce', 'size', 'optimize', 'pdf'], tech: 'adobe', popular: true, color: 'green' },
  
  // Convert operations
  { id: 'excel-to-pdf', name: 'Excel to PDF', icon: '📊', category: 'convert', keywords: ['excel', 'xlsx', 'pdf', 'convert'], tech: 'gotenberg', color: 'blue' },
  { id: 'image-to-pdf', name: 'Image to PDF', icon: '🖼️', category: 'convert', keywords: ['image', 'photo', 'jpg', 'png', 'pdf', 'convert'], tech: 'pypdf', color: 'blue' },
  { id: 'html-to-pdf', name: 'HTML to PDF', icon: '🌐', category: 'convert', keywords: ['html', 'web', 'pdf', 'convert'], tech: 'reportlab', color: 'blue' },
  
  // Edit operations
  { id: 'split-pdf', name: 'Split PDF', icon: '✂️', category: 'edit', keywords: ['split', 'separate', 'extract', 'pages', 'pdf'], tech: 'pypdf', color: 'green' },
  { id: 'rotate-pdf', name: 'Rotate PDF', icon: '🔄', category: 'edit', keywords: ['rotate', 'turn', 'orientation', 'pdf'], tech: 'pypdf', color: 'green' },
  { id: 'watermark-pdf', name: 'Add Watermark', icon: '🏷️', category: 'edit', keywords: ['watermark', 'stamp', 'label', 'pdf'], tech: 'reportlab', color: 'green' },
  { id: 'protect-pdf', name: 'Password Protect', icon: '🔒', category: 'edit', keywords: ['password', 'protect', 'secure', 'lock', 'pdf'], tech: 'pypdf', color: 'green' },
  { id: 'pdf-to-images', name: 'PDF to Images', icon: '🖼️', category: 'convert', keywords: ['pdf', 'image', 'jpg', 'png', 'extract'], tech: 'pypdfium2', color: 'blue' },
  { id: 'page-numbers', name: 'Add Page Numbers', icon: '🔢', category: 'edit', keywords: ['page', 'numbers', 'numbering', 'pdf'], tech: 'reportlab', color: 'green' },
  
  // Batch operations
  { id: 'batch-word-to-pdf', name: 'Batch Word→PDF', icon: '📚', category: 'batch', keywords: ['batch', 'multiple', 'word', 'pdf', 'bulk'], tech: 'gotenberg', color: 'purple' },
  { id: 'batch-compress', name: 'Batch Compress', icon: '📦', category: 'batch', keywords: ['batch', 'compress', 'multiple', 'bulk', 'pdf'], tech: 'adobe', color: 'purple' },
  { id: 'merge-word-to-pdf', name: 'Merge Word→PDF', icon: '🔗', category: 'batch', keywords: ['merge', 'word', 'pdf', 'combine', 'join'], tech: 'gotenberg', color: 'purple' },
  
  // OCR operations
  { id: 'ocr-extract', name: 'Extract Text (OCR)', icon: '🔍', category: 'ocr', keywords: ['ocr', 'text', 'extract', 'scan', 'recognize'], tech: 'tesseract', color: 'orange' },
  { id: 'ocr-vietnamese', name: 'OCR Vietnamese', icon: '🇻🇳', category: 'ocr', keywords: ['ocr', 'vietnamese', 'tieng viet', 'text', 'extract'], tech: 'tesseract', color: 'orange' },
  { id: 'pdf-extract-text', name: 'Extract PDF Text', icon: '📝', category: 'ocr', keywords: ['pdf', 'text', 'extract', 'content'], tech: 'pypdf', color: 'orange' },
];

export default function ToolsPage() {
  // Search functionality - NEW
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showSearchResults, setShowSearchResults] = useState<boolean>(false);
  
  const [activeTab, setActiveTab] = useState<'documents' | 'images' | 'ocr' | 'settings'>('documents');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [processingTime, setProcessingTime] = useState<number>(0);
  
  // Technology tracking
  const [currentTechnology, setCurrentTechnology] = useState<TechnologyType | null>(null);
  
  // Progress tracking - IMPROVED: Track specific operation
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [processingProgress, setProcessingProgress] = useState<number>(0);
  const [currentOperation, setCurrentOperation] = useState<string>('');
  const [loadingOperation, setLoadingOperation] = useState<string | null>(null); // NEW: Track which operation is running
  const [abortController, setAbortController] = useState<AbortController | null>(null); // NEW: For canceling operations
  
  // Multi-file upload for Merge PDFs
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  
  // Batch conversion mode
  const [batchMode, setBatchMode] = useState<boolean>(false);
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [batchOperation, setBatchOperation] = useState<'word-to-pdf' | 'pdf-to-word' | 'excel-to-pdf' | 'image-to-pdf' | 'compress-pdf' | 'bulk-pdf' | 'merge-word-to-pdf' | null>(null);
  const [bulkFormat, setBulkFormat] = useState<'word' | 'excel' | 'image'>('word'); // For bulk PDF conversion
  const [isDraggingBatch, setIsDraggingBatch] = useState<boolean>(false); // For drag visual feedback
  const [draggedBatchIndex, setDraggedBatchIndex] = useState<number | null>(null); // For batch file reordering
  
  // PDF Operations state
  const [pdfOperation, setPdfOperation] = useState<'merge' | 'split' | 'rotate' | 'watermark' | 'protect' | 'unlock' | 'to-images' | 'page-numbers' | null>(null);
  const [pageRanges, setPageRanges] = useState<string>(''); // For split: "1-3,5-7"
  const [rotationAngle, setRotationAngle] = useState<number>(90); // For rotate: 90, 180, 270
  const [specificPages, setSpecificPages] = useState<string>(''); // For rotate: "1,3,5" or empty for all
  
  // Advanced PDF Operations state
  const [watermarkText, setWatermarkText] = useState<string>(''); // For watermark
  const [watermarkPosition, setWatermarkPosition] = useState<string>('center');
  const [password, setPassword] = useState<string>(''); // For protect/unlock
  const [imageFormat, setImageFormat] = useState<string>('png'); // For to-images
  const [pageNumberFormat, setPageNumberFormat] = useState<string>('Page {page}');

  // NEW: Adobe-only features state
  const [showOcrModal, setShowOcrModal] = useState<boolean>(false);
  const [ocrLanguage, setOcrLanguage] = useState<string>('vi-VN');
  const [enableOcr, setEnableOcr] = useState<boolean>(false);
  const [autoDetectScanned, setAutoDetectScanned] = useState<boolean>(true);
  const [showPdfToWordModal, setShowPdfToWordModal] = useState<boolean>(false); // NEW: For PDF→Word OCR options
  const [useGemini, setUseGemini] = useState<boolean>(true); // NEW: Use Gemini API by default (best for Vietnamese)
  const [geminiModel, setGeminiModel] = useState<string>(''); // NEW: Selected Gemini model (empty = use default)
  const [showExtractModal, setShowExtractModal] = useState<boolean>(false);
  const [extractType, setExtractType] = useState<string>('all');
  const [showHtmlToPdfModal, setShowHtmlToPdfModal] = useState<boolean>(false);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [htmlPageSize, setHtmlPageSize] = useState<string>('A4');
  const [htmlOrientation, setHtmlOrientation] = useState<string>('portrait');

  // Helper: Get file extension
  const getFileExtension = (filename: string): string => {
    return filename.split('.').pop()?.toLowerCase() || '';
  };

  // Helper: Get file type category
  const getFileType = (file: File | null): 'word' | 'excel' | 'powerpoint' | 'pdf' | 'image' | null => {
    if (!file) return null;
    const ext = getFileExtension(file.name);
    
    if (['doc', 'docx'].includes(ext)) return 'word';
    if (['xls', 'xlsx'].includes(ext)) return 'excel';
    if (['ppt', 'pptx'].includes(ext)) return 'powerpoint';
    if (ext === 'pdf') return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'heic'].includes(ext)) return 'image';
    
    return null;
  };

  // Helper: Check if a specific operation is running
  const isOperationLoading = (operation: string): boolean => {
    return loadingOperation === operation;
  };

  // Helper: Check if ANY operation is running
  const isAnyOperationLoading = (): boolean => {
    return loadingOperation !== null;
  };

  // Helper: Check if file is PDF
  const isPdfSelected = (): boolean => {
    return selectedFile !== null && getFileType(selectedFile) === 'pdf';
  };

  // Helper: Check if file is uploaded
  const isFileSelected = (): boolean => {
    return selectedFile !== null;
  };

  // NEW: Search operations filter
  const filterOperations = (query: string) => {
    if (!query.trim()) return [];
    
    const searchLower = query.toLowerCase();
    return ALL_OPERATIONS.filter(op => 
      op.name.toLowerCase().includes(searchLower) ||
      op.keywords.some(keyword => keyword.includes(searchLower)) ||
      op.category.includes(searchLower)
    ).slice(0, 8); // Limit to 8 results
  };

  // NEW: Get popular operations
  const getPopularOperations = () => {
    return ALL_OPERATIONS.filter(op => op.popular);
  };

  // NEW: Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    setShowSearchResults(query.trim().length > 0);
  };

  // NEW: Handle operation selection from search
  const handleOperationSelect = (operationId: string) => {
    setSearchQuery('');
    setShowSearchResults(false);
    toast.success(`Selected: ${operationId}`, { icon: '🎯' });
    // TODO: Trigger the actual operation
  };

  // Helper: Validate file before processing
  const validateFile = (file: File | null, requiredType?: 'pdf' | 'word' | 'excel' | 'image'): {
    valid: boolean;
    error?: string;
  } => {
    if (!file) {
      return { valid: false, error: 'Vui lòng upload file trước' };
    }

    // Check file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      return {
        valid: false,
        error: `File quá lớn (${(file.size / 1024 / 1024).toFixed(2)}MB). Tối đa 50MB.`
      };
    }

    // Check file type if specified
    if (requiredType) {
      const fileType = getFileType(file);
      if (fileType !== requiredType) {
        return {
          valid: false,
          error: `File không đúng định dạng. Cần ${requiredType.toUpperCase()}, bạn upload ${fileType?.toUpperCase() || 'UNKNOWN'}.`
        };
      }
    }

    return { valid: true };
  };

  // Helper: Get button disabled state with reason
  const getButtonState = (requiredFileType?: 'pdf' | 'word' | 'excel' | 'image'): {
    disabled: boolean;
    reason: string | null;
  } => {
    // Operation đang chạy
    if (isAnyOperationLoading()) {
      return { disabled: true, reason: 'Đang xử lý thao tác khác...' };
    }

    // Check file requirements
    const validation = validateFile(selectedFile, requiredFileType);
    if (!validation.valid) {
      return { disabled: true, reason: validation.error || null };
    }

    return { disabled: false, reason: null };
  };

  // Cancel current operation
  const handleCancelOperation = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setLoadingOperation(null);
      setLoading(false);
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
      toast('❌ Đã hủy thao tác!', { icon: 'ℹ️' });
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleMultipleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...newFiles]);
      setSelectedFile(newFiles[0]); // Store first file for display
      setResult(null);
    }
  };

  // Drag & Drop handlers for file reordering
  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    e.preventDefault();
    
    if (draggedIndex === null || draggedIndex === index) return;

    // Reorder files
    const newFiles = [...selectedFiles];
    const draggedFile = newFiles[draggedIndex];
    newFiles.splice(draggedIndex, 1);
    newFiles.splice(index, 0, draggedFile);
    
    setSelectedFiles(newFiles);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const moveFile = (fromIndex: number, toIndex: number) => {
    if (toIndex < 0 || toIndex >= selectedFiles.length) return;
    
    const newFiles = [...selectedFiles];
    const [movedFile] = newFiles.splice(fromIndex, 1);
    newFiles.splice(toIndex, 0, movedFile);
    setSelectedFiles(newFiles);
  };

  // Batch file reordering handlers
  const handleBatchDragStart = (index: number) => {
    setDraggedBatchIndex(index);
  };

  const handleBatchDragOver = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    e.preventDefault();
    
    if (draggedBatchIndex === null || draggedBatchIndex === index) return;

    // Reorder batch files
    const newFiles = [...batchFiles];
    const draggedFile = newFiles[draggedBatchIndex];
    newFiles.splice(draggedBatchIndex, 1);
    newFiles.splice(index, 0, draggedFile);
    
    setBatchFiles(newFiles);
    setDraggedBatchIndex(index);
  };

  const handleBatchDragEnd = () => {
    setDraggedBatchIndex(null);
  };

  const moveBatchFile = (fromIndex: number, toIndex: number) => {
    if (toIndex < 0 || toIndex >= batchFiles.length) return;
    
    const newFiles = [...batchFiles];
    const [movedFile] = newFiles.splice(fromIndex, 1);
    newFiles.splice(toIndex, 0, movedFile);
    setBatchFiles(newFiles);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setResult(null);
    }
  };

  /**
   * 🚀 UNIFIED CONVERSION HANDLER - Reuse logic for ALL operations
   * This replaces 500+ lines of duplicate code across different handlers
   */
  const handleConversion = async (options: {
    operation: string;
    endpoint: string;
    file: File;
    additionalData?: Record<string, any>;
    outputFilename?: string;
    technology: TechnologyType;
    validateFileType?: 'pdf' | 'word' | 'excel' | 'image';
    responseType?: 'blob' | 'json';
  }) => {
    const {
      operation,
      endpoint,
      file,
      additionalData,
      outputFilename,
      technology,
      validateFileType,
      responseType = 'blob'
    } = options;

    // Check if another operation is running
    if (isAnyOperationLoading()) {
      toast.error('⚠️ Một thao tác khác đang chạy. Vui lòng đợi!');
      return;
    }

    // Validate file
    const validation = validateFile(file, validateFileType);
    if (!validation.valid) {
      toast.error(validation.error || 'File không hợp lệ');
      return;
    }

    // Initialize
    const controller = new AbortController();
    setAbortController(controller);
    setLoading(true);
    setLoadingOperation(operation.toLowerCase().replace(/\s+/g, '-'));
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation(operation);
    setCurrentTechnology(technology);

    const startTime = Date.now();

    // Upload progress simulation
    const uploadInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 100));
    }, 100);

    try {
      // Time tracking interval
      const timeInterval = setInterval(() => {
        setProcessingTime(Date.now() - startTime);
      }, 100);

      // Prepare form data
      const formData = new FormData();
      formData.append('file', file);

      // Add additional data if provided
      if (additionalData) {
        Object.entries(additionalData).forEach(([key, value]) => {
          formData.append(key, String(value));
        });
      }

      // Make API request
      const response = await axios.post(
        `${API_BASE}${endpoint}`,
        formData,
        {
          responseType: responseType,
          signal: controller.signal,
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(percentCompleted);
            }
          },
        }
      );

      clearInterval(uploadInterval);
      clearInterval(timeInterval);

      setUploadProgress(100);

      // Processing progress animation
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const processingTimeMs = Date.now() - startTime;

      // Handle different response types
      if (responseType === 'json') {
        // JSON response (for extract text, pdf info, etc.)
        const techEngine = response.data.technology || technology;
        const techQuality = response.data.quality || '10/10';

        setResult({
          success: true,
          operation,
          technology: techEngine,
          quality: techQuality,
          processingTime: processingTimeMs,
          data: response.data,
        });

        toast.success(`✅ ${operation} thành công!`);
      } else {
        // Blob response (for file downloads)
        const techEngine = response.headers['x-technology-engine'] || technology;
        const techQuality = response.headers['x-technology-quality'] || '10/10';
        const outputSize = response.data.size;

        // Download file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.download = outputFilename || `output_${Date.now()}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        setResult({
          success: true,
          operation,
          technology: techEngine,
          quality: techQuality,
          processingTime: processingTimeMs,
          originalSize: file.size,
          outputSize: outputSize,
        });

        toast.success(`✅ ${operation} thành công! File đã được tải về.`);
      }

    } catch (error: any) {
      clearInterval(uploadInterval);

      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        toast('❌ Đã hủy thao tác', { icon: 'ℹ️' });
      } else {
        // Better error messages
        let errorMsg = 'Lỗi không xác định';
        
        if (error.code === 'ECONNABORTED') {
          errorMsg = 'Timeout! File quá lớn hoặc mạng chậm.';
        } else if (error.code === 'ERR_NETWORK') {
          errorMsg = 'Lỗi kết nối. Vui lòng kiểm tra mạng.';
        } else if (error.response?.status === 413) {
          errorMsg = 'File quá lớn! Server không chấp nhận.';
        } else if (error.response?.status === 415) {
          errorMsg = 'Định dạng file không được hỗ trợ.';
        } else if (error.response?.status === 500) {
          errorMsg = error.response?.data?.detail || 'Lỗi server. Vui lòng thử lại.';
        } else {
          errorMsg = error.response?.data?.detail || error.message || errorMsg;
        }

        console.error('Conversion error:', error);
        toast.error(`❌ ${errorMsg}`);
        
        setResult({
          success: false,
          operation,
          error: errorMsg,
        });
      }
    } finally {
      setLoadingOperation(null);
      setLoading(false);
      setAbortController(null);
      setUploadProgress(0);
      setProcessingProgress(0);
    }
  };

  // Document: Word to PDF
  const handleWordToPdf = async () => {
    if (!selectedFile) {
      toast.error('❌ Vui lòng upload file Word trước!');
      return;
    }

    await handleConversion({
      operation: 'Word → PDF',
      endpoint: '/documents/convert/word-to-pdf',
      file: selectedFile,
      outputFilename: selectedFile.name.replace(/\.(docx?|doc)$/i, '.pdf'),
      technology: 'gotenberg',
      validateFileType: 'word',
    });
  };

  // Document: PDF to Word
  const handlePdfToWord = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation('PDF → Word');
    setCurrentTechnology(useGemini ? 'gemini' : 'adobe'); // Set technology being used
    const startTime = Date.now();
    
    const uploadInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 100));
    }, 100);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('enable_ocr', String(enableOcr));
    formData.append('ocr_language', ocrLanguage);
    formData.append('auto_detect_scanned', String(autoDetectScanned));
    formData.append('use_gemini', String(useGemini)); // NEW: Gemini API support
    if (useGemini && geminiModel) {
      formData.append('gemini_model', geminiModel); // NEW: Model selection
    }

    try {
      const timeInterval = setInterval(() => {
        setProcessingTime(Date.now() - startTime);
      }, 100);
      
      const response = await axios.post(`${API_BASE}/documents/convert/pdf-to-word`, formData, {
        responseType: 'blob',
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        },
      });

      clearInterval(uploadInterval);
      clearInterval(timeInterval);
      
      setUploadProgress(100);
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const processingTimeMs = Date.now() - startTime;
      const docxSize = response.data.size;
      const originalSize = selectedFile.size;

      // Extract technology metadata from response headers
      const techEngine = response.headers['x-technology-engine'] || 'pdf2docx';
      const techName = response.headers['x-technology-name'] || 'pdf2docx';
      const techModel = response.headers['x-technology-model'] || '';
      const techQuality = response.headers['x-technology-quality'] || '7/10';
      const techSpeed = response.headers['x-technology-speed'] || '';
      const techQuota = response.headers['x-adobe-quota-remaining'] || null;
      const usedOcr = response.headers['x-technology-ocr'] === 'true';
      const ocrLang = response.headers['x-technology-ocr-language'] || 'none';

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace(/\.\w+$/, '.docx');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      const successMsg = usedOcr 
        ? `✅ Converted to Word with OCR (${ocrLang})!`
        : techModel
        ? `✅ Converted with ${techName} (${techModel})!`
        : '✅ Converted to Word successfully!';
      toast.success(successMsg);
      
      setResult({
        type: 'download',
        action: 'PDF → Word Conversion' + (usedOcr ? ` (OCR: ${ocrLang})` : ''),
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: docxSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - docxSize / originalSize) * 100).toFixed(1),
        downloadUrl: url,
        technology: techEngine,
        quality: techQuality,
        quotaRemaining: techQuota
      });
    } catch (error: any) {
      clearInterval(uploadInterval);
      const errorMsg = error.response?.data?.detail || 'PDF to Word conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
      setCurrentTechnology(null);
      // Reset OCR modal
      setShowOcrModal(false);
    }
  };

  // Document: PDF to Excel
  const handlePdfToExcel = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation('PDF → Excel');
    setCurrentTechnology('pdfplumber'); // Set technology
    const startTime = Date.now();
    
    // Simulate upload progress
    const uploadInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(uploadInterval);
          return 100;
        }
        return prev + 10;
      });
    }, 100);
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Update processing time every 100ms
      const timeInterval = setInterval(() => {
        setProcessingTime(Date.now() - startTime);
      }, 100);
      
      const response = await axios.post(`${API_BASE}/documents/convert/pdf-to-excel`, formData, {
        responseType: 'blob',
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        },
      });
      
      clearInterval(uploadInterval);
      clearInterval(timeInterval);

      // Simulate processing progress
      setUploadProgress(100);
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const processingTimeMs = Date.now() - startTime;
      const xlsxSize = response.data.size;
      const originalSize = selectedFile.size;

      // Extract technology metadata from response headers
      const techEngine = response.headers['x-technology-engine'] || 'pdfplumber';
      const techQuality = response.headers['x-technology-quality'] || '8/10';

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace(/\.\w+$/, '.xlsx');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Converted to Excel successfully!');
      setResult({
        type: 'download',
        action: 'PDF → Excel Conversion',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: xlsxSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - xlsxSize / originalSize) * 100).toFixed(1),
        downloadUrl: url,
        technology: techEngine,
        quality: techQuality,
        quotaRemaining: null
      });
    } catch (error: any) {
      clearInterval(uploadInterval);
      const errorMsg = error.response?.data?.detail || 'PDF to Excel conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
      setCurrentTechnology(null);
    }
  };

  // Document: Extract PDF Text
  const handleExtractPdfText = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/extract-text`, formData);
      const processingTimeMs = Date.now() - startTime;

      toast.success('✅ Text extracted successfully!');
      setResult({
        type: 'text',
        action: 'PDF Text Extraction',
        originalFile: selectedFile.name,
        processingTime: processingTimeMs,
        data: {
          text: response.data.text,
          num_pages: response.data.num_pages,
          word_count: response.data.word_count,
          char_count: response.data.char_count
        }
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Text extraction failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Document: Excel to PDF
  const handleExcelToPdf = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE}/documents/convert/excel-to-pdf`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const pdfSize = response.data.size;
      const originalSize = selectedFile.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace(/\.\w+$/, '.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Excel converted to PDF!');
      setResult({
        type: 'download',
        action: 'Excel → PDF Conversion',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: pdfSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - pdfSize / originalSize) * 100).toFixed(1),
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Excel to PDF conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Document: PowerPoint to PDF
  const handlePowerPointToPdf = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE}/documents/convert/powerpoint-to-pdf`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const pdfSize = response.data.size;
      const originalSize = selectedFile.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace(/\.\w+$/, '.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ PowerPoint converted to PDF!');
      setResult({
        type: 'download',
        action: 'PowerPoint → PDF Conversion',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: pdfSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - pdfSize / originalSize) * 100).toFixed(1),
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'PowerPoint to PDF conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Document: PDF Info
  const handlePdfInfo = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE}/documents/info/pdf`, formData);
      const processingTimeMs = Date.now() - startTime;

      toast.success('✅ PDF info retrieved!');
      setResult({
        type: 'info',
        action: 'PDF Information',
        originalFile: selectedFile.name,
        processingTime: processingTimeMs,
        data: response.data
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to get PDF info';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Image: Resize
  const handleImageResize = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('width', '800');
    formData.append('keep_aspect_ratio', 'true');
    formData.append('output_format', 'png');

    try {
      const response = await axios.post(`${API_BASE}/images/resize`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const resizedSize = response.data.size;
      const originalSize = selectedFile.size;

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace(/\.\w+$/, '_resized.png');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Resized successfully!');
      setResult({
        type: 'download',
        action: 'Image Resize',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: resizedSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - resizedSize / originalSize) * 100).toFixed(1),
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Resize failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Image: Remove Background
  const handleRemoveBackground = async () => {
    if (!selectedFile) return;

    setLoading(true);
    toast.loading('AI processing... (may take 10-30 seconds)');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('output_format', 'png');

    try {
      const response = await axios.post(`${API_BASE}/images/remove-background`, formData, {
        responseType: 'blob',
      });

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', selectedFile.name.replace(/\.\w+$/, '_no_bg.png'));
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.dismiss();
      toast.success('Background removed!');
      setResult({ type: 'download', filename: selectedFile.name.replace(/\.\w+$/, '_no_bg.png') });
    } catch (error: any) {
      toast.dismiss();
      toast.error(error.response?.data?.detail || 'Failed to remove background');
    } finally {
      setLoading(false);
    }
  };

  // OCR: Extract Text
  const handleOCR = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('languages', 'vi,en');
    formData.append('detail', '1');

    try {
      const response = await axios.post(`${API_BASE}/ocr/extract`, formData);

      setResult({ type: 'text', data: response.data });
      toast.success('Text extracted successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'OCR failed');
    } finally {
      setLoading(false);
    }
  };

  // PDF: Compress
  const handleCompressPdf = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('quality', 'medium');

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/compress`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const compressedSize = response.data.size;
      const originalSize = selectedFile.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace('.pdf', '_compressed.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ PDF compressed successfully!');
      setResult({
        type: 'download',
        action: 'PDF Compression',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: compressedSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - compressedSize / originalSize) * 100).toFixed(1),
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'PDF compression failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Image: Convert to PDF
  const handleImageToPdf = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE}/documents/convert/image-to-pdf`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const pdfSize = response.data.size;
      const originalSize = selectedFile.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace(/\.\w+$/, '.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Image converted to PDF!');
      setResult({
        type: 'download',
        action: 'Image → PDF Conversion',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: pdfSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - pdfSize / originalSize) * 100).toFixed(1),
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Image to PDF conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // PDF: Merge multiple PDFs
  const handleMergePdfs = async () => {
    if (selectedFiles.length < 2) {
      toast.error('Cần ít nhất 2 file PDF để merge!');
      return;
    }

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });
    formData.append('output_filename', 'merged.pdf');

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/merge`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const mergedSize = response.data.size;
      const totalOriginalSize = selectedFiles.reduce((sum, f) => sum + f.size, 0);

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'merged.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Merged ${selectedFiles.length} PDFs successfully!`);
      setResult({
        type: 'download',
        action: `Merge ${selectedFiles.length} PDFs`,
        originalFile: selectedFiles.map(f => f.name).join(', '),
        originalSize: totalOriginalSize,
        outputFile: 'merged.pdf',
        outputSize: mergedSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - mergedSize / totalOriginalSize) * 100).toFixed(1),
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'PDF merge failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFiles.map(f => f.name).join(', ')
      });
    } finally {
      setLoading(false);
    }
  };

  // PDF: Split PDF by page ranges
  const handleSplitPdf = async () => {
    if (!selectedFile) return;
    if (!pageRanges.trim()) {
      toast.error('Nhập page ranges (ví dụ: 1-3,5-7)');
      return;
    }

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('page_ranges', pageRanges);
    formData.append('output_prefix', 'split');

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/split`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      
      // Download the ZIP file containing split PDFs
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'split_pdfs.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ PDF split successfully!`);
      setResult({
        type: 'download',
        action: `Split PDF (${pageRanges})`,
        originalFile: selectedFile.name,
        originalSize: selectedFile.size,
        outputFile: 'split_pdfs.zip',
        outputSize: response.data.size,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'PDF split failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // PDF: Rotate pages
  const handleRotatePdf = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('rotation', rotationAngle.toString());
    if (specificPages.trim()) {
      formData.append('pages', specificPages);
    }

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/rotate`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const rotatedSize = response.data.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace('.pdf', '_rotated.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      const pagesDesc = specificPages.trim() ? `pages ${specificPages}` : 'all pages';
      toast.success(`✅ PDF rotated ${rotationAngle}° (${pagesDesc})!`);
      setResult({
        type: 'download',
        action: `Rotate PDF ${rotationAngle}°`,
        originalFile: selectedFile.name,
        originalSize: selectedFile.size,
        outputFile: outputFilename,
        outputSize: rotatedSize,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'PDF rotation failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Advanced PDF: Add Watermark
  const handleAddWatermark = async () => {
    if (!selectedFile || !watermarkText.trim()) {
      toast.error('Please enter watermark text');
      return;
    }

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('watermark_text', watermarkText);
    formData.append('position', watermarkPosition);
    formData.append('opacity', '0.3');

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/watermark`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const watermarkedSize = response.data.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace('.pdf', '_watermarked.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Watermark added to PDF!`);
      setResult({
        type: 'download',
        action: 'Add Watermark',
        originalFile: selectedFile.name,
        originalSize: selectedFile.size,
        outputFile: outputFilename,
        outputSize: watermarkedSize,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });
      setWatermarkText(''); // Clear form
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Watermark addition failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Advanced PDF: Password Protection
  const handleProtectPdf = async () => {
    if (!selectedFile || !password.trim()) {
      toast.error('Please enter a password');
      return;
    }

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('password', password);

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/protect`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const protectedSize = response.data.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace('.pdf', '_protected.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ PDF protected with password!`);
      setResult({
        type: 'download',
        action: 'Password Protection',
        originalFile: selectedFile.name,
        originalSize: selectedFile.size,
        outputFile: outputFilename,
        outputSize: protectedSize,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });
      setPassword(''); // Clear password
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Password protection failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Advanced PDF: Unlock PDF
  const handleUnlockPdf = async () => {
    if (!selectedFile || !password.trim()) {
      toast.error('Please enter the password');
      return;
    }

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('password', password);

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/unlock`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const unlockedSize = response.data.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace('.pdf', '_unlocked.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ PDF unlocked successfully!`);
      setResult({
        type: 'download',
        action: 'Unlock PDF',
        originalFile: selectedFile.name,
        originalSize: selectedFile.size,
        outputFile: outputFilename,
        outputSize: unlockedSize,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });
      setPassword(''); // Clear password
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('❌ Incorrect password');
      } else {
        const errorMsg = error.response?.data?.detail || 'Unlock failed';
        toast.error(errorMsg);
      }
      setResult({
        type: 'error',
        message: error.response?.status === 401 ? 'Incorrect password' : error.response?.data?.detail || 'Unlock failed',
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Advanced PDF: PDF to Images
  const handlePdfToImages = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('format', imageFormat);
    formData.append('dpi', '200');

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/to-images`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const zipSize = response.data.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace('.pdf', `_images.zip`);
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ PDF converted to ${imageFormat.toUpperCase()} images!`);
      setResult({
        type: 'download',
        action: `PDF → ${imageFormat.toUpperCase()} Images`,
        originalFile: selectedFile.name,
        originalSize: selectedFile.size,
        outputFile: outputFilename,
        outputSize: zipSize,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'PDF to images conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // Advanced PDF: Add Page Numbers
  const handleAddPageNumbers = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('position', watermarkPosition); // Reuse position state
    formData.append('format', pageNumberFormat);

    try {
      const response = await axios.post(`${API_BASE}/documents/pdf/add-page-numbers`, formData, {
        responseType: 'blob',
      });

      const processingTimeMs = Date.now() - startTime;
      const numberedSize = response.data.size;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace('.pdf', '_numbered.pdf');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Page numbers added to PDF!`);
      setResult({
        type: 'download',
        action: 'Add Page Numbers',
        originalFile: selectedFile.name,
        originalSize: selectedFile.size,
        outputFile: outputFilename,
        outputSize: numberedSize,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Page numbering failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: selectedFile.name
      });
    } finally {
      setLoading(false);
    }
  };

  // ==================== NEW: ADOBE-ONLY FEATURES ====================

  // OCR PDF - Convert scanned PDF to searchable
  const handleOcrPdf = async () => {
    if (!selectedFile) return;

    await handleConversion({
      operation: `OCR PDF (${ocrLanguage})`,
      endpoint: '/documents/pdf/ocr',
      file: selectedFile,
      additionalData: {
        language: ocrLanguage,
      },
      outputFilename: selectedFile.name.replace('.pdf', '_ocr.pdf'),
      technology: 'adobe',
      validateFileType: 'pdf',
    });

    setShowOcrModal(false);
  };

  // Extract PDF Content - AI extraction
  const handleExtractContent = async () => {
    if (!selectedFile) return;

    await handleConversion({
      operation: `Extract PDF Content (${extractType})`,
      endpoint: '/documents/pdf/extract-content',
      file: selectedFile,
      additionalData: {
        extract_type: extractType,
      },
      technology: 'adobe',
      validateFileType: 'pdf',
      responseType: 'json',
    });

    setShowExtractModal(false);
  };

  // HTML to PDF - Perfect HTML rendering
  const handleHtmlToPdf = async () => {
    if (!htmlContent.trim()) {
      toast.error('❌ Vui lòng nhập nội dung HTML');
      return;
    }

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation('HTML → PDF');
    setCurrentTechnology('adobe');
    const startTime = Date.now();

    try {
      const formData = new FormData();
      formData.append('html_content', htmlContent);
      formData.append('page_size', htmlPageSize);
      formData.append('orientation', htmlOrientation);

      const response = await axios.post(
        `${API_BASE}/documents/convert/html-to-pdf`,
        formData,
        {
          responseType: 'blob',
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(percent);
            }
          },
        }
      );

      setUploadProgress(100);
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const processingTimeMs = Date.now() - startTime;
      const pdfSize = response.data.size;

      // Download PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `html_${htmlPageSize}_${htmlOrientation}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('✅ HTML converted to PDF successfully!');
      setResult({
        type: 'download',
        action: `HTML → PDF (${htmlPageSize} ${htmlOrientation})`,
        originalFile: 'HTML Content',
        originalSize: new Blob([htmlContent]).size,
        outputFile: `html_${htmlPageSize}_${htmlOrientation}.pdf`,
        outputSize: pdfSize,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url,
        technology: 'adobe',
        quality: '10/10',
      });

      setShowHtmlToPdfModal(false);
      setHtmlContent(''); // Clear form
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'HTML to PDF conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: 'HTML Content',
      });
    } finally {
      setLoading(false);
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
      setCurrentTechnology(null);
    }
  };

  // ==================== END: ADOBE-ONLY FEATURES ====================

  // ==================== BATCH CONVERSION HANDLERS ====================

  // Batch: Word to PDF
  const handleBatchWordToPdf = async () => {
    if (batchFiles.length === 0) {
      toast.error('Vui lòng upload ít nhất 1 file');
      return;
    }

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation(`Chuyển đổi ${batchFiles.length} file Word → PDF`);
    const startTime = Date.now();

    const formData = new FormData();
    batchFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post(`${API_BASE}/documents/batch/word-to-pdf`, formData, {
        responseType: 'blob',
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percent);
          }
        },
      });

      setUploadProgress(100);
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const processingTimeMs = Date.now() - startTime;

      // Download ZIP
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `converted_${batchFiles.length}_files.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã chuyển đổi ${batchFiles.length} file thành công!`);
      setResult({
        type: 'download',
        action: `Batch Convert ${batchFiles.length} Word → PDF`,
        originalFile: `${batchFiles.length} files`,
        originalSize: batchFiles.reduce((sum, f) => sum + f.size, 0),
        outputFile: `converted_${batchFiles.length}_files.zip`,
        outputSize: response.data.size,
        processingTime: processingTimeMs,
        compressionRatio: '0',
        downloadUrl: url
      });

      // Clear batch files
      setBatchFiles([]);
      setBatchMode(false);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Batch conversion failed';
      toast.error(errorMsg);
      setResult({
        type: 'error',
        message: errorMsg,
        originalFile: `${batchFiles.length} files`
      });
    } finally {
      setLoading(false);
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
    }
  };

  // Batch: PDF to Word
  const handleBatchPdfToWord = async () => {
    if (batchFiles.length === 0) return;

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation(`Chuyển đổi ${batchFiles.length} file PDF → Word`);
    const startTime = Date.now();

    const formData = new FormData();
    batchFiles.forEach(file => formData.append('files', file));

    try {
      const response = await axios.post(`${API_BASE}/documents/batch/pdf-to-word`, formData, {
        responseType: 'blob',
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            setUploadProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
          }
        },
      });

      setUploadProgress(100);
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `converted_word_${batchFiles.length}_files.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã chuyển đổi ${batchFiles.length} file thành công!`);
      setBatchFiles([]);
      setBatchMode(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Batch conversion failed');
    } finally {
      setLoading(false);
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
    }
  };

  // Batch: Excel to PDF
  const handleBatchExcelToPdf = async () => {
    if (batchFiles.length === 0) return;

    setLoading(true);
    setCurrentOperation(`Chuyển đổi ${batchFiles.length} file Excel → PDF`);

    const formData = new FormData();
    batchFiles.forEach(file => formData.append('files', file));

    try {
      const response = await axios.post(`${API_BASE}/documents/batch/excel-to-pdf`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `excel_to_pdf_${batchFiles.length}_files.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã chuyển đổi ${batchFiles.length} file!`);
      setBatchFiles([]);
      setBatchMode(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Batch conversion failed');
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // Batch: Image to PDF
  const handleBatchImageToPdf = async () => {
    if (batchFiles.length === 0) return;

    setLoading(true);
    setCurrentOperation(`Chuyển đổi ${batchFiles.length} ảnh → PDF`);

    const formData = new FormData();
    batchFiles.forEach(file => formData.append('files', file));

    try {
      const response = await axios.post(`${API_BASE}/documents/batch/image-to-pdf`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `images_to_pdf_${batchFiles.length}_files.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã chuyển đổi ${batchFiles.length} ảnh!`);
      setBatchFiles([]);
      setBatchMode(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Batch conversion failed');
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // Batch: Compress PDF
  const handleBatchCompressPdf = async () => {
    if (batchFiles.length === 0) return;

    setLoading(true);
    setCurrentOperation(`Nén ${batchFiles.length} file PDF`);

    const formData = new FormData();
    batchFiles.forEach(file => formData.append('files', file));
    formData.append('quality', 'medium');

    try {
      const response = await axios.post(`${API_BASE}/documents/batch/compress-pdf`, formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `compressed_${batchFiles.length}_files.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã nén ${batchFiles.length} file!`);
      setBatchFiles([]);
      setBatchMode(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Batch compression failed');
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // Bulk: Convert many PDFs to one format (Word/Excel/Image)
  const handleBulkPdfConvert = async () => {
    if (batchFiles.length === 0) {
      toast.error('Vui lòng upload ít nhất 1 file PDF');
      return;
    }

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    
    const formatNames = {
      word: 'Word',
      excel: 'Excel',
      image: 'Hình ảnh'
    };
    
    setCurrentOperation(`Chuyển đổi ${batchFiles.length} PDF → ${formatNames[bulkFormat]}`);
    const startTime = Date.now();

    const formData = new FormData();
    batchFiles.forEach(file => formData.append('files', file));

    try {
      const response = await axios.post(
        `${API_BASE}/documents/batch/pdf-to-multiple?format=${bulkFormat}`,
        formData,
        {
          responseType: 'blob',
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(percent);
            }
          },
        }
      );

      // Simulate processing progress
      setUploadProgress(100);
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(1);

      // Download ZIP
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bulk_pdf_to_${bulkFormat}_${batchFiles.length}_files.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã chuyển đổi ${batchFiles.length} PDF → ${formatNames[bulkFormat]} trong ${duration}s!`);
      setBatchFiles([]);
      setBatchMode(false);
      setBulkFormat('word');
    } catch (error: any) {
      console.error('Bulk PDF conversion error:', error);
      toast.error(error.response?.data?.detail || `Bulk conversion to ${bulkFormat} failed`);
    } finally {
      setLoading(false);
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
    }
  };

  // Merge Word files to single PDF
  const handleMergeWordToPdf = async () => {
    if (batchFiles.length === 0) {
      toast.error('Vui lòng upload ít nhất 1 file Word');
      return;
    }

    const controller = new AbortController();
    setAbortController(controller);
    setLoading(true);
    setLoadingOperation('merge-word-to-pdf'); // Track specific operation
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation(`Gộp ${batchFiles.length} file Word → 1 PDF`);
    const startTime = Date.now();

    const formData = new FormData();
    batchFiles.forEach(file => formData.append('files', file));

    try {
      const response = await axios.post(
        `${API_BASE}/documents/batch/merge-word-to-pdf`,
        formData,
        {
          responseType: 'blob',
          signal: controller.signal, // Add abort signal
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(percent);
            }
          },
        }
      );

      // Simulate processing progress
      setUploadProgress(100);
      for (let i = 0; i <= 100; i += 20) {
        setProcessingProgress(i);
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(1);

      // Download merged PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `merged_${batchFiles.length}_documents.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`✅ Đã gộp ${batchFiles.length} file Word thành 1 PDF trong ${duration}s!`);
      setBatchFiles([]);
      setBatchMode(false);
    } catch (error: any) {
      // Check if operation was aborted
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        toast('❌ Đã hủy gộp Word files', { icon: 'ℹ️' });
        return;
      }
      
      console.error('Merge Word to PDF error:', error);
      toast.error(error.response?.data?.detail || 'Failed to merge Word files');
    } finally {
      setLoading(false);
      setLoadingOperation(null); // Clear operation
      setAbortController(null); // Clear abort controller
      setUploadProgress(0);
      setProcessingProgress(0);
      setCurrentOperation('');
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          🛠️ File Processing Tools
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Convert, edit, and process your files with AI-powered tools
        </p>
      </div>

      {/* Search Bar - NEW */}
      <div className="mb-6 relative">
        <div className="relative">
          <Search className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
          <Input
            type="text"
            placeholder='🔍 Search operations... (e.g., "word to pdf", "merge", "compress")'
            className="pl-10 py-6 text-base shadow-sm"
            value={searchQuery}
            onChange={handleSearchChange}
            onFocus={() => searchQuery && setShowSearchResults(true)}
          />
        </div>
        
        {/* Search Results Dropdown */}
        {showSearchResults && searchQuery && (
          <Card className="absolute z-50 w-full mt-2 shadow-lg border-2 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-semibold text-blue-900">
                  🔍 Found {filterOperations(searchQuery).length} operations:
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSearchQuery('');
                    setShowSearchResults(false);
                  }}
                >
                  ✕
                </Button>
              </div>
              
              {filterOperations(searchQuery).length > 0 ? (
                <div className="grid grid-cols-2 gap-2">
                  {filterOperations(searchQuery).map(op => (
                    <Button
                      key={op.id}
                      variant="outline"
                      className={`justify-start h-auto py-3 px-4 hover:border-${op.color}-500 hover:bg-${op.color}-50`}
                      onClick={() => handleOperationSelect(op.id)}
                    >
                      <div className="flex items-center gap-2 w-full">
                        <span className="text-2xl">{op.icon}</span>
                        <div className="text-left flex-1">
                          <div className="font-medium text-sm">{op.name}</div>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="secondary" className="text-xs">
                              {op.category}
                            </Badge>
                            <TechnologyBadge tech={op.tech as any} size="small" />
                          </div>
                        </div>
                      </div>
                    </Button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-600 text-center py-4">
                  No operations found for "{searchQuery}"
                </p>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Popular Operations Section - NEW */}
      <Card className="mb-6 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-xl">
            ⭐ Popular Operations
            <Badge variant="secondary" className="ml-2">Most Used</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {getPopularOperations().map(op => (
              <Button
                key={op.id}
                variant="outline"
                className="h-auto py-6 flex-col gap-3 bg-white hover:shadow-lg hover:scale-105 transition-all duration-200 border-2 hover:border-blue-500"
                onClick={() => handleOperationSelect(op.id)}
              >
                <div className="text-4xl">{op.icon}</div>
                <div className="font-semibold text-center">{op.name}</div>
                <div className="flex flex-col items-center gap-1">
                  <Badge variant="secondary" className="text-xs">
                    {op.category}
                  </Badge>
                  <TechnologyBadge tech={op.tech as any} size="small" showQuality />
                </div>
              </Button>
            ))}
          </div>
          <p className="text-xs text-center text-gray-600 mt-4">
            💡 Click any operation to get started quickly
          </p>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={activeTab === 'documents' ? 'default' : 'outline'}
          onClick={() => setActiveTab('documents')}
        >
          <FileText className="w-4 h-4 mr-2" />
          Documents
        </Button>
        <Button
          variant={activeTab === 'images' ? 'default' : 'outline'}
          onClick={() => setActiveTab('images')}
        >
          <Image className="w-4 h-4 mr-2" />
          Images
        </Button>
        <Button
          variant={activeTab === 'ocr' ? 'default' : 'outline'}
          onClick={() => setActiveTab('ocr')}
        >
          <FileType className="w-4 h-4 mr-2" />
          OCR
        </Button>
        <Button
          variant={activeTab === 'settings' ? 'default' : 'outline'}
          onClick={() => setActiveTab('settings')}
        >
          <Settings className="w-4 h-4 mr-2" />
          Settings
        </Button>
      </div>

      {/* Settings Panel - Full Width */}
      {activeTab === 'settings' && (
        <SettingsPanel />
      )}

      {/* Regular Tools - 2 Column Grid */}
      {activeTab !== 'settings' && (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Area */}
        <Card>
          <CardHeader>
            <CardTitle>
              {pdfOperation === 'merge' ? 'Upload Multiple PDFs' : batchMode ? `Batch: ${batchOperation?.toUpperCase()}` : 'Upload File'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {batchMode ? (
              // Batch Mode Upload
              <div className="space-y-4">
                <div
                  onDrop={(e) => {
                    e.preventDefault();
                    setIsDraggingBatch(false);
                    const files = Array.from(e.dataTransfer.files);
                    setBatchFiles(prev => [...prev, ...files]);
                    if (files.length > 0) {
                      toast.success(`✅ Đã thêm ${files.length} file(s)`);
                    }
                  }}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDraggingBatch(true);
                  }}
                  onDragLeave={() => setIsDraggingBatch(false)}
                  className={`
                    border-2 border-dashed rounded-lg p-6 text-center transition-all cursor-pointer
                    ${isDraggingBatch 
                      ? 'border-purple-500 bg-purple-100 scale-105 shadow-lg' 
                      : 'border-purple-300 bg-purple-50 hover:border-purple-500'
                    }
                  `}
                  onClick={() => document.getElementById('batchFileInput')?.click()}
                >
                  <Upload className={`w-10 h-10 mx-auto mb-3 transition-all ${isDraggingBatch ? 'text-purple-600 scale-110' : 'text-purple-500'}`} />
                  <p className="text-md font-medium mb-1 text-purple-900">
                    📁 Click để chọn NHIỀU file cùng lúc
                  </p>
                  <p className="text-xs text-purple-700 mt-1">
                    Hoặc kéo thả nhiều file vào đây
                  </p>
                  <p className="text-xs text-purple-600 mt-2 font-semibold">
                    � Tip: Giữ Ctrl/Cmd + Click để chọn nhiều files
                  </p>
                  <input
                    id="batchFileInput"
                    type="file"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files) {
                        const newFiles = Array.from(e.target.files);
                        setBatchFiles(prev => [...prev, ...newFiles]);
                        toast.success(`✅ Đã thêm ${newFiles.length} file(s)`);
                      }
                    }}
                    accept={
                      batchOperation === 'word-to-pdf' ? '.docx,.doc' :
                      batchOperation === 'pdf-to-word' ? '.pdf' :
                      batchOperation === 'excel-to-pdf' ? '.xlsx,.xls' :
                      batchOperation === 'image-to-pdf' ? 'image/*' :
                      batchOperation === 'compress-pdf' ? '.pdf' :
                      batchOperation === 'bulk-pdf' ? '.pdf' : '*'
                    }
                    multiple
                  />
                </div>

                {/* Batch File List with Drag & Drop */}
                {batchFiles.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">
                        {batchFiles.length} file(s) đã chọn
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setBatchFiles([])}
                      >
                        Xóa Tất Cả
                      </Button>
                    </div>
                    
                    <div className="p-3 bg-purple-50 border border-purple-300 rounded-lg">
                      <p className="text-xs text-purple-800 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                        </svg>
                        <strong>
                          {batchOperation === 'bulk-pdf' 
                            ? 'Bulk Mode: Chuyển PDF sang nhiều định dạng' 
                            : batchOperation === 'merge-word-to-pdf'
                            ? 'Merge Mode: Gộp nhiều Word thành 1 PDF duy nhất'
                            : 'Batch Mode: Tất cả file sẽ được convert cùng lúc'
                          }
                        </strong>
                      </p>
                      {(batchOperation === 'merge-word-to-pdf' || batchFiles.length > 1) && (
                        <p className="text-xs text-purple-700 mt-2 flex items-center gap-1">
                          🔄 <strong>Sắp xếp thứ tự:</strong> Kéo thả hoặc dùng nút ↑↓ để di chuyển file
                        </p>
                      )}
                    </div>
                    
                    {/* Format selector for bulk PDF conversion */}
                    {batchOperation === 'bulk-pdf' && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">
                          📁 Chọn định dạng đích:
                        </label>
                        <div className="grid grid-cols-3 gap-2">
                          <button
                            onClick={() => setBulkFormat('word')}
                            className={`p-3 rounded-lg border-2 transition-all ${
                              bulkFormat === 'word'
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 hover:border-blue-300'
                            }`}
                          >
                            <div className="text-2xl mb-1">📝</div>
                            <div className="text-xs font-medium">Word</div>
                          </button>
                          <button
                            onClick={() => setBulkFormat('excel')}
                            className={`p-3 rounded-lg border-2 transition-all ${
                              bulkFormat === 'excel'
                                ? 'border-green-500 bg-green-50'
                                : 'border-gray-200 hover:border-green-300'
                            }`}
                          >
                            <div className="text-2xl mb-1">📊</div>
                            <div className="text-xs font-medium">Excel</div>
                          </button>
                          <button
                            onClick={() => setBulkFormat('image')}
                            className={`p-3 rounded-lg border-2 transition-all ${
                              bulkFormat === 'image'
                                ? 'border-orange-500 bg-orange-50'
                                : 'border-gray-200 hover:border-orange-300'
                            }`}
                          >
                            <div className="text-2xl mb-1">🖼️</div>
                            <div className="text-xs font-medium">Images</div>
                          </button>
                        </div>
                      </div>
                    )}
                    
                    <div className="max-h-96 overflow-y-auto space-y-2">
                      {batchFiles.map((file, idx) => (
                        <div
                          key={`${file.name}-${idx}`}
                          draggable
                          onDragStart={() => handleBatchDragStart(idx)}
                          onDragOver={(e) => handleBatchDragOver(e, idx)}
                          onDragEnd={handleBatchDragEnd}
                          className={`flex items-center gap-3 p-3 rounded-lg border-2 transition-all cursor-move ${
                            draggedBatchIndex === idx
                              ? 'border-purple-500 bg-purple-100 shadow-lg scale-105'
                              : 'bg-white border-gray-200 hover:border-purple-300'
                          }`}
                        >
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 text-white flex items-center justify-center font-bold text-sm shadow-md">
                            {idx + 1}
                          </div>

                          <span className="text-2xl flex-shrink-0">
                            {file.type.includes('image') ? '🖼️' : 
                             file.name.endsWith('.pdf') ? '📕' :
                             file.name.endsWith('.docx') || file.name.endsWith('.doc') ? '📝' :
                             file.name.endsWith('.xlsx') || file.name.endsWith('.xls') ? '📊' : '📄'}
                          </span>

                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate text-gray-900">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(file.size / 1024).toFixed(1)} KB
                            </p>
                          </div>

                          {/* Move up/down buttons */}
                          <div className="flex flex-col gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => moveBatchFile(idx, idx - 1)}
                              disabled={idx === 0}
                              className="h-6 w-6 p-0 hover:bg-purple-100"
                              title="Di chuyển lên"
                            >
                              ↑
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => moveBatchFile(idx, idx + 1)}
                              disabled={idx === batchFiles.length - 1}
                              className="h-6 w-6 p-0 hover:bg-purple-100"
                              title="Di chuyển xuống"
                            >
                              ↓
                            </Button>
                          </div>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setBatchFiles(prev => prev.filter((_, i) => i !== idx))}
                            className="flex-shrink-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                          >
                            ✕
                          </Button>
                        </div>
                      ))}
                    </div>
                    
                    <Button
                      onClick={() => {
                        if (batchOperation === 'word-to-pdf') handleBatchWordToPdf();
                        else if (batchOperation === 'pdf-to-word') handleBatchPdfToWord();
                        else if (batchOperation === 'excel-to-pdf') handleBatchExcelToPdf();
                        else if (batchOperation === 'image-to-pdf') handleBatchImageToPdf();
                        else if (batchOperation === 'compress-pdf') handleBatchCompressPdf();
                        else if (batchOperation === 'bulk-pdf') handleBulkPdfConvert();
                        else if (batchOperation === 'merge-word-to-pdf') handleMergeWordToPdf();
                      }}
                      disabled={
                        batchFiles.length === 0 || 
                        isOperationLoading(batchOperation === 'merge-word-to-pdf' ? 'merge-word-to-pdf' : `batch-${batchOperation}`)
                      }
                      className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                    >
                      {isAnyOperationLoading() ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '⚡'}
                      {batchOperation === 'bulk-pdf' 
                        ? `Convert ${batchFiles.length} PDF → ${bulkFormat.toUpperCase()}`
                        : batchOperation === 'merge-word-to-pdf'
                        ? `Gộp ${batchFiles.length} Word → 1 PDF`
                        : `Convert ${batchFiles.length} File(s)`
                      }
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setBatchMode(false);
                        setBatchFiles([]);
                        setBatchOperation(null);
                      }}
                      className="w-full"
                    >
                      ← Quay về chế độ đơn file
                    </Button>
                  </div>
                )}
              </div>
            ) : pdfOperation === 'merge' ? (
              // Multi-file upload for Merge PDFs
              <div className="space-y-4">
                <div
                  onDrop={(e) => {
                    e.preventDefault();
                    const files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
                    setSelectedFiles(prev => [...prev, ...files]);
                  }}
                  onDragOver={(e) => e.preventDefault()}
                  className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer bg-blue-50"
                  onClick={() => document.getElementById('multiFileInput')?.click()}
                >
                  <Upload className="w-10 h-10 mx-auto mb-3 text-blue-500" />
                  <p className="text-md font-medium mb-1 text-blue-900">
                    Click or drag PDF files here
                  </p>
                  <p className="text-xs text-blue-700">
                    📚 Upload multiple PDFs to merge (minimum 2 files)
                  </p>
                  <input
                    id="multiFileInput"
                    type="file"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files) {
                        const newFiles = Array.from(e.target.files);
                        setSelectedFiles(prev => [...prev, ...newFiles]);
                      }
                    }}
                    accept=".pdf"
                    multiple
                  />
                </div>

                {/* File List */}
                {selectedFiles.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">
                        {selectedFiles.length} file(s) được chọn
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedFiles([])}
                      >
                        Xóa Tất Cả
                      </Button>
                    </div>
                    
                    <div className="p-3 bg-blue-50 border border-blue-300 rounded-lg">
                      <p className="text-xs text-blue-800 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                        </svg>
                        <strong>Kéo thả</strong> để sắp xếp thứ tự file (từ trên xuống dưới)
                      </p>
                    </div>
                    
                    <div className="max-h-96 overflow-y-auto space-y-2">
                      {selectedFiles.map((file, idx) => (
                        <div
                          key={`${file.name}-${idx}`}
                          draggable
                          onDragStart={() => handleDragStart(idx)}
                          onDragOver={(e) => handleDragOver(e, idx)}
                          onDragEnd={handleDragEnd}
                          className={`
                            flex items-center gap-3 p-3 bg-white rounded-lg border-2 
                            transition-all duration-200 cursor-move
                            ${draggedIndex === idx 
                              ? 'border-blue-500 shadow-lg scale-105 bg-blue-50' 
                              : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
                            }
                          `}
                        >
                          {/* Order Number */}
                          <div className={`
                            flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
                            font-bold text-sm
                            ${draggedIndex === idx 
                              ? 'bg-blue-500 text-white' 
                              : 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
                            }
                          `}>
                            {idx + 1}
                          </div>

                          {/* Drag Handle */}
                          <div className="flex-shrink-0 text-gray-400 hover:text-blue-500 cursor-grab active:cursor-grabbing">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M7 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 2zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 14zm6-8a2 2 0 1 0-.001-4.001A2 2 0 0 0 13 6zm0 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 14z"></path>
                            </svg>
                          </div>

                          {/* File Icon */}
                          <span className="text-2xl flex-shrink-0">📄</span>

                          {/* File Info */}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate text-gray-900">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(file.size / 1024).toFixed(1)} KB
                            </p>
                          </div>

                          {/* Move Buttons */}
                          <div className="flex flex-col gap-1">
                            <button
                              onClick={() => moveFile(idx, idx - 1)}
                              disabled={idx === 0}
                              className={`
                                p-1 rounded transition-colors
                                ${idx === 0 
                                  ? 'text-gray-300 cursor-not-allowed' 
                                  : 'text-blue-600 hover:bg-blue-100 active:bg-blue-200'
                                }
                              `}
                              title="Di chuyển lên"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                              </svg>
                            </button>
                            <button
                              onClick={() => moveFile(idx, idx + 1)}
                              disabled={idx === selectedFiles.length - 1}
                              className={`
                                p-1 rounded transition-colors
                                ${idx === selectedFiles.length - 1
                                  ? 'text-gray-300 cursor-not-allowed' 
                                  : 'text-blue-600 hover:bg-blue-100 active:bg-blue-200'
                                }
                              `}
                              title="Di chuyển xuống"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            </button>
                          </div>

                          {/* Delete Button */}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== idx))}
                            className="flex-shrink-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                          >
                            ✕
                          </Button>
                        </div>
                      ))}
                    </div>
                    
                    <Button
                      onClick={handleMergePdfs}
                      disabled={loading || selectedFiles.length < 2}
                      className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                    >
                      {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                      Gộp {selectedFiles.length} PDFs theo thứ tự
                    </Button>
                  </div>
                )}
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setPdfOperation(null);
                    setSelectedFiles([]);
                  }}
                  className="w-full"
                >
                  ← Back to Single File Mode
                </Button>
              </div>
            ) : (
              // Enhanced single file upload - Full width with better UX
              <div className="space-y-4">
                {!selectedFile ? (
                  // Large prominent upload zone
                  <div
                    onDrop={handleDrop}
                    onDragOver={(e) => {
                      e.preventDefault();
                      e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
                    }}
                    onDragLeave={(e) => {
                      e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
                    }}
                    className="border-3 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-400 hover:bg-gray-50 transition-all duration-200 cursor-pointer group"
                    onClick={() => document.getElementById('fileInput')?.click()}
                  >
                    {/* Upload Icon with animation */}
                    <div className="relative inline-block">
                      <Upload className="w-20 h-20 mx-auto mb-6 text-gray-400 group-hover:text-blue-500 transition-colors" />
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                        <span className="text-white text-xs font-bold">+</span>
                      </div>
                    </div>
                    
                    {/* Main message */}
                    <h3 className="text-2xl font-semibold mb-2 text-gray-700 group-hover:text-blue-600 transition-colors">
                      Drop your file here
                    </h3>
                    <p className="text-base text-gray-500 mb-6">
                      or click to browse from your computer
                    </p>
                    
                    {/* Supported formats with icons */}
                    <div className="flex items-center justify-center gap-6 flex-wrap">
                      {activeTab === 'documents' && (
                        <>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">📝</span>
                            <span className="text-sm font-medium text-gray-700">Word</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">📊</span>
                            <span className="text-sm font-medium text-gray-700">Excel</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">📄</span>
                            <span className="text-sm font-medium text-gray-700">PDF</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">📑</span>
                            <span className="text-sm font-medium text-gray-700">PowerPoint</span>
                          </div>
                        </>
                      )}
                      {activeTab === 'images' && (
                        <>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">🖼️</span>
                            <span className="text-sm font-medium text-gray-700">JPG</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">🎨</span>
                            <span className="text-sm font-medium text-gray-700">PNG</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">🌐</span>
                            <span className="text-sm font-medium text-gray-700">WebP</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">📱</span>
                            <span className="text-sm font-medium text-gray-700">HEIC</span>
                          </div>
                        </>
                      )}
                      {activeTab === 'ocr' && (
                        <>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">🖼️</span>
                            <span className="text-sm font-medium text-gray-700">JPG</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">🎨</span>
                            <span className="text-sm font-medium text-gray-700">PNG</span>
                          </div>
                          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                            <span className="text-2xl">📄</span>
                            <span className="text-sm font-medium text-gray-700">PDF with text</span>
                          </div>
                        </>
                      )}
                    </div>
                    
                    {/* File size limit info */}
                    <p className="text-xs text-gray-400 mt-6">
                      Maximum file size: 50MB
                    </p>
                    
                    <input
                      id="fileInput"
                      type="file"
                      className="hidden"
                      onChange={handleFileChange}
                      accept={
                        activeTab === 'documents'
                          ? '.docx,.doc,.pdf,.xlsx,.xls,.pptx,.ppt'
                          : activeTab === 'images'
                          ? 'image/*'
                          : 'image/*'
                      }
                    />
                  </div>
                ) : (
                  // File selected - Show file info card
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6">
                    <div className="flex items-start justify-between gap-4">
                      {/* File icon based on type */}
                      <div className="flex-shrink-0">
                        <div className="w-16 h-16 bg-white rounded-lg shadow-md flex items-center justify-center text-3xl">
                          {selectedFile.name.endsWith('.pdf') && '📄'}
                          {(selectedFile.name.endsWith('.docx') || selectedFile.name.endsWith('.doc')) && '📝'}
                          {(selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls')) && '📊'}
                          {(selectedFile.name.endsWith('.pptx') || selectedFile.name.endsWith('.ppt')) && '📑'}
                          {selectedFile.type.startsWith('image/') && '🖼️'}
                          {!selectedFile.name.match(/\.(pdf|docx?|xlsx?|pptx?)$/i) && !selectedFile.type.startsWith('image/') && '📎'}
                        </div>
                      </div>
                      
                      {/* File details */}
                      <div className="flex-1 min-w-0">
                        <h4 className="text-lg font-semibold text-gray-800 mb-1 truncate" title={selectedFile.name}>
                          {selectedFile.name}
                        </h4>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <span className="font-medium">Size:</span>
                            <span>{(selectedFile.size / 1024).toFixed(2)} KB</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="font-medium">Type:</span>
                            <span className="uppercase">{selectedFile.name.split('.').pop()}</span>
                          </div>
                        </div>
                        
                        {/* Success indicator */}
                        <div className="flex items-center gap-2 mt-3">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span className="text-sm text-green-700 font-medium">Ready to process</span>
                        </div>
                      </div>
                      
                      {/* Clear button */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedFile(null)}
                        className="flex-shrink-0 hover:bg-red-50 hover:border-red-300 hover:text-red-600"
                      >
                        <span className="mr-1">✕</span> Remove
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Actions</span>
              {selectedFile && (
                <div className="flex items-center gap-2 text-xs">
                  <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                    <span className="mr-1">🔄</span> Convert
                  </Badge>
                  <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                    <span className="mr-1">✏️</span> Edit
                  </Badge>
                  <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                    <span className="mr-1">📚</span> Batch
                  </Badge>
                  <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                    <span className="mr-1">🔍</span> OCR
                  </Badge>
                </div>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(() => {
                // Get file type once for all tabs
                const fileType = getFileType(selectedFile);
                
                if (activeTab === 'documents') {
                  // Smart actions based on file type
                  if (!selectedFile) {
                    return (
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-center">
                        <p className="text-sm text-blue-800">
                          📤 Upload một file để xem các thao tác khả dụng
                        </p>
                      </div>
                    );
                  }

                  // WORD FILES
                  if (fileType === 'word') {
                      return (
                        <div className="space-y-3">
                          <div className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
                            <p className="text-sm font-semibold text-blue-900 mb-1">
                              📝 File Word được phát hiện
                            </p>
                            <p className="text-xs text-blue-700">
                              Các thao tác được đề xuất cho file Word:
                            </p>
                          </div>
                          
                          <div className="space-y-1">
                            <Button
                              onClick={handleWordToPdf}
                              disabled={isOperationLoading('word-to-pdf')}
                              className="w-full bg-blue-600 hover:bg-blue-700"
                            >
                              {isOperationLoading('word-to-pdf') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📄'}
                              <span className="ml-2">Chuyển sang PDF</span>
                            </Button>
                            <div className="flex items-center justify-center gap-2 text-xs">
                              <span className="text-gray-500">Powered by:</span>
                              <TechnologyBadge tech="gotenberg" showQuality size="small" />
                            </div>
                          </div>
                          
                          <Button
                            onClick={() => {
                              if (isAnyOperationLoading()) {
                                toast('⚠️ Một thao tác khác đang chạy!', { icon: '⚠️' });
                                return;
                              }
                              setBatchMode(true);
                              setBatchOperation('word-to-pdf');
                              setBatchFiles([selectedFile]);
                            }}
                            disabled={isOperationLoading('batch-word-to-pdf')}
                            className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                          >
                            {isOperationLoading('batch-word-to-pdf') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                            <span className="ml-2">Chuyển NHIỀU file Word → PDF</span>
                          </Button>
                          
                          <Button
                            onClick={() => {
                              if (isAnyOperationLoading()) {
                                toast('⚠️ Một thao tác khác đang chạy!', { icon: '⚠️' });
                                return;
                              }
                              setBatchMode(true);
                              setBatchOperation('merge-word-to-pdf');
                              setBatchFiles([selectedFile]);
                            }}
                            disabled={isOperationLoading('merge-word-to-pdf')}
                            className="w-full bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔗'}
                            <span className="ml-2">Gộp NHIỀU Word → 1 PDF</span>
                          </Button>
                          
                          <Button
                            onClick={handleExtractPdfText}
                            disabled={loading}
                            className="w-full"
                            variant="outline"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📝'}
                            <span className="ml-2">Trích xuất Text từ Word</span>
                          </Button>
                        </div>
                      );
                    }

                    // EXCEL FILES
                    if (fileType === 'excel') {
                      return (
                        <div className="space-y-3">
                          <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
                            <p className="text-sm font-semibold text-green-900 mb-1">
                              📊 File Excel được phát hiện
                            </p>
                            <p className="text-xs text-green-700">
                              Các thao tác được đề xuất cho file Excel:
                            </p>
                          </div>
                          
                          <Button
                            onClick={handleExcelToPdf}
                            disabled={loading}
                            className="w-full bg-green-600 hover:bg-green-700"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📄'}
                            <span className="ml-2">Chuyển sang PDF</span>
                          </Button>
                          
                          <Button
                            onClick={() => {
                              setBatchMode(true);
                              setBatchOperation('excel-to-pdf');
                              setBatchFiles([selectedFile]);
                            }}
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                            <span className="ml-2">Chuyển NHIỀU file Excel → PDF</span>
                          </Button>
                          
                          <Button
                            onClick={handleExtractPdfText}
                            disabled={loading}
                            className="w-full"
                            variant="outline"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📝'}
                            <span className="ml-2">Trích xuất Data từ Excel</span>
                          </Button>
                        </div>
                      );
                    }

                    // POWERPOINT FILES
                    if (fileType === 'powerpoint') {
                      return (
                        <div className="space-y-3">
                          <div className="p-3 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg">
                            <p className="text-sm font-semibold text-purple-900 mb-1">
                              📽️ File PowerPoint được phát hiện
                            </p>
                            <p className="text-xs text-purple-700">
                              Các thao tác được đề xuất cho file PowerPoint:
                            </p>
                          </div>
                          
                          <Button
                            onClick={handlePowerPointToPdf}
                            disabled={loading}
                            className="w-full bg-purple-600 hover:bg-purple-700"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📄'}
                            <span className="ml-2">Chuyển sang PDF</span>
                          </Button>
                          
                          <Button
                            onClick={handleExtractPdfText}
                            disabled={loading}
                            className="w-full"
                            variant="outline"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📝'}
                            <span className="ml-2">Trích xuất Text từ Slides</span>
                          </Button>
                        </div>
                      );
                    }

                    // PDF FILES
                    if (fileType === 'pdf') {
                      return (
                        <div className="space-y-3">
                          <div className="p-3 bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg">
                            <p className="text-sm font-semibold text-red-900 mb-1">
                              📕 File PDF được phát hiện
                            </p>
                            <p className="text-xs text-red-700">
                              Các thao tác được đề xuất cho file PDF:
                            </p>
                          </div>
                          
                          <div className="space-y-2">
                            <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                              Chuyển đổi
                            </h3>
                            <div className="space-y-1">
                              <Button
                                onClick={() => {
                                  setShowPdfToWordModal(!showPdfToWordModal);
                                  // Scroll to modal if opening
                                  if (!showPdfToWordModal) {
                                    setTimeout(() => {
                                      const modal = document.querySelector('[data-modal="pdf-to-word"]');
                                      if (modal) {
                                        modal.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                                      }
                                    }, 100);
                                  }
                                }}
                                disabled={loading}
                                className="w-full bg-red-600 hover:bg-red-700"
                              >
                                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📝'}
                                <span className="ml-2">Chuyển sang Word</span>
                                {showPdfToWordModal && <span className="ml-auto">▼</span>}
                                {!showPdfToWordModal && <span className="ml-auto">▶</span>}
                              </Button>
                              <div className="flex items-center justify-center gap-2 text-xs">
                                <span className="text-gray-500">Powered by:</span>
                                <TechnologyBadge tech="adobe" showQuality size="small" />
                                <span className="text-gray-400">→</span>
                                <TechnologyBadge tech="pdf2docx" showQuality size="small" />
                              </div>
                            </div>
                            
                            <Button
                              onClick={() => {
                                setBatchMode(true);
                                setBatchOperation('pdf-to-word');
                                setBatchFiles([selectedFile]);
                              }}
                              disabled={loading}
                              className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                              <span className="ml-2">Chuyển NHIỀU PDF → Word</span>
                            </Button>
                            
                            <div className="space-y-1">
                              <Button
                                onClick={handlePdfToExcel}
                                disabled={loading}
                                className="w-full bg-green-600 hover:bg-green-700"
                              >
                                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📊'}
                                <span className="ml-2">Chuyển sang Excel</span>
                              </Button>
                              <div className="flex items-center justify-center gap-2 text-xs">
                                <span className="text-gray-500">Powered by:</span>
                                <TechnologyBadge tech="pdfplumber" showQuality size="small" />
                              </div>
                            </div>
                            
                            <Button
                              onClick={() => {
                                setBatchMode(true);
                                setBatchOperation('bulk-pdf');
                                setBatchFiles([selectedFile]);
                                setBulkFormat('word');
                              }}
                              disabled={loading}
                              className="w-full bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 hover:from-purple-700 hover:via-blue-700 hover:to-green-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔀'}
                              <span className="ml-2">BULK: PDF → Word/Excel/Image</span>
                            </Button>
                          </div>

                          <div className="space-y-2">
                            <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                              Công cụ PDF
                            </h3>
                            <Button
                              onClick={handleExtractPdfText}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {isOperationLoading('extract-text') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📝'}
                              <span className="ml-2">Trích xuất Text</span>
                            </Button>
                            
                            <Button
                              onClick={handlePdfInfo}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {isOperationLoading('pdf-info') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : 'ℹ️'}
                              <span className="ml-2">Xem Thông Tin PDF</span>
                            </Button>
                            
                            <div className="space-y-1">
                              <Button
                                onClick={handleCompressPdf}
                                disabled={!isPdfSelected() || isAnyOperationLoading()}
                                className="w-full"
                                variant="outline"
                              >
                                {isOperationLoading('compress') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📦'}
                                <span className="ml-2">Nén PDF</span>
                              </Button>
                              <div className="flex items-center justify-center gap-2 text-xs">
                                <span className="text-gray-500">Powered by:</span>
                                <TechnologyBadge tech="pypdf" showQuality size="small" />
                              </div>
                            </div>
                            
                            <Button
                              onClick={() => {
                                setBatchMode(true);
                                setBatchOperation('compress-pdf');
                                setBatchFiles([selectedFile]);
                              }}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                              <span className="ml-2">Nén NHIỀU PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('split')}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '✂️'}
                              <span className="ml-2">Tách PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('rotate')}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔄'}
                              <span className="ml-2">Xoay PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('watermark')}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🖨️'}
                              <span className="ml-2">Thêm Watermark</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('protect')}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔒'}
                              <span className="ml-2">Bảo vệ bằng Password</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('unlock')}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔓'}
                              <span className="ml-2">Mở khóa PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('to-images')}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🖼️'}
                              <span className="ml-2">Chuyển sang Images</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('page-numbers')}
                              disabled={!isPdfSelected() || isAnyOperationLoading()}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔢'}
                              <span className="ml-2">Thêm Số Trang</span>
                            </Button>

                            {/* NEW: Adobe-only features */}
                            <div className="col-span-3 mt-4 pt-4 border-t border-blue-200">
                              <h3 className="text-sm font-semibold text-blue-700 mb-3 flex items-center gap-2">
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
                                </svg>
                                Adobe AI-Powered Features (Cloud)
                              </h3>
                              
                              <div className="grid grid-cols-3 gap-2">
                                <Button
                                  onClick={() => setShowOcrModal(true)}
                                  disabled={!isPdfSelected() || isAnyOperationLoading()}
                                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                                >
                                  {isOperationLoading('ocr-pdf') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔍'}
                                  <span className="ml-2">OCR PDF</span>
                                </Button>

                                <Button
                                  onClick={() => setShowExtractModal(true)}
                                  disabled={!isPdfSelected() || isAnyOperationLoading()}
                                  className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
                                >
                                  {isOperationLoading('extract-content') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔬'}
                                  <span className="ml-2">Extract Content</span>
                                </Button>

                                <Button
                                  onClick={() => setShowHtmlToPdfModal(true)}
                                  disabled={isAnyOperationLoading()}
                                  className="w-full bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700"
                                >
                                  {isOperationLoading('html-to-pdf') ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🌐'}
                                  <span className="ml-2">HTML → PDF</span>
                                </Button>
                              </div>
                              
                              <p className="text-xs text-gray-500 mt-2 italic">
                                ⚡ Powered by Adobe PDF Services API • 10/10 Quality • 500 free transactions/month
                              </p>
                            </div>
                          </div>

                          {/* PDF Operation Forms */}
                          {pdfOperation === 'split' && (
                            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-blue-900">✂️ Tách PDF</h4>
                              <input
                                type="text"
                                placeholder="Ví dụ: 1-3,5-7 (pages 1-3 và 5-7)"
                                value={pageRanges}
                                onChange={(e) => setPageRanges(e.target.value)}
                                className="w-full px-3 py-2 border border-blue-300 rounded text-sm"
                              />
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleSplitPdf}
                                  disabled={loading || !pageRanges.trim()}
                                  className="flex-1"
                                  size="sm"
                                >
                                  {loading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : '✂️'}
                                  Tách
                                </Button>
                                <Button
                                  onClick={() => setPdfOperation(null)}
                                  variant="outline"
                                  size="sm"
                                >
                                  Hủy
                                </Button>
                              </div>
                            </div>
                          )}

                          {pdfOperation === 'rotate' && (
                            <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-purple-900">🔄 Xoay PDF</h4>
                              <select
                                value={rotationAngle}
                                onChange={(e) => setRotationAngle(Number(e.target.value))}
                                className="w-full px-3 py-2 border border-purple-300 rounded text-sm"
                              >
                                <option value={90}>90° (phải)</option>
                                <option value={180}>180° (lật ngược)</option>
                                <option value={270}>270° (trái)</option>
                              </select>
                              <input
                                type="text"
                                placeholder="Trang cụ thể (ví dụ: 1,3,5) hoặc để trống = tất cả"
                                value={specificPages}
                                onChange={(e) => setSpecificPages(e.target.value)}
                                className="w-full px-3 py-2 border border-purple-300 rounded text-sm"
                              />
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleRotatePdf}
                                  disabled={loading}
                                  className="flex-1"
                                  size="sm"
                                >
                                  {loading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : '🔄'}
                                  Xoay
                                </Button>
                                <Button
                                  onClick={() => setPdfOperation(null)}
                                  variant="outline"
                                  size="sm"
                                >
                                  Hủy
                                </Button>
                              </div>
                            </div>
                          )}

                          {pdfOperation === 'watermark' && (
                            <div className="p-3 bg-green-50 border border-green-200 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-green-900">🖨️ Thêm Watermark</h4>
                              <input
                                type="text"
                                placeholder="Nhập text watermark..."
                                value={watermarkText}
                                onChange={(e) => setWatermarkText(e.target.value)}
                                className="w-full px-3 py-2 border border-green-300 rounded text-sm"
                              />
                              <select
                                value={watermarkPosition}
                                onChange={(e) => setWatermarkPosition(e.target.value)}
                                className="w-full px-3 py-2 border border-green-300 rounded text-sm"
                              >
                                <option value="center">Giữa</option>
                                <option value="top-left">Trên trái</option>
                                <option value="top-right">Trên phải</option>
                                <option value="bottom-left">Dưới trái</option>
                                <option value="bottom-right">Dưới phải</option>
                              </select>
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleAddWatermark}
                                  disabled={loading || !watermarkText.trim()}
                                  className="flex-1"
                                  size="sm"
                                >
                                  {loading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : '🖨️'}
                                  Thêm
                                </Button>
                                <Button
                                  onClick={() => setPdfOperation(null)}
                                  variant="outline"
                                  size="sm"
                                >
                                  Hủy
                                </Button>
                              </div>
                            </div>
                          )}

                          {pdfOperation === 'protect' && (
                            <div className="p-3 bg-red-50 border border-red-200 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-red-900">🔒 Bảo vệ PDF</h4>
                              <input
                                type="password"
                                placeholder="Nhập password..."
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-3 py-2 border border-red-300 rounded text-sm"
                              />
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleProtectPdf}
                                  disabled={loading || !password.trim()}
                                  className="flex-1"
                                  size="sm"
                                >
                                  {loading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : '🔒'}
                                  Bảo vệ
                                </Button>
                                <Button
                                  onClick={() => {
                                    setPdfOperation(null);
                                    setPassword('');
                                  }}
                                  variant="outline"
                                  size="sm"
                                >
                                  Hủy
                                </Button>
                              </div>
                            </div>
                          )}

                          {pdfOperation === 'unlock' && (
                            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-yellow-900">🔓 Mở khóa PDF</h4>
                              <input
                                type="password"
                                placeholder="Nhập password để mở khóa..."
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-3 py-2 border border-yellow-300 rounded text-sm"
                              />
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleUnlockPdf}
                                  disabled={loading || !password.trim()}
                                  className="flex-1"
                                  size="sm"
                                >
                                  {loading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : '🔓'}
                                  Mở khóa
                                </Button>
                                <Button
                                  onClick={() => {
                                    setPdfOperation(null);
                                    setPassword('');
                                  }}
                                  variant="outline"
                                  size="sm"
                                >
                                  Hủy
                                </Button>
                              </div>
                            </div>
                          )}

                          {pdfOperation === 'to-images' && (
                            <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-indigo-900">🖼️ Chuyển sang Images</h4>
                              <div className="flex gap-2">
                                <label className="flex items-center gap-2 cursor-pointer">
                                  <input
                                    type="radio"
                                    value="png"
                                    checked={imageFormat === 'png'}
                                    onChange={(e) => setImageFormat(e.target.value)}
                                    className="w-4 h-4"
                                  />
                                  <span className="text-sm">PNG</span>
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer">
                                  <input
                                    type="radio"
                                    value="jpg"
                                    checked={imageFormat === 'jpg'}
                                    onChange={(e) => setImageFormat(e.target.value)}
                                    className="w-4 h-4"
                                  />
                                  <span className="text-sm">JPG</span>
                                </label>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  onClick={handlePdfToImages}
                                  disabled={loading}
                                  className="flex-1"
                                  size="sm"
                                >
                                  {loading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : '🖼️'}
                                  Chuyển
                                </Button>
                                <Button
                                  onClick={() => setPdfOperation(null)}
                                  variant="outline"
                                  size="sm"
                                >
                                  Hủy
                                </Button>
                              </div>
                            </div>
                          )}

                          {pdfOperation === 'page-numbers' && (
                            <div className="p-3 bg-teal-50 border border-teal-200 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-teal-900">🔢 Thêm Số Trang</h4>
                              <select
                                value={watermarkPosition}
                                onChange={(e) => setWatermarkPosition(e.target.value)}
                                className="w-full px-3 py-2 border border-teal-300 rounded text-sm"
                              >
                                <option value="bottom-center">Dưới giữa</option>
                                <option value="bottom-left">Dưới trái</option>
                                <option value="bottom-right">Dưới phải</option>
                              </select>
                              <input
                                type="text"
                                placeholder='Ví dụ: "Page {page} of {total}"'
                                value={pageNumberFormat}
                                onChange={(e) => setPageNumberFormat(e.target.value)}
                                className="w-full px-3 py-2 border border-teal-300 rounded text-sm"
                              />
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleAddPageNumbers}
                                  disabled={loading}
                                  className="flex-1"
                                  size="sm"
                                >
                                  {loading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : '🔢'}
                                  Thêm
                                </Button>
                                <Button
                                  onClick={() => setPdfOperation(null)}
                                  variant="outline"
                                  size="sm"
                                >
                                  Hủy
                                </Button>
                              </div>
                            </div>
                          )}

                          {/* NEW: OCR Modal */}
                          {showOcrModal && (
                            <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-300 rounded-lg space-y-3 shadow-lg">
                              <h4 className="text-lg font-bold text-purple-900 flex items-center gap-2">
                                🔍 OCR - Nhận Dạng Chữ (Adobe AI)
                              </h4>
                              <p className="text-sm text-purple-700">
                                Chuyển đổi PDF scan thành PDF có thể tìm kiếm và copy text. Hỗ trợ 50+ ngôn ngữ.
                              </p>
                              <div>
                                <label className="block text-sm font-semibold text-purple-900 mb-2">
                                  📝 Chọn Ngôn Ngữ:
                                </label>
                                <select
                                  value={ocrLanguage}
                                  onChange={(e) => setOcrLanguage(e.target.value)}
                                  className="w-full px-4 py-3 border-2 border-purple-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                >
                                  <option value="vi-VN">🇻🇳 Tiếng Việt (Vietnamese)</option>
                                  <option value="en-US">🇺🇸 English (US)</option>
                                  <option value="en-GB">🇬🇧 English (UK)</option>
                                  <option value="fr-FR">🇫🇷 Français (French)</option>
                                  <option value="de-DE">🇩🇪 Deutsch (German)</option>
                                  <option value="es-ES">🇪🇸 Español (Spanish)</option>
                                  <option value="it-IT">🇮🇹 Italiano (Italian)</option>
                                  <option value="ja-JP">🇯🇵 日本語 (Japanese)</option>
                                  <option value="ko-KR">🇰🇷 한국어 (Korean)</option>
                                  <option value="zh-CN">🇨🇳 简体中文 (Chinese Simplified)</option>
                                  <option value="zh-TW">🇹🇼 繁體中文 (Chinese Traditional)</option>
                                  <option value="th-TH">🇹🇭 ไทย (Thai)</option>
                                  <option value="ru-RU">🇷🇺 Русский (Russian)</option>
                                  <option value="ar-SA">🇸🇦 العربية (Arabic)</option>
                                </select>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleOcrPdf}
                                  disabled={loading || !isPdfSelected()}
                                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                                >
                                  {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔍'}
                                  Bắt Đầu OCR
                                </Button>
                                <Button
                                  onClick={() => setShowOcrModal(false)}
                                  variant="outline"
                                  className="border-purple-300 text-purple-700 hover:bg-purple-100"
                                >
                                  Đóng
                                </Button>
                              </div>
                              <p className="text-xs text-purple-600 italic">
                                ⚡ AI-powered • 10/10 accuracy • Preserves original layout
                              </p>
                            </div>
                          )}

                          {/* NEW: Extract Content Modal */}
                          {showExtractModal && (
                            <div className="p-4 bg-gradient-to-br from-indigo-50 to-blue-50 border-2 border-indigo-300 rounded-lg space-y-3 shadow-lg">
                              <h4 className="text-lg font-bold text-indigo-900 flex items-center gap-2">
                                🔬 Extract Content (Adobe AI)
                              </h4>
                              <p className="text-sm text-indigo-700">
                                Trích xuất thông minh: tables → Excel data, images → PNG files, text với font info
                              </p>
                              <div>
                                <label className="block text-sm font-semibold text-indigo-900 mb-2">
                                  📦 Loại nội dung cần trích xuất:
                                </label>
                                <select
                                  value={extractType}
                                  onChange={(e) => setExtractType(e.target.value)}
                                  className="w-full px-4 py-3 border-2 border-indigo-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                >
                                  <option value="all">📚 All - Toàn bộ (text, tables, images)</option>
                                  <option value="text">📝 Text Only - Chỉ text với font information</option>
                                  <option value="tables">📊 Tables Only - Chỉ bảng biểu (Excel format)</option>
                                  <option value="images">🖼️ Images Only - Chỉ hình ảnh (PNG files)</option>
                                </select>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleExtractContent}
                                  disabled={loading || !isPdfSelected()}
                                  className="flex-1 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
                                >
                                  {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔬'}
                                  Trích Xuất
                                </Button>
                                <Button
                                  onClick={() => setShowExtractModal(false)}
                                  variant="outline"
                                  className="border-indigo-300 text-indigo-700 hover:bg-indigo-100"
                                >
                                  Đóng
                                </Button>
                              </div>
                              <p className="text-xs text-indigo-600 italic">
                                ⚡ AI-powered structure detection • Character bounding boxes • Data mining ready
                              </p>
                            </div>
                          )}

                          {/* NEW: HTML to PDF Modal */}
                          {showHtmlToPdfModal && (
                            <div className="p-4 bg-gradient-to-br from-green-50 to-teal-50 border-2 border-green-300 rounded-lg space-y-3 shadow-lg">
                              <h4 className="text-lg font-bold text-green-900 flex items-center gap-2">
                                🌐 HTML to PDF (Adobe CreatePDF)
                              </h4>
                              <p className="text-sm text-green-700">
                                Perfect rendering with full CSS3 support. Ideal for invoices, reports, certificates.
                              </p>
                              <div>
                                <label className="block text-sm font-semibold text-green-900 mb-2">
                                  📄 HTML Content:
                                </label>
                                <textarea
                                  value={htmlContent}
                                  onChange={(e) => setHtmlContent(e.target.value)}
                                  placeholder={`<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial; margin: 20px; }
    h1 { color: #333; }
  </style>
</head>
<body>
  <h1>My Document</h1>
  <p>Content here...</p>
</body>
</html>`}
                                  className="w-full px-4 py-3 border-2 border-green-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                  rows={8}
                                />
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className="block text-sm font-semibold text-green-900 mb-2">
                                    📏 Page Size:
                                  </label>
                                  <select
                                    value={htmlPageSize}
                                    onChange={(e) => setHtmlPageSize(e.target.value)}
                                    className="w-full px-3 py-2 border-2 border-green-300 rounded-lg text-sm"
                                  >
                                    <option value="A4">A4 (210mm × 297mm)</option>
                                    <option value="Letter">Letter (8.5in × 11in)</option>
                                    <option value="Legal">Legal (8.5in × 14in)</option>
                                    <option value="A3">A3 (297mm × 420mm)</option>
                                  </select>
                                </div>
                                <div>
                                  <label className="block text-sm font-semibold text-green-900 mb-2">
                                    🔄 Orientation:
                                  </label>
                                  <select
                                    value={htmlOrientation}
                                    onChange={(e) => setHtmlOrientation(e.target.value)}
                                    className="w-full px-3 py-2 border-2 border-green-300 rounded-lg text-sm"
                                  >
                                    <option value="portrait">📄 Portrait (Vertical)</option>
                                    <option value="landscape">📃 Landscape (Horizontal)</option>
                                  </select>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  onClick={handleHtmlToPdf}
                                  disabled={loading || !htmlContent.trim()}
                                  className="flex-1 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700"
                                >
                                  {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🌐'}
                                  Convert to PDF
                                </Button>
                                <Button
                                  onClick={() => setShowHtmlToPdfModal(false)}
                                  variant="outline"
                                  className="border-green-300 text-green-700 hover:bg-green-100"
                                >
                                  Đóng
                                </Button>
                              </div>
                              <p className="text-xs text-green-600 italic">
                                ⚡ Chrome-quality rendering • Full CSS3 & JavaScript support • Perfect for invoices
                              </p>
                            </div>
                          )}

                          {/* NEW: PDF to Word OCR Options Modal */}
                          {showPdfToWordModal && (
                            <div 
                              data-modal="pdf-to-word"
                              className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-300 rounded-lg space-y-3 shadow-lg animate-in slide-in-from-top duration-300"
                            >
                              <h4 className="text-lg font-bold text-blue-900 flex items-center gap-2">
                                📝 PDF → Word Conversion Options
                              </h4>
                              <p className="text-sm text-blue-700">
                                Chọn công nghệ chuyển đổi tốt nhất cho PDF của bạn.
                              </p>
                              
                              {/* NEW: Gemini API Option */}
                              <div className="space-y-3">
                                <label className="flex items-center gap-3 p-3 bg-gradient-to-r from-emerald-50 to-green-50 border-2 border-emerald-200 rounded-lg cursor-pointer hover:bg-emerald-100 transition-colors">
                                  <input
                                    type="checkbox"
                                    checked={useGemini}
                                    onChange={(e) => setUseGemini(e.target.checked)}
                                    className="w-5 h-5 text-emerald-600 rounded focus:ring-2 focus:ring-emerald-500"
                                  />
                                  <div>
                                    <span className="text-sm font-bold text-emerald-900 block">
                                      ⭐ Sử dụng Gemini API (KHUYẾN NGHỊ)
                                    </span>
                                    <span className="text-xs text-emerald-700 block">
                                      🇻🇳 Hỗ trợ Tiếng Việt • 📊 Xuất sắc cho bảng biểu • � Multiple models to choose
                                    </span>
                                    <span className="text-xs text-emerald-600 italic">
                                      Native PDF reading, không cần OCR preprocessing
                                    </span>
                                  </div>
                                </label>

                                {/* Model Selector - Only show when Gemini is enabled */}
                                {useGemini && (
                                  <div className="bg-white rounded-lg p-4 border-2 border-emerald-200">
                                    <GeminiModelSelector
                                      value={geminiModel}
                                      onChange={setGeminiModel}
                                      showDetails={true}
                                      disabled={loading}
                                    />
                                  </div>
                                )}
                              </div>

                              {/* Separator when Gemini is not selected */}
                              {!useGemini && (
                                <div className="flex items-center gap-3">
                                  <div className="flex-1 h-px bg-gray-300"></div>
                                  <span className="text-xs text-gray-500 bg-white px-2">HOẶC</span>
                                  <div className="flex-1 h-px bg-gray-300"></div>
                                </div>
                              )}

                              {/* Adobe OCR Options (only show if Gemini not selected) */}
                              {!useGemini && (
                                <>
                                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                                    <p className="text-xs text-amber-800 font-semibold mb-1">
                                      ⚠️ Adobe PDF Services không hỗ trợ Tiếng Việt!
                                    </p>
                                    <p className="text-xs text-amber-700">
                                      Nếu PDF có nội dung Tiếng Việt, vui lòng chọn Gemini API ở trên.
                                    </p>
                                  </div>

                                  <div className="space-y-2">
                                    <label className="flex items-center gap-3 p-3 bg-white border-2 border-blue-200 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors">
                                      <input
                                        type="checkbox"
                                        checked={autoDetectScanned}
                                        onChange={(e) => setAutoDetectScanned(e.target.checked)}
                                        className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                      />
                                      <div>
                                        <span className="text-sm font-semibold text-blue-900 block">
                                          🤖 Tự động phát hiện PDF scan
                                        </span>
                                        <span className="text-xs text-blue-600">
                                          Tự động bật OCR nếu PDF không có text layer (khuyến nghị)
                                        </span>
                                      </div>
                                    </label>
                                    
                                    {/* Manual OCR enable option */}
                                    <label className="flex items-center gap-3 p-3 bg-white border-2 border-blue-200 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors">
                                      <input
                                        type="checkbox"
                                        checked={enableOcr}
                                        onChange={(e) => setEnableOcr(e.target.checked)}
                                        className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                      />
                                      <div>
                                        <span className="text-sm font-semibold text-blue-900 block">
                                          🔍 Bật OCR thủ công
                                        </span>
                                        <span className="text-xs text-blue-600">
                                          Bắt buộc sử dụng OCR cho tất cả PDF (bỏ qua auto-detect)
                                        </span>
                                      </div>
                                    </label>
                                  </div>

                                  {/* Language selection (shown if either option enabled) */}
                                  {(enableOcr || autoDetectScanned) && (
                                    <div>
                                      <label className="block text-sm font-semibold text-blue-900 mb-2">
                                        🌐 Ngôn ngữ OCR (Adobe - KHÔNG bao gồm Tiếng Việt):
                                      </label>
                                      <select
                                        value={ocrLanguage}
                                        onChange={(e) => setOcrLanguage(e.target.value)}
                                        className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                      >
                                        <option value="en-US">🇺🇸 English (US)</option>
                                        <option value="en-GB">🇬🇧 English (UK)</option>
                                        <option value="fr-FR">🇫🇷 Français (French)</option>
                                        <option value="de-DE">🇩🇪 Deutsch (German)</option>
                                        <option value="es-ES">🇪🇸 Español (Spanish)</option>
                                        <option value="it-IT">🇮🇹 Italiano (Italian)</option>
                                        <option value="ja-JP">🇯🇵 日本語 (Japanese)</option>
                                        <option value="ko-KR">🇰🇷 한국어 (Korean)</option>
                                        <option value="zh-CN">🇨🇳 简体中文 (Chinese Simplified)</option>
                                        <option value="zh-TW">🇹🇼 繁體中文 (Chinese Traditional)</option>
                                        <option value="th-TH">🇹🇭 ไทย (Thai)</option>
                                        <option value="ru-RU">🇷🇺 Русский (Russian)</option>
                                        <option value="ar-SA">🇸🇦 العربية (Arabic)</option>
                                      </select>
                                      <p className="text-xs text-red-600 mt-1 italic font-semibold">
                                        ❌ Adobe KHÔNG hỗ trợ Tiếng Việt. Sử dụng Gemini để xử lý Tiếng Việt!
                                      </p>
                                    </div>
                                  )}
                                </>
                              )}

                              {/* Action buttons */}
                              <div className="flex gap-2">
                                <Button
                                  onClick={() => {
                                    setShowPdfToWordModal(false);
                                    handlePdfToWord();
                                  }}
                                  disabled={loading}
                                  className={`flex-1 ${
                                    useGemini 
                                      ? 'bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700'
                                      : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700'
                                  }`}
                                >
                                  {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : (useGemini ? '⭐' : '📝')}
                                  {useGemini ? 'Chuyển Đổi với Gemini' : 'Chuyển Đổi với Adobe'}
                                </Button>
                                <Button
                                  onClick={() => setShowPdfToWordModal(false)}
                                  variant="outline"
                                  className="border-blue-300 text-blue-700 hover:bg-blue-100"
                                >
                                  Hủy
                                </Button>
                              </div>
                              
                              {/* Info text - Dynamic based on selection */}
                              <div className={`border rounded-lg p-3 space-y-1 ${
                                useGemini 
                                  ? 'bg-emerald-100 border-emerald-300'
                                  : 'bg-blue-100 border-blue-300'
                              }`}>
                                {useGemini ? (
                                  <>
                                    <p className="text-xs text-emerald-800 font-semibold">
                                      ⭐ Gemini API - Giải pháp tốt nhất cho Tiếng Việt:
                                    </p>
                                    <ul className="text-xs text-emerald-700 space-y-1 ml-4 list-disc">
                                      <li><strong>✅ Hỗ trợ Tiếng Việt:</strong> 100+ ngôn ngữ bao gồm Vietnamese</li>
                                      <li><strong>📊 Xuất sắc cho bảng:</strong> Hiểu layout & structure tốt hơn</li>
                                      <li><strong>💰 Rẻ hơn 85%:</strong> $6.43/30k pages vs Google Vision $43.50</li>
                                      <li><strong>🚀 Không cần OCR:</strong> Đọc PDF trực tiếp, nhanh hơn</li>
                                    </ul>
                                  </>
                                ) : (
                                  <>
                                    <p className="text-xs text-blue-800 font-semibold">
                                      ℹ️ Adobe PDF Services - Cách hoạt động:
                                    </p>
                                    <ul className="text-xs text-blue-700 space-y-1 ml-4 list-disc">
                                      <li><strong>Auto-detect ON:</strong> Tự động kiểm tra PDF có text layer không, bật OCR nếu cần</li>
                                      <li><strong>Manual OCR ON:</strong> Luôn sử dụng OCR cho tất cả PDF</li>
                                      <li><strong>Cả hai OFF:</strong> Chuyển đổi trực tiếp không OCR (nhanh hơn cho PDF bình thường)</li>
                                    </ul>
                                  </>
                                )}
                              </div>

                              <p className={`text-xs italic text-center ${
                                useGemini ? 'text-emerald-600' : 'text-blue-600'
                              }`}>
                                {useGemini 
                                  ? '⚡ Google Gemini • Native PDF understanding • 100+ languages • $6.43/30k pages'
                                  : '⚡ Adobe AI-powered • One-step OCR + Conversion • NO Vietnamese support'
                                }
                              </p>
                            </div>
                          )}

                          <div className="space-y-1">
                            <Button
                              onClick={() => setPdfOperation('merge')}
                              disabled={loading}
                              className="w-full"
                              variant="secondary"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                              <span className="ml-2">Gộp nhiều PDF</span>
                            </Button>
                            {pdfOperation === 'merge' && (
                              <p className="text-xs text-gray-600 px-2">
                                💡 Chuyển sang chế độ multi-file upload bên trái
                              </p>
                            )}
                          </div>

                          <div className="p-2 bg-green-50 border border-green-200 rounded text-xs text-green-800">
                            ✅ <strong>Mới:</strong> 16 Tính năng PDF! (Nén, Tách, Xoay, Gộp, Watermark, Password, Unlock, PDF↔Excel, PDF↔Word, Images, Page Numbers)
                          </div>
                        </div>
                      );
                    }

                    // UNSUPPORTED FILE
                    return (
                      <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg text-center">
                        <p className="text-sm text-orange-800 mb-2">
                          ⚠️ File type không được hỗ trợ
                        </p>
                        <p className="text-xs text-orange-700">
                          Hỗ trợ: Word (.docx), Excel (.xlsx), PowerPoint (.pptx), PDF
                        </p>
                      </div>
                    );
                  }

                  // IMAGES TAB
                  if (activeTab === 'images') {
                    if (!selectedFile) {
                      return (
                        <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg text-center">
                          <p className="text-sm text-purple-800">
                            🖼️ Upload một ảnh để xem các thao tác khả dụng
                          </p>
                        </div>
                      );
                    }
                    
                    if (fileType === 'image') {
                      return (
                        <div className="space-y-3">
                          <div className="p-3 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg">
                            <p className="text-sm font-semibold text-purple-900 mb-1">
                              🖼️ File ảnh được phát hiện
                            </p>
                            <p className="text-xs text-purple-700">
                              Các thao tác được đề xuất cho ảnh:
                            </p>
                          </div>
                          
                          <div className="space-y-2">
                            <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                              Xử lý ảnh
                            </h3>
                            <div className="space-y-1">
                              <Button
                                onClick={handleImageResize}
                                disabled={loading}
                                className="w-full bg-purple-600 hover:bg-purple-700"
                              >
                                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📏'}
                                <span className="ml-2">Resize (800px width)</span>
                              </Button>
                              <div className="flex items-center justify-center gap-2 text-xs">
                                <span className="text-gray-500">Powered by:</span>
                                <TechnologyBadge tech="pillow" showQuality size="small" />
                              </div>
                            </div>
                            <Button
                              onClick={handleRemoveBackground}
                              disabled={loading}
                              className="w-full"
                              variant="secondary"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '✂️'}
                              <span className="ml-2">Remove Background (AI)</span>
                            </Button>
                          </div>

                          <div className="space-y-2">
                            <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                              Chuyển đổi
                            </h3>
                            <div className="space-y-1">
                              <Button
                                onClick={handleImageToPdf}
                                disabled={loading}
                                className="w-full"
                                variant="outline"
                              >
                                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📄'}
                                <span className="ml-2">Chuyển sang PDF</span>
                              </Button>
                              <div className="flex items-center justify-center gap-2 text-xs">
                                <span className="text-gray-500">Powered by:</span>
                                <TechnologyBadge tech="pillow" showQuality size="small" />
                              </div>
                            </div>
                            
                            <Button
                              onClick={() => {
                                setBatchMode(true);
                                setBatchOperation('image-to-pdf');
                                setBatchFiles([selectedFile]);
                              }}
                              disabled={loading}
                              className="w-full bg-gradient-to-r from-orange-600 to-pink-600 hover:from-orange-700 hover:to-pink-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                              <span className="ml-2">Chuyển NHIỀU ảnh → PDF</span>
                            </Button>
                          </div>

                          <div className="p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
                            ⏱️ <strong>Lưu ý:</strong> AI background removal có thể mất 10-30 giây
                          </div>

                          <div className="p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-800">
                            💡 <strong>Tip:</strong> Chuyển sang tab OCR để trích xuất text từ ảnh!
                          </div>
                        </div>
                      );
                    }
                    
                    return (
                      <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg text-center">
                        <p className="text-sm text-orange-800 mb-2">
                          ⚠️ File không phải là ảnh
                        </p>
                        <p className="text-xs text-orange-700">
                          Hỗ trợ: JPG, PNG, GIF, WebP, BMP, HEIC
                        </p>
                      </div>
                    );
                  }

                  // OCR TAB
                  if (activeTab === 'ocr') {
                    if (!selectedFile) {
                      return (
                        <div className="p-4 bg-cyan-50 border border-cyan-200 rounded-lg text-center">
                          <p className="text-sm text-cyan-800">
                            🔍 Upload một ảnh để trích xuất text
                          </p>
                        </div>
                      );
                    }
                    
                    if (fileType === 'image') {
                      return (
                        <div className="space-y-3">
                          <div className="p-3 bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200 rounded-lg">
                            <p className="text-sm font-semibold text-cyan-900 mb-1">
                              🔍 File ảnh được phát hiện
                            </p>
                            <p className="text-xs text-cyan-700">
                              Sử dụng AI OCR để trích xuất text:
                            </p>
                          </div>
                          
                          <div className="space-y-1">
                            <Button
                              onClick={handleOCR}
                              disabled={loading}
                              className="w-full bg-cyan-600 hover:bg-cyan-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔍'}
                              <span className="ml-2">Trích Xuất Text (VI + EN)</span>
                            </Button>
                            <div className="flex items-center justify-center gap-2 text-xs">
                              <span className="text-gray-500">Powered by:</span>
                              <TechnologyBadge tech="tesseract" showQuality size="small" />
                              <span className="text-gray-400">→</span>
                              <TechnologyBadge tech="adobe" showQuality size="small" />
                            </div>
                          </div>

                          <div className="p-2 bg-green-50 border border-green-200 rounded text-xs text-green-800">
                            🌍 <strong>Hỗ trợ:</strong> Tiếng Việt, English, và 80+ ngôn ngữ khác
                          </div>

                          <div className="p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
                            ⏱️ <strong>Lưu ý:</strong> OCR có thể mất 5-15 giây tùy độ phức tạp
                          </div>
                        </div>
                      );
                    }
                    
                    return (
                      <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg text-center">
                        <p className="text-sm text-orange-800 mb-2">
                          ⚠️ File không phải là ảnh
                        </p>
                        <p className="text-xs text-orange-700">
                          OCR chỉ hoạt động với file ảnh (JPG, PNG, etc.)
                        </p>
                      </div>
                    );
                  }

                  return null;
                })()}

                {activeTab === 'documents' && (
                  <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                    <p className="text-xs text-gray-600">
                      ⚡ <strong>Powered by:</strong> Gotenberg (LibreOffice headless)
                    </p>
                  </div>
                )}
            </div>
          </CardContent>
        </Card>
      </div>
      )}

      {/* Progress Indicator */}
      {loading && currentTechnology && (
        <Card className="mt-6">
          <CardContent className="pt-6">
            <ConversionProgress
              tech={currentTechnology}
              status={uploadProgress < 100 ? 'uploading' : 'processing'}
              progress={Math.max(uploadProgress, processingProgress)}
            />
            
            <div className="mt-4 text-center text-sm text-gray-600">
              {uploadProgress < 100
                ? `📤 Đang tải lên... ${uploadProgress}%`
                : `⚙️ Đang xử lý file... ${processingProgress}%`
              }
              {processingTime > 0 && (
                <span className="ml-2 text-gray-500">
                  ({(processingTime / 1000).toFixed(1)}s)
                </span>
              )}
            </div>
            
            {abortController && (
              <div className="mt-4 flex justify-center">
                <Button
                  onClick={handleCancelOperation}
                  variant="outline"
                  size="sm"
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-300"
                >
                  ❌ Hủy Thao Tác
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Fallback loading indicator without technology (for legacy operations) */}
      {loading && !currentTechnology && (
        <Card className="mt-6">
          <CardContent className="pt-6">
            <div className="space-y-4">
              {/* Operation Name */}
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  {currentOperation || 'Đang xử lý...'}
                </h3>
                <span className="text-sm text-gray-500">
                  {processingTime > 0 ? `${(processingTime / 1000).toFixed(1)}s` : '0.0s'}
                </span>
              </div>

              {/* Upload Progress */}
              {uploadProgress > 0 && uploadProgress < 100 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">📤 Đang tải lên...</span>
                    <span className="font-semibold text-blue-600">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Processing Progress */}
              {uploadProgress >= 100 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">⚙️ Đang xử lý file...</span>
                    <span className="font-semibold text-green-600">{processingProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-gradient-to-r from-green-500 to-emerald-500 h-2.5 rounded-full transition-all duration-300 animate-pulse"
                      style={{ width: `${processingProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Spinning Loader with Cancel Button */}
              <div className="flex items-center justify-center gap-4 py-4">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                {abortController && (
                  <Button
                    onClick={handleCancelOperation}
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-300"
                  >
                    ❌ Hủy
                  </Button>
                )}
              </div>

              {/* Status Message */}
              <p className="text-sm text-center text-gray-500">
                Vui lòng đợi, đang xử lý file của bạn...
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileType className="w-5 h-5" />
              Kết Quả Xử Lý
            </CardTitle>
          </CardHeader>
          <CardContent>
            {result.type === 'download' && result.technology && (
              <ConversionResult
                filename={result.outputFile}
                fileSize={result.outputSize}
                tech={result.technology}
                quality={result.quality}
                processingTime={result.processingTime / 1000}
                quotaRemaining={result.quotaRemaining}
                downloadUrl={result.downloadUrl}
                onConvertAnother={() => {
                  setResult(null);
                  setSelectedFile(null);
                }}
              />
            )}
            
            {result.type === 'download' && !result.technology && (
              <div className="space-y-4">
                {/* Success Banner */}
                <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-green-900 mb-1">
                        ✨ {result.action} Thành Công!
                      </h3>
                      <p className="text-sm text-green-700">
                        File đã được tải xuống và sẵn sàng sử dụng
                      </p>
                    </div>
                  </div>
                </div>

                {/* File Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Input File */}
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                      <Upload className="w-4 h-4" />
                      File Gốc
                    </h4>
                    <div className="space-y-1 text-sm">
                      <p className="text-blue-800">
                        <span className="font-medium">Tên:</span> {result.originalFile}
                      </p>
                      <p className="text-blue-800">
                        <span className="font-medium">Kích thước:</span> {(result.originalSize / 1024).toFixed(2)} KB
                      </p>
                      <p className="text-blue-800">
                        <span className="font-medium">Định dạng:</span> {result.originalFile.split('.').pop()?.toUpperCase()}
                      </p>
                    </div>
                  </div>

                  {/* Output File */}
                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      File Đã Chuyển Đổi
                    </h4>
                    <div className="space-y-1 text-sm">
                      <p className="text-purple-800">
                        <span className="font-medium">Tên:</span> {result.outputFile}
                      </p>
                      <p className="text-purple-800">
                        <span className="font-medium">Kích thước:</span> {(result.outputSize / 1024).toFixed(2)} KB
                      </p>
                      <p className="text-purple-800">
                        <span className="font-medium">Định dạng:</span> {result.outputFile.split('.').pop()?.toUpperCase()}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Processing Stats */}
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Thống Kê Xử Lý
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">
                        {(result.processingTime / 1000).toFixed(2)}s
                      </p>
                      <p className="text-xs text-gray-600">Thời gian xử lý</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">
                        {result.compressionRatio > 0 ? '+' : ''}{Math.abs(parseFloat(result.compressionRatio)).toFixed(1)}%
                      </p>
                      <p className="text-xs text-gray-600">
                        {result.compressionRatio > 0 ? 'Tăng' : 'Giảm'} kích thước
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-600">
                        {((result.originalSize / 1024 / (result.processingTime / 1000))).toFixed(1)}
                      </p>
                      <p className="text-xs text-gray-600">KB/giây</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-orange-600">
                        ⚡
                      </p>
                      <p className="text-xs text-gray-600">Gotenberg Engine</p>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <Button
                    onClick={() => {
                      const link = document.createElement('a');
                      link.href = result.downloadUrl;
                      link.download = result.outputFile;
                      link.click();
                    }}
                    className="flex-1"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Tải Lại File
                  </Button>
                  <Button
                    onClick={() => {
                      setResult(null);
                      setSelectedFile(null);
                    }}
                    variant="outline"
                  >
                    Chuyển Đổi File Khác
                  </Button>
                </div>
              </div>
            )}

            {result.type === 'error' && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-10 h-10 bg-red-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-red-900 mb-1">
                      ❌ Chuyển Đổi Thất Bại
                    </h3>
                    <p className="text-sm text-red-700 mb-2">{result.message}</p>
                    <p className="text-xs text-red-600">File: {result.originalFile}</p>
                  </div>
                </div>
              </div>
            )}

            {result.type === 'text' && (
              <div className="space-y-4">
                {/* Success Banner */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-blue-900 mb-1">
                        📄 {result.action} Thành Công!
                      </h3>
                      <p className="text-sm text-blue-700">
                        Đã trích xuất text từ PDF
                      </p>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-center">
                    <p className="text-2xl font-bold text-blue-600">{result.data.num_pages || 'N/A'}</p>
                    <p className="text-xs text-gray-600">Trang</p>
                  </div>
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-600">{result.data.word_count || 'N/A'}</p>
                    <p className="text-xs text-gray-600">Từ</p>
                  </div>
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-center">
                    <p className="text-2xl font-bold text-purple-600">{result.data.char_count || 'N/A'}</p>
                    <p className="text-xs text-gray-600">Ký tự</p>
                  </div>
                  <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg text-center">
                    <p className="text-2xl font-bold text-orange-600">{(result.processingTime / 1000).toFixed(2)}s</p>
                    <p className="text-xs text-gray-600">Thời gian</p>
                  </div>
                </div>

                {/* Extracted Text */}
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Text Đã Trích Xuất:</h4>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        navigator.clipboard.writeText(result.data.text);
                        toast.success('Copied to clipboard!');
                      }}
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy
                    </Button>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono leading-relaxed">
                      {result.data.text}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {result.type === 'info' && (
              <div className="space-y-4">
                {/* Success Banner */}
                <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-indigo-900 mb-1">
                        ℹ️ Thông Tin PDF
                      </h3>
                      <p className="text-sm text-indigo-700">
                        {result.originalFile}
                      </p>
                    </div>
                  </div>
                </div>

                {/* PDF Metadata */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-white border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-3">📑 Thông Tin Cơ Bản</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Số trang:</span>
                        <span className="font-medium">{result.data.num_pages}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Mã hóa:</span>
                        <span className={`font-medium ${result.data.encrypted ? 'text-red-600' : 'text-green-600'}`}>
                          {result.data.encrypted ? '🔒 Có' : '🔓 Không'}
                        </span>
                      </div>
                      {result.data.author && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Tác giả:</span>
                          <span className="font-medium">{result.data.author}</span>
                        </div>
                      )}
                      {result.data.title && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Tiêu đề:</span>
                          <span className="font-medium">{result.data.title}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="p-4 bg-white border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-3">📐 Kích Thước Trang</h4>
                    <div className="space-y-2">
                      {result.data.page_sizes && result.data.page_sizes.slice(0, 5).map((size: any, idx: number) => (
                        <div key={idx} className="flex justify-between text-sm">
                          <span className="text-gray-600">Trang {idx + 1}:</span>
                          <span className="font-medium font-mono">
                            {size.width.toFixed(1)} × {size.height.toFixed(1)} pt
                          </span>
                        </div>
                      ))}
                      {result.data.page_sizes && result.data.page_sizes.length > 5 && (
                        <p className="text-xs text-gray-500 text-center mt-2">
                          ... và {result.data.page_sizes.length - 5} trang nữa
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Processing Time */}
                <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-center">
                  <p className="text-sm text-gray-600">
                    ⚡ Xử lý trong <span className="font-bold text-gray-900">{(result.processingTime / 1000).toFixed(2)}s</span>
                  </p>
                </div>
              </div>
            )}

            {result.type === 'text' && result.data.num_detections && (
              <div>
                <div className="mb-4">
                  <p className="text-sm text-muted-foreground mb-2">
                    Detected {result.data.num_detections} text blocks (Avg confidence: {(result.data.avg_confidence * 100).toFixed(1)}%)
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium mb-2">Extracted Text:</h3>
                  <pre className="whitespace-pre-wrap text-sm">{result.data.text}</pre>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
