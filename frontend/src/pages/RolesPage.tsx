import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roleService } from '../services';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { RoleCardSkeleton, PermissionGridSkeleton } from '../components/ui/skeleton';
import EmptyState from '../components/ui/empty-state';
import RoleModal from '../components/modals/RoleModal';
import ConfirmDialog from '../components/modals/ConfirmDialog';
import { Shield, Plus, Edit2, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import type { RoleDetail } from '../types';
import { formatApiError } from '../lib/error-utils';

export default function RolesPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<RoleDetail | null>(null);
  const [roleToDelete, setRoleToDelete] = useState<RoleDetail | null>(null);
  const [roleUsers, setRoleUsers] = useState<any[]>([]);

  const queryClient = useQueryClient();

  const { data: roles, isLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: () => roleService.getRoles(),
  });

  const { data: permissions } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => roleService.getPermissions(),
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: roleService.createRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setIsModalOpen(false);
      toast.success('Tạo vai trò thành công!');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      roleService.updateRole(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setIsModalOpen(false);
      setSelectedRole(null);
      toast.success('Cập nhật vai trò thành công!');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: roleService.deleteRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setRoleToDelete(null);
      toast.success('Xóa vai trò thành công!');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });

  const handleOpenModal = (role?: RoleDetail) => {
    if (role) {
      setSelectedRole(role);
    } else {
      setSelectedRole(null);
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedRole(null);
  };

  const handleSubmit = (data: any) => {
    if (selectedRole) {
      // Update mode - remove name field
      const { name, ...updateData } = data;
      updateMutation.mutate({ id: selectedRole.id, data: updateData });
    } else {
      // Create mode
      createMutation.mutate(data);
    }
  };

  const handleDelete = async (role: RoleDetail) => {
    // Fetch users with this role
    try {
      const users = await roleService.getRoleUsers(role.id);
      setRoleUsers(users);
      setRoleToDelete(role);
    } catch (error) {
      toast.error('Không thể kiểm tra người dùng của vai trò này');
    }
  };

  const confirmDelete = () => {
    if (roleToDelete) {
      deleteMutation.mutate(roleToDelete.id);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Vai trò & Quyền hạn</h1>
          <p className="text-muted-foreground mt-2">
            Quản lý các vai trò và quyền hạn của hệ thống
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <RoleCardSkeleton key={i} />
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Tất cả quyền hạn</CardTitle>
          </CardHeader>
          <CardContent>
            <PermissionGridSkeleton />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Vai trò & Quyền hạn</h1>
          <p className="text-muted-foreground mt-2">
            Quản lý các vai trò và quyền hạn của hệ thống
          </p>
        </div>
        <Button onClick={() => handleOpenModal()} className="gap-2">
          <Plus className="h-4 w-4" />
          Thêm vai trò
        </Button>
      </div>

      {/* Roles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {roles && roles.length > 0 ? (
          roles.map((role) => (
            <Card key={role.id} className="relative group">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Shield className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-lg">{role.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {role.description || 'Chưa có mô tả'}
                    </p>
                  </div>
                </div>
              </CardHeader>
              {/* Action buttons */}
              <div className="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleOpenModal(role as RoleDetail)}
                  className="p-2 bg-white border rounded-lg hover:bg-gray-50 transition-colors"
                  title="Chỉnh sửa"
                >
                  <Edit2 className="h-4 w-4 text-blue-600" />
                </button>
                {!['admin', 'viewer', 'editor'].includes(role.name) && (
                  <button
                    onClick={() => handleDelete(role as RoleDetail)}
                    className="p-2 bg-white border rounded-lg hover:bg-gray-50 transition-colors"
                    title="Xóa"
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </button>
                )}
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-3">
            <EmptyState
              icon={Shield}
              title="Chưa có vai trò nào"
              description="Hệ thống chưa có vai trò nào. Nhấn nút 'Thêm vai trò' để tạo vai trò mới."
              action={{
                label: 'Thêm vai trò',
                onClick: () => handleOpenModal(),
              }}
            />
          </div>
        )}
      </div>

      {/* Permissions */}
      <Card>
        <CardHeader>
          <CardTitle>Tất cả quyền hạn</CardTitle>
        </CardHeader>
        <CardContent>
          {permissions && permissions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {permissions.map((permission) => (
                <div
                  key={permission.id}
                  className="p-3 border rounded-lg"
                >
                  <div className="font-medium text-sm">{permission.name}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {permission.description || 'Chưa có mô tả'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Shield}
              title="Chưa có quyền hạn nào"
              description="Hệ thống chưa có quyền hạn nào được định nghĩa."
            />
          )}
        </CardContent>
      </Card>

      {/* Role Modal */}
      <RoleModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSubmit}
        role={selectedRole}
        permissions={permissions || []}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!roleToDelete}
        onClose={() => setRoleToDelete(null)}
        onConfirm={confirmDelete}
        title="Xóa vai trò?"
        message={
          roleToDelete && roleUsers.length > 0
            ? `Vai trò "${roleToDelete.name}" hiện có ${roleUsers.length} người dùng. Xóa vai trò sẽ loại bỏ vai trò này khỏi tất cả người dùng. Bạn có chắc chắn muốn xóa?`
            : `Bạn có chắc chắn muốn xóa vai trò "${roleToDelete?.name}"?`
        }
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
}
