/**
 * Document Tools Hub - Trang xử lý tài liệu tổng hợp
 * Features: Convert, Merge, Split files (DOC, PDF, Images)
 * Responsive: Mobile-first design
 */
import { useState } from 'react';
import { 
  FileText, FileImage, FileSpreadsheet, 
  Scissors, Link as LinkIcon, RotateCw,
  Upload, Download, Trash2, Plus, Settings,
  ChevronDown, ChevronUp, Search, Zap
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import toast from 'react-hot-toast';

// API Base URL - SAME AS ToolsPage
const API_BASE = API_BASE_URL;

// Tool configuration
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
    description: 'Chuyển PDF sang Word có thể chỉnh sửa (OCR tiếng Việt)',
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

export default function DocumentToolsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'convert' | 'edit' | 'batch'>('all');
  const [expandedTool, setExpandedTool] = useState<string | null>(null);

  // Debug logging
  console.log('🔧 DocumentToolsPage - API_BASE:', API_BASE);
  console.log('🔧 Total tools:', TOOLS.length);

  // Filter tools
  const filteredTools = TOOLS.filter(tool => {
    const matchCategory = selectedCategory === 'all' || tool.category === selectedCategory;
    const matchSearch = tool.nameVi.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       tool.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchCategory && matchSearch;
  });
  
  console.log('🔧 Filtered tools:', filteredTools.length);

  // Category counts
  const categoryCounts = {
    all: TOOLS.length,
    convert: TOOLS.filter(t => t.category === 'convert').length,
    edit: TOOLS.filter(t => t.category === 'edit').length,
    batch: TOOLS.filter(t => t.category === 'batch').length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-3">
            🛠️ Công cụ xử lý tài liệu
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm md:text-base">
            Chuyển đổi, ghép, tách file Word, PDF, Excel, Ảnh - Nhanh chóng & Miễn phí
          </p>
        </div>

        {/* Search & Filter */}
        <div className="mb-6 space-y-4">
          {/* Search bar */}
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Tìm kiếm công cụ... (VD: word, ghép pdf, chuyển đổi)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 h-12 text-base"
            />
          </div>

          {/* Category filter */}
          <div className="flex flex-wrap gap-2 justify-center">
            {(['all', 'convert', 'edit', 'batch'] as const).map((cat) => {
              const labels = {
                all: 'Tất cả',
                convert: '🔄 Chuyển đổi',
                edit: '✂️ Chỉnh sửa',
                batch: '⚡ Hàng loạt'
              };
              
              return (
                <Button
                  key={cat}
                  variant={selectedCategory === cat ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(cat)}
                  className="rounded-full"
                >
                  {labels[cat]}
                  <Badge variant="secondary" className="ml-2 text-xs">
                    {categoryCounts[cat]}
                  </Badge>
                </Button>
              );
            })}
          </div>
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          {filteredTools.map((tool) => (
            <ToolCard 
              key={tool.id} 
              tool={tool}
              isExpanded={expandedTool === tool.id}
              onToggle={() => setExpandedTool(expandedTool === tool.id ? null : tool.id)}
            />
          ))}
        </div>

        {/* Empty state */}
        {filteredTools.length === 0 && (
          <div className="text-center py-16">
            <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Không tìm thấy công cụ phù hợp</p>
            <Button 
              variant="link" 
              onClick={() => { setSearchTerm(''); setSelectedCategory('all'); }}
              className="mt-2"
            >
              Xóa bộ lọc
            </Button>
          </div>
        )}
      </div>
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

  const handleProcess = async () => {
    if (files.length === 0) {
      toast.error('Vui lòng chọn file');
      return;
    }

    setIsProcessing(true);
    const formData = new FormData();
    
    if (tool.multiple) {
      files.forEach(file => formData.append('files', file));
    } else {
      formData.append('file', files[0]);
    }

    // Special handling for split PDF
    if (tool.id === 'split-pdf' && splitPages) {
      formData.append('pages', splitPages);
    }

    try {
      // USE SAME PATTERN AS ToolsPage - axios with API_BASE
      const response = await axios.post(
        `${API_BASE}${tool.endpoint}`,
        formData,
        {
          responseType: 'blob', // CRITICAL: Force blob response
        }
      );

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Smart filename detection based on TOOL CATEGORY
      let outputExt = 'pdf'; // Default
      if (tool.id === 'pdf-to-word') {
        outputExt = 'docx';
      } else if (tool.id.startsWith('batch-') && tool.id.includes('word')) {
        outputExt = 'zip'; // Batch operations return zip
      }
      
      link.download = `output_${Date.now()}.${outputExt}`;
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url); // Cleanup
      
      toast.success(`✅ ${tool.nameVi} thành công!`);
      setFiles([]);
      setSplitPages('');
    } catch (error: any) {
      console.error('Conversion error:', error);
      const errorMsg = error.response?.data?.detail || error.message || `Lỗi ${tool.nameVi}`;
      toast.error(`❌ ${errorMsg}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card className={`transition-all duration-200 ${colorClasses[tool.color as keyof typeof colorClasses]}`}>
      <CardHeader className="cursor-pointer" onClick={onToggle}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3 flex-1">
            <div className={`p-2 rounded-lg bg-${tool.color}-100 dark:bg-${tool.color}-900/20`}>
              <Icon className={`h-6 w-6 text-${tool.color}-600 dark:text-${tool.color}-400`} />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base md:text-lg truncate">{tool.nameVi}</CardTitle>
              <CardDescription className="text-xs md:text-sm line-clamp-2">
                {tool.description}
              </CardDescription>
            </div>
          </div>
          {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-4">
          {/* File upload */}
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
              <div className="mt-2 space-y-1">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
                    <span className="truncate flex-1">{file.name}</span>
                    <span className="text-gray-500 ml-2">{(file.size / 1024).toFixed(1)} KB</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Split PDF options */}
          {tool.id === 'split-pdf' && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Chọn trang (VD: 1-3, 5, 7-9)
              </label>
              <Input
                type="text"
                placeholder="1-5, 7, 10-15"
                value={splitPages}
                onChange={(e) => setSplitPages(e.target.value)}
              />
            </div>
          )}

          {/* Process button */}
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

          {/* Clear button */}
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
