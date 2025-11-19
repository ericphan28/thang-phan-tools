import { useState } from 'react';
import { Upload, FileText, Image, FileType, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export default function ToolsPage() {
  const [activeTab, setActiveTab] = useState<'documents' | 'images' | 'ocr'>('documents');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [processingTime, setProcessingTime] = useState<number>(0);
  
  // Progress tracking
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [processingProgress, setProcessingProgress] = useState<number>(0);
  const [currentOperation, setCurrentOperation] = useState<string>('');
  
  // Multi-file upload for Merge PDFs
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleMultipleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]); // Store first file for display
      setResult(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setResult(null);
    }
  };

  // Document: Word to PDF
  const handleWordToPdf = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation('Word → PDF');
    const startTime = Date.now();
    
    const uploadInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 100));
    }, 100);
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const timeInterval = setInterval(() => {
        setProcessingTime(Date.now() - startTime);
      }, 100);
      
      const response = await axios.post(`${API_BASE}/documents/convert/word-to-pdf`, formData, {
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
      setProcessingTime(processingTimeMs);

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

      toast.success('✅ Converted successfully!');
      setResult({
        type: 'download',
        action: 'Word → PDF Conversion',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: pdfSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - pdfSize / originalSize) * 100).toFixed(1),
        downloadUrl: url
      });
    } catch (error: any) {
      clearInterval(uploadInterval);
      const errorMsg = error.response?.data?.detail || 'Conversion failed';
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
    }
  };

  // Document: PDF to Word
  const handlePdfToWord = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation('PDF → Word');
    const startTime = Date.now();
    
    const uploadInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 100));
    }, 100);
    
    const formData = new FormData();
    formData.append('file', selectedFile);

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

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const outputFilename = selectedFile.name.replace(/\.\w+$/, '.docx');
      link.setAttribute('download', outputFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('✅ Converted to Word successfully!');
      setResult({
        type: 'download',
        action: 'PDF → Word Conversion',
        originalFile: selectedFile.name,
        originalSize: originalSize,
        outputFile: outputFilename,
        outputSize: docxSize,
        processingTime: processingTimeMs,
        compressionRatio: ((1 - docxSize / originalSize) * 100).toFixed(1),
        downloadUrl: url
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
    }
  };

  // Document: PDF to Excel
  const handlePdfToExcel = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setUploadProgress(0);
    setProcessingProgress(0);
    setCurrentOperation('PDF → Excel');
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
        downloadUrl: url
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

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Công Cụ Xử Lý File</h1>
        <p className="text-muted-foreground mt-2">
          Convert documents, process images, extract text from images
        </p>
      </div>

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
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Area */}
        <Card>
          <CardHeader>
            <CardTitle>
              {pdfOperation === 'merge' ? 'Upload Multiple PDFs' : 'Upload File'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {pdfOperation === 'merge' ? (
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
                        {selectedFiles.length} file(s) selected
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedFiles([])}
                      >
                        Clear All
                      </Button>
                    </div>
                    <div className="max-h-60 overflow-y-auto space-y-2">
                      {selectedFiles.map((file, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded border"
                        >
                          <div className="flex items-center gap-2 flex-1">
                            <span className="text-lg">📄</span>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium truncate">{file.name}</p>
                              <p className="text-xs text-gray-500">
                                {(file.size / 1024).toFixed(1)} KB
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== idx))}
                          >
                            ✕
                          </Button>
                        </div>
                      ))}
                    </div>
                    <Button
                      onClick={handleMergePdfs}
                      disabled={loading || selectedFiles.length < 2}
                      className="w-full"
                    >
                      {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📚'}
                      Merge {selectedFiles.length} PDFs
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
              // Single file upload (original)
              <div>
                <div
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
                  onClick={() => document.getElementById('fileInput')?.click()}
                >
                  <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium mb-2">
                    {selectedFile ? selectedFile.name : 'Click or drag file here'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {activeTab === 'documents' && 'Hỗ trợ: Word (.docx), Excel (.xlsx), PowerPoint (.pptx), PDF'}
                    {activeTab === 'images' && 'Supported: JPG, PNG, WebP, HEIC'}
                    {activeTab === 'ocr' && 'Supported: JPG, PNG (images with text)'}
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

                {selectedFile && (
                  <div className="mt-4">
                    <p className="text-sm text-muted-foreground mb-2">File size: {(selectedFile.size / 1024).toFixed(2)} KB</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedFile(null)}
                    >
                      Clear
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
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
                          
                          <Button
                            onClick={handleWordToPdf}
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-700"
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
                            <Button
                              onClick={handlePdfToWord}
                              disabled={loading}
                              className="w-full bg-red-600 hover:bg-red-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📝'}
                              <span className="ml-2">Chuyển sang Word</span>
                            </Button>
                            
                            <Button
                              onClick={handlePdfToExcel}
                              disabled={loading}
                              className="w-full bg-green-600 hover:bg-green-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📊'}
                              <span className="ml-2">Chuyển sang Excel</span>
                            </Button>
                          </div>

                          <div className="space-y-2">
                            <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                              Công cụ PDF
                            </h3>
                            <Button
                              onClick={handleExtractPdfText}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📝'}
                              <span className="ml-2">Trích xuất Text</span>
                            </Button>
                            
                            <Button
                              onClick={handlePdfInfo}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : 'ℹ️'}
                              <span className="ml-2">Xem Thông Tin PDF</span>
                            </Button>
                            
                            <Button
                              onClick={handleCompressPdf}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📦'}
                              <span className="ml-2">Nén PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('split')}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '✂️'}
                              <span className="ml-2">Tách PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('rotate')}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔄'}
                              <span className="ml-2">Xoay PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('watermark')}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🖨️'}
                              <span className="ml-2">Thêm Watermark</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('protect')}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔒'}
                              <span className="ml-2">Bảo vệ bằng Password</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('unlock')}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔓'}
                              <span className="ml-2">Mở khóa PDF</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('to-images')}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🖼️'}
                              <span className="ml-2">Chuyển sang Images</span>
                            </Button>
                            
                            <Button
                              onClick={() => setPdfOperation('page-numbers')}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔢'}
                              <span className="ml-2">Thêm Số Trang</span>
                            </Button>
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
                            <Button
                              onClick={handleImageResize}
                              disabled={loading}
                              className="w-full bg-purple-600 hover:bg-purple-700"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📏'}
                              <span className="ml-2">Resize (800px width)</span>
                            </Button>
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
                            <Button
                              onClick={handleImageToPdf}
                              disabled={loading}
                              className="w-full"
                              variant="outline"
                            >
                              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '📄'}
                              <span className="ml-2">Chuyển sang PDF</span>
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
                          
                          <Button
                            onClick={handleOCR}
                            disabled={loading}
                            className="w-full bg-cyan-600 hover:bg-cyan-700"
                          >
                            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : '🔍'}
                            <span className="ml-2">Trích Xuất Text (VI + EN)</span>
                          </Button>

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

      {/* Progress Indicator */}
      {loading && (
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

              {/* Spinning Loader */}
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
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
            {result.type === 'download' && (
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
