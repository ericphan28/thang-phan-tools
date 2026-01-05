import React from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText, AlertTriangle, Clock } from 'lucide-react';

interface FileSizeWarningProps {
  file: File | null;
  maxSizeRecommended?: number; // Default 50MB
  maxSizeAbsolute?: number; // Default 200MB
}

export const FileSizeWarning: React.FC<FileSizeWarningProps> = ({
  file,
  maxSizeRecommended = 50 * 1024 * 1024, // 50MB
  maxSizeAbsolute = 200 * 1024 * 1024, // 200MB
}) => {
  if (!file) return null;

  const fileSizeMB = file.size / (1024 * 1024);
  const estimatedTime = Math.max(30, Math.min(fileSizeMB * 10, 300)); // 30s to 5min

  // File too large (absolute limit)
  if (file.size > maxSizeAbsolute) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          <strong>File quá lớn!</strong>
          <br />
          File của bạn: <strong>{fileSizeMB.toFixed(1)} MB</strong>
          <br />
          Giới hạn tối đa: <strong>{maxSizeAbsolute / (1024*1024)} MB</strong>
          <br />
          Vui lòng sử dụng file nhỏ hơn hoặc chia nhỏ tài liệu.
        </AlertDescription>
      </Alert>
    );
  }

  // File large but acceptable (warning)
  if (file.size > maxSizeRecommended) {
    return (
      <Alert variant="warning" className="mb-4 border-yellow-200 bg-yellow-50">
        <Clock className="h-4 w-4 text-yellow-600" />
        <AlertDescription className="text-yellow-800">
          <strong>File khá lớn</strong>
          <br />
          Kích thước: <strong>{fileSizeMB.toFixed(1)} MB</strong>
          <br />
          Thời gian xử lý dự kiến: <strong>{Math.round(estimatedTime)} giây</strong>
          <br />
          💡 Để xử lý nhanh hơn, hãy sử dụng file dưới {maxSizeRecommended/(1024*1024)}MB
        </AlertDescription>
      </Alert>
    );
  }

  // File size OK (info)
  return (
    <Alert variant="default" className="mb-4 border-green-200 bg-green-50">
      <FileText className="h-4 w-4 text-green-600" />
      <AlertDescription className="text-green-800">
        <strong>Sẵn sàng xử lý</strong>
        <br />
        Kích thước: <strong>{fileSizeMB.toFixed(1)} MB</strong>
        <br />
        Thời gian dự kiến: <strong>{Math.round(estimatedTime)} giây</strong>
      </AlertDescription>
    </Alert>
  );
};

export default FileSizeWarning;