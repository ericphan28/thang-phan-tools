// frontend/src/components/TechnologyBadge.tsx
import React from 'react';

export type TechnologyType = 'adobe' | 'gotenberg' | 'pdf2docx' | 'pdfplumber' | 'gemini' | 'claude' | 'pypdf' | 'tesseract' | 'pillow' | 'reportlab' | 'pypdfium2' | 'matplotlib';

interface TechnologyBadgeProps {
  tech: TechnologyType;
  size?: 'small' | 'medium' | 'large' | 'lg';
  showQuality?: boolean;
}

const TECH_CONFIG = {
  adobe: {
    name: 'Adobe PDF Services',
    icon: '🌟',
    color: '#FF0000',
    bgColor: '#FFE6E6',
    quality: 'Premium',
    description: 'AI-powered, best quality'
  },
  gotenberg: {
    name: 'Gotenberg',
    icon: '⚡',
    color: '#0066FF',
    bgColor: '#E6F0FF',
    quality: 'Fast',
    description: 'Fast & reliable'
  },
  pdf2docx: {
    name: 'pdf2docx',
    icon: '📦',
    color: '#6B7280',
    bgColor: '#F3F4F6',
    quality: 'Standard',
    description: 'Good quality, offline'
  },
  pdfplumber: {
    name: 'pdfplumber',
    icon: '📊',
    color: '#10B981',
    bgColor: '#D1FAE5',
    quality: 'Standard',
    description: 'Table extraction'
  },
  gemini: {
    name: 'Google Gemini',
    icon: '⭐',
    color: '#34D399',
    bgColor: '#ECFDF5',
    quality: 'Premium',
    description: 'Best for Vietnamese, tables'
  },
  claude: {
    name: 'Anthropic Claude',
    icon: '✨',
    color: '#A855F7',
    bgColor: '#F3E8FF',
    quality: 'Premium',
    description: 'High accuracy OCR'
  },
  pypdf: {
    name: 'PyPDF',
    icon: '✅',
    color: '#8B5CF6',
    bgColor: '#F3E8FF',
    quality: 'Standard',
    description: 'PDF manipulation'
  },
  tesseract: {
    name: 'Tesseract OCR',
    icon: '⚡',
    color: '#F59E0B',
    bgColor: '#FEF3C7',
    quality: 'Fast',
    description: 'Free OCR engine'
  },
  pillow: {
    name: 'Pillow',
    icon: '🖼️',
    color: '#EC4899',
    bgColor: '#FCE7F3',
    quality: 'Standard',
    description: 'Image processing'
  },
  reportlab: {
    name: 'ReportLab',
    icon: '📝',
    color: '#06B6D4',
    bgColor: '#CFFAFE',
    quality: 'Standard',
    description: 'PDF generation'
  },
  pypdfium2: {
    name: 'PyPDFium2',
    icon: '🔧',
    color: '#64748B',
    bgColor: '#F1F5F9',
    quality: 'Standard',
    description: 'PDF rendering'
  },
  matplotlib: {
    name: 'Matplotlib',
    icon: '📊',
    color: '#FF6B6B',
    bgColor: '#FFE8E8',
    quality: 'Premium',
    description: 'Data visualization'
  }
};

