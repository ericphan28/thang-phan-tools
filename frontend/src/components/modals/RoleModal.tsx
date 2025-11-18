import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import type { RoleDetail, Permission } from '../../types';

interface RoleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    description?: string;
    permission_specs: Array<{ resource: string; action: string }>;
  }) => void;
  role?: RoleDetail | null;
  permissions: Permission[];
  isLoading?: boolean;
}

export default function RoleModal({
  isOpen,
  onClose,
  onSubmit,
  role,
  permissions,
  isLoading = false,
}: RoleModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    selectedPermissions: [] as string[], // Store as "resource.action" strings
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      if (role) {
        // Edit mode
        setFormData({
          name: role.name,
          description: role.description || '',
          selectedPermissions: role.permissions.map((p) => `${p.resource}.${p.action}`),
        });
      } else {
        // Create mode
        setFormData({
          name: '',
          description: '',
          selectedPermissions: [],
        });
      }
      setErrors({});
    }
  }, [isOpen, role]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Tên vai trò không được để trống';
    } else if (formData.name.length < 3) {
      newErrors.name = 'Tên vai trò phải có ít nhất 3 ký tự';
    } else if (formData.name.length > 50) {
      newErrors.name = 'Tên vai trò không được vượt quá 50 ký tự';
    }

    if (formData.description && formData.description.length > 200) {
      newErrors.description = 'Mô tả không được vượt quá 200 ký tự';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    
    // Convert selectedPermissions to permission_specs
    const permission_specs = formData.selectedPermissions.map((key) => {
      const [resource, action] = key.split('.');
      return { resource, action };
    });

    onSubmit({
      name: formData.name,
      description: formData.description || undefined,
      permission_specs,
    });
  };

  const togglePermission = (permissionKey: string) => {
    setFormData((prev) => ({
      ...prev,
      selectedPermissions: prev.selectedPermissions.includes(permissionKey)
        ? prev.selectedPermissions.filter((key) => key !== permissionKey)
        : [...prev.selectedPermissions, permissionKey],
    }));
  };

  const toggleAllPermissions = () => {
    if (formData.selectedPermissions.length === permissions.length) {
      // Deselect all
      setFormData((prev) => ({ ...prev, selectedPermissions: [] }));
    } else {
      // Select all
      setFormData((prev) => ({
        ...prev,
        selectedPermissions: permissions.map((p) => `${p.resource}.${p.action}`),
      }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-lg w-full max-w-2xl max-h-[90vh] overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold">
            {role ? 'Chỉnh sửa vai trò' : 'Thêm vai trò mới'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isLoading}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="flex flex-col max-h-[calc(90vh-140px)]">
          <div className="p-6 space-y-4 overflow-y-auto">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Tên vai trò <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) => {
                  setFormData({ ...formData, name: e.target.value });
                  if (errors.name) setErrors({ ...errors, name: '' });
                }}
                placeholder="Ví dụ: Content Manager"
                disabled={!!role || isLoading}
                className={errors.name ? 'border-red-500' : ''}
              />
              {errors.name && (
                <p className="text-xs text-red-500 mt-1">{errors.name}</p>
              )}
              {role && (
                <p className="text-xs text-muted-foreground mt-1">
                  Tên vai trò không thể thay đổi sau khi tạo
                </p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium mb-2">Mô tả</label>
              <textarea
                value={formData.description}
                onChange={(e) => {
                  setFormData({ ...formData, description: e.target.value });
                  if (errors.description) setErrors({ ...errors, description: '' });
                }}
                placeholder="Mô tả vai trò này (tùy chọn)"
                rows={3}
                disabled={isLoading}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.description ? 'border-red-500' : ''
                }`}
              />
              {errors.description && (
                <p className="text-xs text-red-500 mt-1">{errors.description}</p>
              )}
              <p className="text-xs text-muted-foreground mt-1">
                {formData.description.length}/200 ký tự
              </p>
            </div>

            {/* Permissions */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium">
                  Quyền hạn ({formData.selectedPermissions.length}/{permissions.length})
                </label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={toggleAllPermissions}
                  disabled={isLoading}
                >
                  {formData.selectedPermissions.length === permissions.length
                    ? 'Bỏ chọn tất cả'
                    : 'Chọn tất cả'}
                </Button>
              </div>
              <div className="border rounded-lg p-4 max-h-64 overflow-y-auto bg-gray-50">
                {permissions.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Không có quyền hạn nào
                  </p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {permissions.map((permission) => {
                      const permissionKey = `${permission.resource}.${permission.action}`;
                      const isSelected = formData.selectedPermissions.includes(permissionKey);
                      
                      return (
                        <label
                          key={permission.id}
                          className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                            isSelected
                              ? 'bg-primary/10 border-primary'
                              : 'bg-white hover:bg-gray-50'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => togglePermission(permissionKey)}
                            disabled={isLoading}
                            className="mt-1"
                          />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium">{permission.name}</div>
                            <div className="text-xs text-muted-foreground mt-1">
                              {permission.description}
                            </div>
                          </div>
                        </label>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-6 border-t bg-gray-50">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Hủy
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Đang xử lý...' : role ? 'Cập nhật' : 'Tạo vai trò'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
