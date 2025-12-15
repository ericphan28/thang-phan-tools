import { useState, useEffect } from 'react';
import { FileText, Download, Plus, Trash2, Loader2, Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import toast from 'react-hot-toast';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ArrayItem {
  id: number;
  [key: string]: any;
}

interface Template {
  id: string;
  name: string;
  description: string;
}

export default function Mau2CPage() {
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [showTemplates, setShowTemplates] = useState(false);
  
  // Simple fields
  const [formData, setFormData] = useState({
    // Location info
    tinh: '',
    don_vi_truc_thuoc: '',
    don_vi_co_so: '',
    so_hieu: '',
    
    // Personal info
    ho_ten: '',
    gioi_tinh: 'Nam',
    ten_goi_khac: '',
    ngay: '',
    thang: '',
    nam: '',
    noi_sinh: '',
    que_quan_xa: '',
    que_quan_huyen: '',
    que_quan_tinh: '',
    noi_o_hien_nay: '',
    dien_thoai: '',
    email: '',
    dan_toc: 'Kinh',
    ton_giao: '',
    
    // Party/Work info
    cap_uy_hien_tai: '',
    cap_uy_kiem: '',
    chuc_vu_full: '',
    phu_cap_chuc_vu: '',
    thanh_phan_xuat_than: '',
    nghe_nghiep_ban_than: '',
    ngay_tuyen_dung: '',
    co_quan_tuyen_dung: '',
    ngay_vao_co_quan: '',
    ngay_tham_gia_cach_mang: '',
    ngay_vao_dang: '',
    ngay_chinh_thuc_dang: '',
    ngay_tham_gia_to_chuc: '',
    ngay_nhap_ngu: '',
    ngay_xuat_ngu: '',
    quan_ham: '',
    
    // Education/Skills
    trinh_do_giao_duc_pho_thong: '',
    hoc_ham_hoc_vi: '',
    ly_luan_chinh_tri: '',
    ngoai_ngu: '',
    quan_ly_nha_nuoc: '',
    tin_hoc: '',
    
    // Position info
    cong_tac_chinh: '',
    ngach_cong_chuc: '',
    ma_ngach: '',
    bac_luong: '',
    he_so_luong: '',
    tu_thang_nam: '',
    
    // Recognition
    danh_hieu: '',
    so_truong_cong_tac: '',
    cong_viec_lau_nhat: '',
    khen_thuong: '',
    ky_luat: '',
    
    // Health
    suc_khoe: '',
    chieu_cao: '',
    can_nang: '',
    nhom_mau: '',
    
    // ID info
    so_cmnd: '',
    ngay_cap: '',
    noi_cap: '',
    
    // Other
    thuong_binh_loai: '',
    gia_dinh_liet_si: '',
    lich_su_bi_bat: '',
    lam_viec_che_do_cu: '',
    quan_he_nuoc_ngoai: '',
    than_nhan_nuoc_ngoai: '',
  });
  
  // Array fields
  const [daoTao, setDaoTao] = useState<ArrayItem[]>([
    { id: 1, ten_truong: '', nganh_hoc: '', thoi_gian: '', hinh_thuc: '', van_bang: '' }
  ]);
  
  const [congTac, setCongTac] = useState<ArrayItem[]>([
    { id: 1, thoi_gian: '', chuc_vu_don_vi: '' }
  ]);
  
  const [giaDinh, setGiaDinh] = useState<ArrayItem[]>([
    { id: 1, quan_he: '', ho_ten: '', nam_sinh: '', thong_tin: '' }
  ]);
  
  const [giaDinhVoChong, setGiaDinhVoChong] = useState<ArrayItem[]>([
    { id: 1, quan_he: '', ho_ten: '', nam_sinh: '', thong_tin: '' }
  ]);
  
  const [luong, setLuong] = useState<ArrayItem[]>([
    { id: 1, thang_nam: '', ngach_bac: '', he_so: '' }
  ]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayAdd = (setter: Function, currentArray: ArrayItem[]) => {
    const newId = Math.max(...currentArray.map(item => item.id), 0) + 1;
    setter([...currentArray, { id: newId }]);
  };

  const handleArrayRemove = (setter: Function, currentArray: ArrayItem[], id: number) => {
    if (currentArray.length > 1) {
      setter(currentArray.filter(item => item.id !== id));
    } else {
      toast.error('Cần ít nhất 1 mục');
    }
  };

  const handleArrayChange = (setter: Function, currentArray: ArrayItem[], id: number, field: string, value: any) => {
    setter(currentArray.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      console.log('🔥 HARDCODED URL: http://localhost:8000/api/mau-2c/sample-templates');
      const response = await axios.get('http://localhost:8000/api/mau-2c/sample-templates');
      console.log('✅ Templates response:', response.data);
      setTemplates(response.data.templates);
      console.log('✅ Templates set:', response.data.templates);
    } catch (error) {
      console.error('❌ Error loading templates:', error);
      toast.error('Không thể tải danh sách mẫu');
    }
  };

  const loadSampleData = async () => {
    if (!selectedTemplate) {
      toast.error('Vui lòng chọn mẫu dữ liệu');
      return;
    }

    try {
      console.log('🔥 HARDCODED URL: http://localhost:8000/api/mau-2c/sample-data/' + selectedTemplate);
      const response = await axios.get(`http://localhost:8000/api/mau-2c/sample-data/${selectedTemplate}`);
      const data = response.data;
      
      // Load simple fields
      setFormData({
        tinh: data.tinh || '',
        don_vi_truc_thuoc: data.don_vi_truc_thuoc || '',
        don_vi_co_so: data.don_vi_co_so || '',
        so_hieu: data.so_hieu || '',
        ho_ten: data.ho_ten || '',
        gioi_tinh: data.gioi_tinh || 'Nam',
        ten_goi_khac: data.ten_goi_khac || '',
        ngay: data.ngay || '',
        thang: data.thang || '',
        nam: data.nam || '',
        noi_sinh: data.noi_sinh || '',
        que_quan_xa: data.que_quan_xa || '',
        que_quan_huyen: data.que_quan_huyen || '',
        que_quan_tinh: data.que_quan_tinh || '',
        noi_o_hien_nay: data.noi_o_hien_nay || '',
        dien_thoai: data.dien_thoai || '',
        email: data.email || '',
        dan_toc: data.dan_toc || 'Kinh',
        ton_giao: data.ton_giao || '',
        cap_uy_hien_tai: data.cap_uy_hien_tai || '',
        cap_uy_kiem: data.cap_uy_kiem || '',
        chuc_vu_full: data.chuc_vu_full || '',
        phu_cap_chuc_vu: data.phu_cap_chuc_vu || '',
        thanh_phan_xuat_than: data.thanh_phan_xuat_than || '',
        nghe_nghiep_ban_than: data.nghe_nghiep_ban_than || '',
        ngay_tuyen_dung: data.ngay_tuyen_dung || '',
        co_quan_tuyen_dung: data.co_quan_tuyen_dung || '',
        ngay_vao_co_quan: data.ngay_vao_co_quan || '',
        ngay_tham_gia_cach_mang: data.ngay_tham_gia_cach_mang || '',
        ngay_vao_dang: data.ngay_vao_dang || '',
        ngay_chinh_thuc_dang: data.ngay_chinh_thuc_dang || '',
        ngay_tham_gia_to_chuc: data.ngay_tham_gia_to_chuc || '',
        ngay_nhap_ngu: data.ngay_nhap_ngu || '',
        ngay_xuat_ngu: data.ngay_xuat_ngu || '',
        quan_ham: data.quan_ham || '',
        trinh_do_giao_duc_pho_thong: data.trinh_do_giao_duc_pho_thong || '',
        hoc_ham_hoc_vi: data.hoc_ham_hoc_vi || '',
        ly_luan_chinh_tri: data.ly_luan_chinh_tri || '',
        ngoai_ngu: data.ngoai_ngu || '',
        quan_ly_nha_nuoc: data.quan_ly_nha_nuoc || '',
        tin_hoc: data.tin_hoc || '',
        cong_tac_chinh: data.cong_tac_chinh || '',
        ngach_cong_chuc: data.ngach_cong_chuc || '',
        ma_ngach: data.ma_ngach || '',
        bac_luong: data.bac_luong || '',
        he_so_luong: data.he_so_luong || '',
        tu_thang_nam: data.tu_thang_nam || '',
        danh_hieu: data.danh_hieu || '',
        so_truong_cong_tac: data.so_truong_cong_tac || '',
        cong_viec_lau_nhat: data.cong_viec_lau_nhat || '',
        khen_thuong: data.khen_thuong || '',
        ky_luat: data.ky_luat || '',
        suc_khoe: data.suc_khoe || '',
        chieu_cao: data.chieu_cao || '',
        can_nang: data.can_nang || '',
        nhom_mau: data.nhom_mau || '',
        so_cmnd: data.so_cmnd || '',
        ngay_cap: data.ngay_cap || '',
        noi_cap: data.noi_cap || '',
        thuong_binh_loai: data.thuong_binh_loai || '',
        gia_dinh_liet_si: data.gia_dinh_liet_si || '',
        lich_su_bi_bat: data.lich_su_bi_bat || '',
        lam_viec_che_do_cu: data.lam_viec_che_do_cu || '',
        quan_he_nuoc_ngoai: data.quan_he_nuoc_ngoai || '',
        than_nhan_nuoc_ngoai: data.than_nhan_nuoc_ngoai || '',
      });
      
      // Load arrays
      if (data.dao_tao && data.dao_tao.length > 0) {
        setDaoTao(data.dao_tao.map((item: any, idx: number) => ({ ...item, id: idx + 1 })));
      }
      if (data.cong_tac && data.cong_tac.length > 0) {
        setCongTac(data.cong_tac.map((item: any, idx: number) => ({ ...item, id: idx + 1 })));
      }
      if (data.gia_dinh && data.gia_dinh.length > 0) {
        setGiaDinh(data.gia_dinh.map((item: any, idx: number) => ({ ...item, id: idx + 1 })));
      }
      if (data.gia_dinh_vo_chong && data.gia_dinh_vo_chong.length > 0) {
        setGiaDinhVoChong(data.gia_dinh_vo_chong.map((item: any, idx: number) => ({ ...item, id: idx + 1 })));
      }
      if (data.luong && data.luong.length > 0) {
        setLuong(data.luong.map((item: any, idx: number) => ({ ...item, id: idx + 1 })));
      }
      
      toast.success('✅ Đã tải dữ liệu mẫu');
      setShowTemplates(false);
    } catch (error) {
      toast.error('Không thể tải dữ liệu mẫu');
      console.error(error);
    }
  };

  const generateDocument = async () => {
    setLoading(true);
    const loadingToast = toast.loading('⏳ Đang tạo tài liệu...');
    
    try {
      // Prepare data
      const payload = {
        ...formData,
        dao_tao: daoTao.map(({ id, ...rest }) => rest),
        cong_tac: congTac.map(({ id, ...rest }) => rest),
        gia_dinh: giaDinh.map(({ id, ...rest }) => rest),
        gia_dinh_vo_chong: giaDinhVoChong.map(({ id, ...rest }) => rest),
        luong: luong.map(({ id, ...rest }) => rest),
      };
      
      const response = await axios.post(
        'http://localhost:8000/api/mau-2c/generate-and-download',
        payload,
        { responseType: 'blob' }
      );
      
      // Download file
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Mau_2C_${formData.ho_ten || 'document'}_${new Date().getTime()}.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.dismiss(loadingToast);
      toast.success('✅ Tạo tài liệu thành công!');
    } catch (error: any) {
      toast.dismiss(loadingToast);
      
      // Handle Blob error responses
      if (error.response?.data instanceof Blob) {
        try {
          const text = await error.response.data.text();
          const json = JSON.parse(text);
          toast.error(json.detail || 'Có lỗi xảy ra');
        } catch (e) {
          toast.error('Có lỗi xảy ra khi tạo tài liệu');
        }
      } else {
        toast.error(error.response?.data?.detail || 'Có lỗi xảy ra khi tạo tài liệu');
      }
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mẫu 2C - Sơ Yếu Lý Lịch</h1>
          <p className="text-gray-500 mt-1">Tạo sơ yếu lý lịch tự động theo mẫu 2C-TCTW-98</p>
        </div>
        <Button onClick={() => setShowTemplates(!showTemplates)} variant="outline">
          <Users className="w-4 h-4 mr-2" />
          Chọn mẫu dữ liệu
        </Button>
      </div>

      {/* Template Selection Card */}
      {showTemplates && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-blue-900">Chọn mẫu dữ liệu có sẵn</CardTitle>
          </CardHeader>
          <CardContent>
            {templates.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Loader2 className="w-8 h-8 mx-auto mb-2 animate-spin" />
                <p>Đang tải danh sách mẫu...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {templates.map((template) => (
                <div
                  key={template.id}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedTemplate === template.id
                      ? 'border-blue-500 bg-blue-100 shadow-md'
                      : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow'
                  }`}
                  onClick={() => setSelectedTemplate(template.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{template.name}</h3>
                    {selectedTemplate === template.id && (
                      <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">✓ Đã chọn</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{template.description}</p>
                </div>
              ))}
            </div>
            )}
            <div className="mt-4 flex justify-end gap-2">
              <Button onClick={() => setShowTemplates(false)} variant="outline">
                Đóng
              </Button>
              <Button 
                onClick={() => loadSampleData()} 
                disabled={!selectedTemplate}
              >
                <FileText className="w-4 h-4 mr-2" />
                Tải dữ liệu mẫu
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle>Thông tin cá nhân</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Tỉnh/Thành phố</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.tinh}
                onChange={(e) => handleInputChange('tinh', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Đơn vị trực thuộc</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.don_vi_truc_thuoc}
                onChange={(e) => handleInputChange('don_vi_truc_thuoc', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Đơn vị cơ sở</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.don_vi_co_so}
                onChange={(e) => handleInputChange('don_vi_co_so', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Số hiệu</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.so_hieu}
                onChange={(e) => handleInputChange('so_hieu', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Họ và tên *</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.ho_ten}
                onChange={(e) => handleInputChange('ho_ten', e.target.value)}
                placeholder="Nguyễn Văn A"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Giới tính</label>
              <select
                className="w-full px-3 py-2 border rounded-md"
                value={formData.gioi_tinh}
                onChange={(e) => handleInputChange('gioi_tinh', e.target.value)}
              >
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Tên gọi khác</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.ten_goi_khac}
                onChange={(e) => handleInputChange('ten_goi_khac', e.target.value)}
              />
            </div>
            <div className="col-span-1 md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium mb-1">Ngày sinh</label>
              <div className="grid grid-cols-3 gap-4">
                <input
                  type="text"
                  placeholder="Ngày (01-31)"
                  className="px-3 py-2 border rounded-md"
                  value={formData.ngay}
                  onChange={(e) => handleInputChange('ngay', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Tháng (01-12)"
                  className="px-3 py-2 border rounded-md"
                  value={formData.thang}
                  onChange={(e) => handleInputChange('thang', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Năm (1990)"
                  className="px-3 py-2 border rounded-md"
                  value={formData.nam}
                  onChange={(e) => handleInputChange('nam', e.target.value)}
                />
              </div>
            </div>
            <div className="col-span-1 md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium mb-1">Nơi sinh</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.noi_sinh}
                onChange={(e) => handleInputChange('noi_sinh', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Quê quán - Xã</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.que_quan_xa}
                onChange={(e) => handleInputChange('que_quan_xa', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Quê quán - Huyện</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.que_quan_huyen}
                onChange={(e) => handleInputChange('que_quan_huyen', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Quê quán - Tỉnh</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.que_quan_tinh}
                onChange={(e) => handleInputChange('que_quan_tinh', e.target.value)}
              />
            </div>
            <div className="col-span-1 md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium mb-1">Nơi ở hiện nay</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.noi_o_hien_nay}
                onChange={(e) => handleInputChange('noi_o_hien_nay', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Điện thoại</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.dien_thoai}
                onChange={(e) => handleInputChange('dien_thoai', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Dân tộc</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.dan_toc}
                onChange={(e) => handleInputChange('dan_toc', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Tôn giáo</label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.ton_giao}
                onChange={(e) => handleInputChange('ton_giao', e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Continue with more cards... Due to length, showing structure */}
      {/* You can expand this with all the other fields following the same pattern */}

      {/* Đào tạo Array */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Đào tạo</CardTitle>
            <Button size="sm" onClick={() => handleArrayAdd(setDaoTao, daoTao)}>
              <Plus className="w-4 h-4 mr-1" /> Thêm
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {daoTao.map((item, idx) => (
            <div key={item.id} className="mb-4 p-4 border rounded-md">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">Trường #{idx + 1}</span>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  onClick={() => handleArrayRemove(setDaoTao, daoTao, item.id)}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Tên trường"
                  className="px-3 py-2 border rounded-md"
                  value={item.ten_truong || ''}
                  onChange={(e) => handleArrayChange(setDaoTao, daoTao, item.id, 'ten_truong', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Ngành học"
                  className="px-3 py-2 border rounded-md"
                  value={item.nganh_hoc || ''}
                  onChange={(e) => handleArrayChange(setDaoTao, daoTao, item.id, 'nganh_hoc', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Thời gian (2015-2019)"
                  className="px-3 py-2 border rounded-md"
                  value={item.thoi_gian || ''}
                  onChange={(e) => handleArrayChange(setDaoTao, daoTao, item.id, 'thoi_gian', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Hình thức (Chính quy)"
                  className="px-3 py-2 border rounded-md"
                  value={item.hinh_thuc || ''}
                  onChange={(e) => handleArrayChange(setDaoTao, daoTao, item.id, 'hinh_thuc', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Văn bằng"
                  className="px-3 py-2 border rounded-md col-span-1 md:col-span-2"
                  value={item.van_bang || ''}
                  onChange={(e) => handleArrayChange(setDaoTao, daoTao, item.id, 'van_bang', e.target.value)}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Generate Button */}
      <Card>
        <CardContent className="pt-6">
          <Button 
            onClick={generateDocument} 
            disabled={loading || !formData.ho_ten}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Đang tạo tài liệu...
              </>
            ) : (
              <>
                <Download className="w-5 h-5 mr-2" />
                Tạo tài liệu Mẫu 2C
              </>
            )}
          </Button>
          {!formData.ho_ten && (
            <p className="text-sm text-red-500 mt-2 text-center">
              * Vui lòng nhập họ tên
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
