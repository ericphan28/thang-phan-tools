import { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { X } from 'lucide-react';
import type { User, Role } from '../../types';

interface UserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  user?: User | null;
  roles: Role[];
  isLoading?: boolean;
}

export default function UserModal({
  isOpen,
  onClose,
  onSubmit,
  user,
  roles,
  isLoading = false,
}: UserModalProps) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role_ids: [] as number[],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username,
        email: user.email,
        full_name: user.full_name || '',
        password: '',
        role_ids: user.roles.map(roleName => 
          roles.find(r => r.name === roleName)?.id || 0
        ).filter(id => id > 0),
      });
    } else {
      setFormData({
        username: '',
        email: '',
        full_name: '',
        password: '',
        role_ids: [],
      });
    }
    setErrors({}); // Clear errors when modal opens/closes
  }, [user, roles, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    const newErrors: Record<string, string> = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Tên đăng nhập không được để trống';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Tên đăng nhập phải có ít nhất 3 ký tự';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email không được để trống';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email không hợp lệ';
    }
    
    if (!user && !formData.password) {
      newErrors.password = 'Mật khẩu không được để trống';
    } else if (formData.password && formData.password.length < 6) {
      newErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    setErrors({});
    onSubmit(formData);
  };

  const handleRoleToggle = (roleId: number) => {
    setFormData(prev => ({
      ...prev,
      role_ids: prev.role_ids.includes(roleId)
        ? prev.role_ids.filter(id => id !== roleId)
        : [...prev.role_ids, roleId],
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-in fade-in duration-200">
      <div className="bg-card rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold">
            {user ? 'Chỉnh sửa người dùng' : 'Thêm người dùng mới'}
          </h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Username */}
          <div className="space-y-2">
            <label htmlFor="username" className="text-sm font-medium">
              Tên đăng nhập <span className="text-destructive">*</span>
            </label>
            <Input
              id="username"
              type="text"
              value={formData.username}
              onChange={(e) => {
                setFormData({ ...formData, username: e.target.value });
                if (errors.username) setErrors({ ...errors, username: '' });
              }}
              required
              disabled={!!user || isLoading}
              placeholder="Nhập tên đăng nhập"
              className={errors.username ? 'border-red-500' : ''}
            />
            {errors.username && (
              <p className="text-xs text-red-500 mt-1">{errors.username}</p>
            )}
            {user && (
              <p className="text-xs text-muted-foreground">
                Tên đăng nhập không thể thay đổi
              </p>
            )}
          </div>

          {/* Email */}
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Email <span className="text-destructive">*</span>
            </label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => {
                setFormData({ ...formData, email: e.target.value });
                if (errors.email) setErrors({ ...errors, email: '' });
              }}
              required
              disabled={isLoading}
              placeholder="Nhập email"
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && (
              <p className="text-xs text-red-500 mt-1">{errors.email}</p>
            )}
          </div>

          {/* Full Name */}
          <div className="space-y-2">
            <label htmlFor="full_name" className="text-sm font-medium">
              Họ và tên
            </label>
            <Input
              id="full_name"
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              disabled={isLoading}
              placeholder="Nhập họ và tên"
            />
          </div>

          {/* Password */}
          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              Mật khẩu {!user && <span className="text-destructive">*</span>}
            </label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => {
                setFormData({ ...formData, password: e.target.value });
                if (errors.password) setErrors({ ...errors, password: '' });
              }}
              required={!user}
              disabled={isLoading}
              placeholder={user ? "Để trống nếu không đổi" : "Nhập mật khẩu"}
              className={errors.password ? 'border-red-500' : ''}
            />
            {errors.password && (
              <p className="text-xs text-red-500 mt-1">{errors.password}</p>
            )}
            {user && (
              <p className="text-xs text-muted-foreground">
                Để trống nếu không muốn thay đổi mật khẩu
              </p>
            )}
          </div>

          {/* Roles */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Vai trò</label>
            {roles.length === 0 ? (
              <div className="border rounded-lg p-3 text-sm text-muted-foreground text-center">
                Không có vai trò nào. Vui lòng kiểm tra quyền truy cập.
              </div>
            ) : (
              <div className="space-y-2 border rounded-lg p-3">
                {roles.map((role) => (
                  <label
                    key={role.id}
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={formData.role_ids.includes(role.id)}
                      onChange={() => handleRoleToggle(role.id)}
                      disabled={isLoading}
                      className="rounded border-gray-300"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{role.name}</div>
                      {role.description && (
                        <div className="text-xs text-muted-foreground">
                          {role.description}
                        </div>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1"
            >
              Hủy
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? 'Đang xử lý...' : (user ? 'Cập nhật' : 'Thêm mới')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