export const TechnologyBadge: React.FC<TechnologyBadgeProps> = ({
  tech,
  size = 'medium',
  showQuality = false
}) => {
  const config = TECH_CONFIG[tech];
  
  // Fallback for unknown tech
  if (!config) {
    console.warn(`Unknown technology type: ${tech}`);
    return (
      <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
        {tech}
      </span>
    );
  }
  
  const sizeStyles = {
    small: 'text-xs px-2 py-0.5',
    medium: 'text-sm px-3 py-1',
    large: 'text-base px-4 py-2',
    lg: 'text-base px-4 py-2'
  };

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizeStyles[size]}`}
      style={{
        backgroundColor: config.bgColor,
        color: config.color,
        border: `1px solid ${config.color}40`
      }}
    >
      <span className="text-base">{config.icon}</span>
      <span>{config.name}</span>
      {showQuality && (
        <span className="ml-1 opacity-75">{config.quality}</span>
      )}
    </div>
  );
};

// Conversion Type Card Component
interface ConversionCardProps {
  title: string;
  description: string;
  primaryTech: TechnologyType;
  fallbackTech?: TechnologyType;
  quality: string;
  speed: string;
  onSelect: () => void;
}

export const ConversionCard: React.FC<ConversionCardProps> = ({
  title,
  description,
  primaryTech,
  fallbackTech,
  quality,
  speed,
  onSelect
}) => {
  return (
    <div className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer bg-white">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900">{title}</h3>
        <div className="flex flex-col gap-2">
          <TechnologyBadge tech={primaryTech} showQuality />
          {fallbackTech && (
            <div className="flex items-center gap-1">
              <span className="text-xs text-gray-500">Fallback:</span>
              <TechnologyBadge tech={fallbackTech} size="small" />
            </div>
          )}
        </div>
      </div>
      
      <p className="text-gray-600 mb-4">{description}</p>
      
      <div className="flex items-center gap-4 mb-4 text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <span>⭐</span>
          <span>Quality: {quality}</span>
        </div>
        <div className="flex items-center gap-1">
          <span>⏱️</span>
          <span>Speed: {speed}</span>
        </div>
      </div>
      
      <button
        onClick={onSelect}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
      >
        Select Conversion
      </button>
    </div>
  );
};

// Conversion Progress Component
interface ConversionProgressProps {
  tech: TechnologyType;
  status: 'uploading' | 'processing' | 'downloading' | 'complete';
  progress: number;
}

export const ConversionProgress: React.FC<ConversionProgressProps> = ({
  tech,
  status,
  progress
}) => {
  const config = TECH_CONFIG[tech];
  
  const statusText = {
    uploading: 'Uploading file...',
    processing: `Processing with ${config.name}...`,
    downloading: 'Downloading result...',
    complete: 'Conversion complete!'
  };

  const statusIcon = {
    uploading: '📤',
    processing: '⚙️',
    downloading: '⬇️',
    complete: '✅'
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Converting...</h3>
        <TechnologyBadge tech={tech} size="small" />
      </div>
      
      {/* Progress Bar */}
      <div className="mb-4">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-300"
            style={{
              width: `${progress}%`,
              backgroundColor: config.color
            }}
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-500">
          <span>{progress}%</span>
          <span>{statusText[status]}</span>
        </div>
      </div>
      
      {/* Status Steps */}
      <div className="space-y-2">
        <div className={`flex items-center gap-2 ${status === 'uploading' ? 'text-blue-600 font-medium' : 'text-gray-400'}`}>
          <span>{statusIcon.uploading}</span>
          <span>Uploading file</span>
          {status !== 'uploading' && <span className="ml-auto">✓</span>}
        </div>
        <div className={`flex items-center gap-2 ${status === 'processing' ? 'text-blue-600 font-medium' : status === 'uploading' ? 'text-gray-400' : 'text-gray-400'}`}>
          <span>{statusIcon.processing}</span>
          <span>Processing with {config.icon} {config.name}</span>
          {['downloading', 'complete'].includes(status) && <span className="ml-auto">✓</span>}
        </div>
        <div className={`flex items-center gap-2 ${status === 'downloading' ? 'text-blue-600 font-medium' : status === 'complete' ? 'text-gray-400' : 'text-gray-400'}`}>
          <span>{statusIcon.downloading}</span>
          <span>Downloading result</span>
          {status === 'complete' && <span className="ml-auto">✓</span>}
        </div>
      </div>
    </div>
  );
};

// Conversion Result Component
interface ConversionResultProps {
  filename: string;
  fileSize: number;
  tech: TechnologyType;
  quality: string;
  processingTime: number;
  quotaRemaining?: string;
  downloadUrl: string;
  onConvertAnother: () => void;
}

export const ConversionResult: React.FC<ConversionResultProps> = ({
  filename,
  fileSize,
  tech,
  quality,
  processingTime,
  quotaRemaining,
  downloadUrl,
  onConvertAnother
}) => {
  const config = TECH_CONFIG[tech];
  
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
      <div className="text-center mb-6">
        <div className="text-6xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Conversion Complete!
        </h2>
        <p className="text-gray-600">Your file is ready to download</p>
      </div>
      
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-600">File:</span>
          <span className="text-sm text-gray-900">{filename}</span>
        </div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-600">Size:</span>
          <span className="text-sm text-gray-900">{formatFileSize(fileSize)}</span>
        </div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-600">Engine:</span>
          <TechnologyBadge tech={tech} size="small" />
        </div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-600">Quality:</span>
          <span className="text-sm font-medium text-green-600">
            {quality} ⭐⭐⭐⭐⭐
          </span>
        </div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-600">Time:</span>
          <span className="text-sm text-gray-900">{processingTime.toFixed(1)}s</span>
        </div>
        {quotaRemaining && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Quota:</span>
            <span className="text-sm text-gray-900">{quotaRemaining}</span>
          </div>
        )}
      </div>
      
      <div className="space-y-3">
        <a
          href={downloadUrl}
          download
          className="block w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg text-center transition-colors"
        >
          📥 Download File
        </a>
        <button
          onClick={onConvertAnother}
          className="block w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg text-center transition-colors"
        >
          🔄 Convert Another File
        </button>
      </div>
    </div>
  );
};

// Usage Example
export default function ConversionExample() {
  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold mb-8">Document Conversion</h1>
      
      {/* Conversion Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ConversionCard
          title="PDF → Word"
          description="Convert PDF to editable Word document with AI-powered layout preservation"
          primaryTech="adobe"
          fallbackTech="pdf2docx"
          quality="10/10"
          speed="5-10s"
          onSelect={() => console.log('Selected PDF to Word')}
        />
        
        <ConversionCard
          title="Word → PDF"
          description="Convert Word document to PDF with perfect format preservation"
          primaryTech="gotenberg"
          quality="9/10"
          speed="2-5s"
          onSelect={() => console.log('Selected Word to PDF')}
        />
        
        <ConversionCard
          title="PDF → Excel"
          description="Extract tables from PDF to Excel spreadsheet"
          primaryTech="pdfplumber"
          quality="8/10"
          speed="3-5s"
          onSelect={() => console.log('Selected PDF to Excel')}
        />
      </div>
      
      {/* Progress Example */}
      <ConversionProgress
        tech="adobe"
        status="processing"
        progress={65}
      />
      
      {/* Result Example */}
      <ConversionResult
        filename="document.docx"
        fileSize={45678}
        tech="adobe"
        quality="10/10"
        processingTime={8.2}
        quotaRemaining="498/500"
        downloadUrl="/downloads/document.docx"
        onConvertAnother={() => console.log('Convert another')}
      />
    </div>
  );
}
