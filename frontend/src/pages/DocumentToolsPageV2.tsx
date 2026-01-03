/**
 * Document Tools Hub V2 - Tối ưu quota Adobe API
 * Chiến lược: Chỉ PDF→Word dùng Adobe (OCR tiếng Việt), còn lại dùng PyPDF2/Gotenberg
 * Tiết kiệm: ~75% quota Adobe (400 → 100 requests/tháng)
 */
import { useState } from 'react';
import { 
  FileText, FileImage, FileSpreadsheet, 
  Scissors, Link as LinkIcon, RotateCw,
  Upload, Download, Trash2, Zap, Sparkles,
  GripVertical, ArrowUp, ArrowDown
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import toast from 'react-hot-toast';

const API_BASE = API_BASE_URL;

interface Tool {
  id: string;
  name: string;
  nameVi: string;
  icon: any;
  description: string;
  category: 'convert' | 'edit' | 'batch';
  accept: string;
  multiple?: boolean;
  endpoint: string;
  color: string;
}

const TOOLS: Tool[] = [
  // CONVERT
  {
    id: 'word-to-pdf',
    name: 'Word to PDF',
    nameVi: 'Word → PDF',
    icon: FileText,
    description: 'Chuyển file Word (.doc, .docx) sang PDF với định dạng hoàn hảo',
    category: 'convert',
    accept: '.doc,.docx',
    endpoint: '/documents/convert/word-to-pdf',
    color: 'blue'
  },
  {
    id: 'pdf-to-word',
    name: 'PDF to Word',
    nameVi: 'PDF → Word',
    icon: FileText,
    description: 'Chuyển PDF sang Word có thể chỉnh sửa (OCR tiếng Việt chuyên nghiệp)',
    category: 'convert',
    accept: '.pdf',
    endpoint: '/documents/convert/pdf-to-word',
    color: 'blue'
  },
  {
    id: 'excel-to-pdf',
    name: 'Excel to PDF',
    nameVi: 'Excel → PDF',
    icon: FileSpreadsheet,
    description: 'Chuyển bảng tính Excel sang PDF',
    category: 'convert',
    accept: '.xls,.xlsx',
    endpoint: '/documents/convert/excel-to-pdf',
    color: 'green'
  },
  {
    id: 'image-to-pdf',
    name: 'Image to PDF',
    nameVi: 'Ảnh → PDF',
    icon: FileImage,
    description: 'Chuyển ảnh (JPG, PNG) sang PDF',
    category: 'convert',
    accept: '.jpg,.jpeg,.png',
    multiple: true,
    endpoint: '/documents/convert/image-to-pdf',
    color: 'purple'
  },
  
  // EDIT
  {
    id: 'merge-pdf',
    name: 'Merge PDFs',
    nameVi: 'Ghép PDF',
    icon: LinkIcon,
    description: 'Ghép nhiều file PDF thành một file',
    category: 'edit',
    accept: '.pdf',
    multiple: true,
    endpoint: '/documents/pdf/merge',
    color: 'orange'
  },
  {
    id: 'split-pdf',
    name: 'Split PDF',
    nameVi: 'Tách PDF',
    icon: Scissors,
    description: 'Tách file PDF thành nhiều file nhỏ theo trang',
    category: 'edit',
    accept: '.pdf',
    endpoint: '/documents/pdf/split',
    color: 'red'
  },
  {
    id: 'rotate-pdf',
    name: 'Rotate PDF',
    nameVi: 'Xoay PDF',
    icon: RotateCw,
    description: 'Xoay các trang PDF 90°, 180°, 270°',
    category: 'edit',
    accept: '.pdf',
    endpoint: '/documents/pdf/rotate',
    color: 'indigo'
  },
  
  // BATCH
  {
    id: 'batch-word-to-pdf',
    name: 'Batch Word→PDF',
    nameVi: 'Chuyển nhiều Word → PDF',
    icon: Zap,
    description: 'Chuyển đổi hàng loạt file Word sang PDF',
    category: 'batch',
    accept: '.doc,.docx',
    multiple: true,
    endpoint: '/documents/batch/word-to-pdf',
    color: 'cyan'
  },
  {
    id: 'merge-word-to-pdf',
    name: 'Merge Word→PDF',
    nameVi: 'Ghép Word → 1 PDF',
    icon: LinkIcon,
    description: 'Ghép nhiều file Word thành 1 file PDF duy nhất',
    category: 'batch',
    accept: '.doc,.docx',
    multiple: true,
    endpoint: '/documents/batch/merge-word-to-pdf',
    color: 'teal'
  },
];

export default function DocumentToolsPageV2() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'convert' | 'edit' | 'batch'>('all');
  const [expandedToolId, setExpandedToolId] = useState<string | null>(null);

  const filteredTools = TOOLS.filter(tool => {
    const matchesSearch = tool.nameVi.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tool.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-2 mb-3">
          <Sparkles className="h-8 w-8 text-yellow-500" />
          <h1 className="text-3xl md:text-4xl font-bold">Công cụ xử lý tài liệu</h1>
        </div>
        <p className="text-base md:text-lg text-gray-600 dark:text-gray-400 mb-4">
          Chuyển đổi, ghép, tách file Word, PDF, Excel, Ảnh - Nhanh chóng & Tiện lợi
        </p>
      </div>

      {/* Search & Filters */}
      <div className="mb-6 space-y-4">
        <Input
          type="text"
          placeholder="🔍 Tìm kiếm công cụ... (VD: word, ghép pdf, chuyển đổi)"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-2xl mx-auto"
        />
        
        <div className="flex flex-wrap justify-center gap-2">
          <Button
            variant={selectedCategory === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory('all')}
          >
            Tất cả ({TOOLS.length})
          </Button>
          <Button
            variant={selectedCategory === 'convert' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory('convert')}
          >
            🔄 Chuyển đổi ({TOOLS.filter(t => t.category === 'convert').length})
          </Button>
          <Button
            variant={selectedCategory === 'edit' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory('edit')}
          >
            ✂️ Chỉnh sửa ({TOOLS.filter(t => t.category === 'edit').length})
          </Button>
          <Button
            variant={selectedCategory === 'batch' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory('batch')}
          >
            ⚡ Hàng loạt ({TOOLS.filter(t => t.category === 'batch').length})
          </Button>
        </div>
      </div>

      {/* Tools Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTools.map((tool) => (
          <ToolCard
            key={tool.id}
            tool={tool}
            isExpanded={expandedToolId === tool.id}
            onToggle={() => setExpandedToolId(expandedToolId === tool.id ? null : tool.id)}
          />
        ))}
      </div>

      {/* No results */}
      {filteredTools.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Không tìm thấy công cụ phù hợp
          </p>
          <Button
            variant="outline"
            onClick={() => { setSearchTerm(''); setSelectedCategory('all'); }}
          >
            Xóa bộ lọc
          </Button>
        </div>
      )}
    </div>
  );
}

