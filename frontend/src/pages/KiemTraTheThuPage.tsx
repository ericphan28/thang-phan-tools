import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import api from '@/services/api';
import { toast } from 'react-hot-toast';

interface ViPhamTheThu {
  thanh_phan: string;
  mo_ta: string;
  muc_do: 'CAO' | 'TRUNG_BINH' | 'THAP';
  goi_y_sua?: string;
}

interface KetQuaKiemTra {
  success: boolean;
  van_ban_id?: number;
  tong_diem: number;
  loai_van_ban: string;
  vi_pham: ViPhamTheThu[];
  dat_yeu_cau: string[];
  message?: string;
}

const KiemTraTheThuPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<KetQuaKiemTra | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleCheckDocument = async () => {
    if (!file) {
      toast.error('Vui lòng chọn file văn bản');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('chi_tiet_cao', 'false');
    formData.append('luu_database', 'true');

    try {
      const response = await api.post('/vb-hanh-chinh/check-the-thuc', formData);
      setResult(response.data);
      
      if (response.data.tong_diem >= 80) {
        toast.success(`✅ Văn bản đạt ${response.data.tong_diem}/100 điểm`);
      } else {
        toast.error(`⚠️ Văn bản cần sửa: ${response.data.tong_diem}/100 điểm`);
      }
    } catch (error: any) {
      console.error('Error checking document:', error);
      toast.error(error.response?.data?.detail || 'Không thể kiểm tra văn bản');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const getMucDoColor = (mucDo: string) => {
    switch (mucDo) {
      case 'CAO':
        return 'border-red-500 bg-red-50';
      case 'TRUNG_BINH':
        return 'border-orange-500 bg-orange-50';
      case 'THAP':
        return 'border-yellow-500 bg-yellow-50';
      default:
        return 'border-gray-500 bg-gray-50';
    }
  };

  const getMucDoIcon = (mucDo: string) => {
    switch (mucDo) {
      case 'CAO':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'TRUNG_BINH':
        return <AlertCircle className="h-5 w-5 text-orange-600" />;
      case 'THAP':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold mb-3 flex items-center gap-3">
          <FileText className="h-8 w-8 md:h-10 md:w-10 text-blue-600" />
          Kiểm tra thể thức văn bản
        </h1>
        <p className="text-gray-600 text-base md:text-lg">
          Kiểm tra văn bản hành chính theo <strong>Nghị định 30/2020/NĐ-CP</strong> của Chính phủ
        </p>
      </div>

      {/* Upload Area */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Upload văn bản</CardTitle>
          <CardDescription>
            Hỗ trợ: PDF, DOCX, JPG, PNG (tối đa 10MB)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors
              ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="flex flex-col items-center gap-3">
                <FileText className="h-12 w-12 text-blue-600" />
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <Button variant="outline" onClick={() => setFile(null)} size="sm">
                  Chọn file khác
                </Button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <Upload className="h-12 w-12 text-gray-400" />
                <p className="text-gray-600">
                  Kéo thả file vào đây hoặc{' '}
                  <label className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium">
                    chọn file
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
                      onChange={handleFileChange}
                    />
                  </label>
                </p>
              </div>
            )}
          </div>

          <Button
            onClick={handleCheckDocument}
            disabled={!file || loading}
            className="w-full mt-4"
            size="lg"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
                Đang kiểm tra...
              </>
            ) : (
              'Kiểm tra ngay'
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <CardTitle className="text-2xl flex items-center gap-2">
                  Kết quả kiểm tra
                  {result.tong_diem >= 80 ? (
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  ) : (
                    <AlertCircle className="h-6 w-6 text-orange-600" />
                  )}
                </CardTitle>
                <CardDescription>
                  Loại văn bản: <strong>{result.loai_van_ban}</strong>
                </CardDescription>
              </div>
              <div className="text-right">
                <div
                  className={`text-4xl font-bold ${
                    result.tong_diem >= 80
                      ? 'text-green-600'
                      : result.tong_diem >= 60
                      ? 'text-orange-600'
                      : 'text-red-600'
                  }`}
                >
                  {result.tong_diem}/100
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {result.tong_diem >= 80
                    ? '✅ Đạt yêu cầu'
                    : result.tong_diem >= 60
                    ? '⚠️ Cần cải thiện'
                    : '❌ Cần sửa lại'}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Vi phạm */}
            {result.vi_pham.length > 0 ? (
              <div>
                <h3 className="font-semibold text-lg mb-3 text-red-700">
                  ❌ Vi phạm thể thức ({result.vi_pham.length})
                </h3>
                <div className="space-y-3">
                  {result.vi_pham.map((viPham, idx) => (
                    <div
                      key={idx}
                      className={`border-l-4 p-4 rounded-r-lg ${getMucDoColor(viPham.muc_do)}`}
                    >
                      <div className="flex items-start gap-3">
                        {getMucDoIcon(viPham.muc_do)}
                        <div className="flex-1">
                          <p className="font-semibold text-gray-900 mb-1">
                            {viPham.thanh_phan.replace(/_/g, ' ').toUpperCase()}
                          </p>
                          <p className="text-gray-700 mb-2">{viPham.mo_ta}</p>
                          {viPham.goi_y_sua && (
                            <div className="mt-2 p-2 bg-white rounded border border-green-300">
                              <p className="text-sm text-green-700">
                                <strong>💡 Gợi ý sửa:</strong> {viPham.goi_y_sua}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="border-2 border-green-500 bg-green-50 rounded-lg p-4 flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                <p className="text-green-800 font-medium">
                  Không phát hiện vi phạm thể thức!
                </p>
              </div>
            )}

            {/* Đạt yêu cầu */}
            <div>
              <h3 className="font-semibold text-lg mb-3 text-green-700">
                ✅ Các thành phần đạt yêu cầu ({result.dat_yeu_cau.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.dat_yeu_cau.map((item, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                  >
                    {item.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-lg">📋 10 thành phần thể thức được kiểm tra</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            <li>1. Quốc hiệu và Tiêu ngữ</li>
            <li>2. Tên cơ quan ban hành</li>
            <li>3. Số ký hiệu văn bản</li>
            <li>4. Ngày tháng ban hành</li>
            <li>5. Trích yếu nội dung</li>
            <li>6. Nội dung văn bản (cấu trúc)</li>
            <li>7. Chức vụ và người ký</li>
            <li>8. Nơi nhận</li>
            <li>9. Font chữ và trình bày</li>
            <li>10. Các thành phần bổ sung</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default KiemTraTheThuPage;