// Tool Card Component
function ToolCard({ tool, isExpanded, onToggle }: { 
  tool: Tool; 
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const [files, setFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [splitPages, setSplitPages] = useState('');
  const [rotationAngle, setRotationAngle] = useState(90);
  const [rotatePages, setRotatePages] = useState('');
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  const Icon = tool.icon;
  
  const colorClasses = {
    blue: 'border-blue-200 hover:border-blue-400 dark:border-blue-800',
    green: 'border-green-200 hover:border-green-400 dark:border-green-800',
    purple: 'border-purple-200 hover:border-purple-400 dark:border-purple-800',
    orange: 'border-orange-200 hover:border-orange-400 dark:border-orange-800',
    red: 'border-red-200 hover:border-red-400 dark:border-red-800',
    indigo: 'border-indigo-200 hover:border-indigo-400 dark:border-indigo-800',
    cyan: 'border-cyan-200 hover:border-cyan-400 dark:border-cyan-800',
    teal: 'border-teal-200 hover:border-teal-400 dark:border-teal-800',
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const moveFile = (fromIndex: number, toIndex: number) => {
    const newFiles = [...files];
    const [movedFile] = newFiles.splice(fromIndex, 1);
    newFiles.splice(toIndex, 0, movedFile);
    setFiles(newFiles);
  };

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex !== null && draggedIndex !== index) {
      moveFile(draggedIndex, index);
      setDraggedIndex(index);
    }
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const handleProcess = async () => {
    if (files.length === 0) {
      toast.error('Vui lòng chọn file');
      return;
    }
    
    if (tool.id === 'split-pdf' && !splitPages.trim()) {
      toast.error('⚠️ Vui lòng nhập khoảng trang cần tách (VD: 1-3,5-7)');
      return;
    }
    
    setIsProcessing(true);
    const formData = new FormData();
    
    if (tool.multiple) {
      files.forEach(file => formData.append('files', file));
    } else {
      formData.append('file', files[0]);
    }

    if (tool.id === 'split-pdf' && splitPages) {
      formData.append('page_ranges', splitPages);
    }

    if (tool.id === 'rotate-pdf') {
      formData.append('rotation', rotationAngle.toString());
      if (rotatePages.trim()) {
        formData.append('pages', rotatePages.trim());
      }
    }

    try {
      const response = await axios.post(
        `${API_BASE}${tool.endpoint}`,
        formData,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      let filename = null;
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const matches = /filename\*?=(?:UTF-8'')?([^;]+)/.exec(contentDisposition);
        if (matches && matches[1]) {
          filename = decodeURIComponent(matches[1].replace(/['"]/g, ''));
        }
      }
      
      if (!filename) {
        let outputExt = 'pdf';
        if (tool.id === 'pdf-to-word') outputExt = 'docx';
        else if (tool.id === 'split-pdf' || tool.id === 'merge-pdf') outputExt = 'zip';
        else if (tool.id.startsWith('batch-')) outputExt = 'zip';
        filename = `output_${Date.now()}.${outputExt}`;
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`✅ ${tool.nameVi} thành công!`, { duration: 3000 });
      setFiles([]);
      setSplitPages('');
      setRotatePages('');
    } catch (error: any) {
      let errorMsg = `Lỗi ${tool.nameVi}`;
      
      if (error.response?.data) {
        const data = error.response.data;
        
        if (data instanceof Blob) {
          try {
            const text = await data.text();
            try {
              const json = JSON.parse(text);
              errorMsg = json.detail || json.message || text;
            } catch {
              errorMsg = text;
            }
          } catch (blobError) {
            console.error('Failed to read Blob:', blobError);
          }
        } else {
          if (typeof data === 'string') errorMsg = data;
          else if (data.detail) errorMsg = data.detail;
          else if (data.message) errorMsg = data.message;
        }
      }
      
      toast.error(errorMsg, {
        duration: 8000,
        style: { maxWidth: '600px', whiteSpace: 'pre-line' }
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card className={`${colorClasses[tool.color]} transition-all`}>
      <CardHeader className="cursor-pointer" onClick={onToggle}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1">
            <div className={`p-2 rounded-lg bg-${tool.color}-100 dark:bg-${tool.color}-900/20`}>
              <Icon className={`h-5 w-5 text-${tool.color}-600 dark:text-${tool.color}-400`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <CardTitle className="text-base md:text-lg truncate">{tool.nameVi}</CardTitle>
              </div>
              <CardDescription className="text-xs md:text-sm line-clamp-2">
                {tool.description}
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              {tool.multiple ? 'Chọn file (nhiều file)' : 'Chọn file'}
            </label>
            <Input
              type="file"
              accept={tool.accept}
              multiple={tool.multiple}
              onChange={handleFileChange}
              className="cursor-pointer"
            />
            {files.length > 0 && (
              <div className="mt-3 space-y-2">
                {tool.id === 'merge-word-to-pdf' && (
                  <div className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-3 py-2 rounded-md">
                    <GripVertical className="h-4 w-4" />
                    <span>Kéo thả để sắp xếp thứ tự ghép PDF</span>
                  </div>
                )}
                <div className="space-y-1">
                  {files.map((file, idx) => (
                    <div
                      key={idx}
                      draggable={tool.id === 'merge-word-to-pdf'}
                      onDragStart={() => handleDragStart(idx)}
                      onDragOver={(e) => handleDragOver(e, idx)}
                      onDragEnd={handleDragEnd}
                      className={`flex items-center gap-2 text-xs bg-gray-50 dark:bg-gray-800 px-2 py-2 rounded transition-all ${
                        tool.id === 'merge-word-to-pdf' ? 'cursor-move hover:bg-gray-100 dark:hover:bg-gray-700' : ''
                      } ${
                        draggedIndex === idx ? 'opacity-50 scale-95' : ''
                      }`}
                    >
                      {tool.id === 'merge-word-to-pdf' && (
                        <>
                          <GripVertical className="h-4 w-4 text-gray-400" />
                          <span className="font-semibold text-blue-600 dark:text-blue-400 min-w-[20px]">{idx + 1}.</span>
                        </>
                      )}
                      <span className="truncate flex-1">{file.name}</span>
                      <span className="text-gray-500 ml-2">{(file.size / 1024).toFixed(1)} KB</span>
                      {tool.id === 'merge-word-to-pdf' && (
                        <div className="flex gap-1">
                          {idx > 0 && (
                            <button
                              onClick={() => moveFile(idx, idx - 1)}
                              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                              title="Di chuyển lên"
                            >
                              <ArrowUp className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                            </button>
                          )}
                          {idx < files.length - 1 && (
                            <button
                              onClick={() => moveFile(idx, idx + 1)}
                              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                              title="Di chuyển xuống"
                            >
                              <ArrowDown className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {tool.id === 'split-pdf' && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Chọn trang <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                placeholder="1-3,5-7,10-12 (phân cách bằng dấu phẩy)"
                value={splitPages}
                onChange={(e) => setSplitPages(e.target.value)}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                💡 Mỗi khoảng trang sẽ tạo 1 file PDF riêng. Kết quả: file ZIP chứa tất cả PDF đã tách.
              </p>
            </div>
          )}

          {tool.id === 'rotate-pdf' && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Góc xoay <span className="text-red-500">*</span>
                </label>
                <select
                  value={rotationAngle}
                  onChange={(e) => setRotationAngle(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-indigo-500"
                >
                  <option value={90}>90° ↻ (Xoay phải)</option>
                  <option value={180}>180° ↻ (Lật ngược)</option>
                  <option value={270}>270° ↻ (Xoay trái)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Trang cần xoay (tùy chọn)
                </label>
                <Input
                  type="text"
                  placeholder="1,3,5 hoặc để trống = tất cả trang"
                  value={rotatePages}
                  onChange={(e) => setRotatePages(e.target.value)}
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  💡 Nhập số trang cách nhau bằng dấu phẩy (VD: 1,3,5). Để trống = xoay tất cả trang.
                </p>
              </div>
            </div>
          )}

          <Button
            onClick={handleProcess}
            disabled={isProcessing || files.length === 0}
            className="w-full"
          >
            {isProcessing ? (
              <>
                <RotateCw className="mr-2 h-4 w-4 animate-spin" />
                Đang xử lý...
              </>
            ) : (
              <>
                <Zap className="mr-2 h-4 w-4" />
                Xử lý ngay
              </>
            )}
          </Button>

          {files.length > 0 && !isProcessing && (
            <Button
              variant="outline"
              onClick={() => setFiles([])}
              className="w-full"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Xóa file
            </Button>
          )}
        </CardContent>
      )}
    </Card>
  );
}
