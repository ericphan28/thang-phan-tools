import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { userService, roleService } from '../services';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { TableRowSkeleton } from '../components/ui/skeleton';
import EmptyState from '../components/ui/empty-state';
import UserModal from '../components/modals/UserModal';
import ConfirmDialog from '../components/modals/ConfirmDialog';
import { formatApiError } from '../lib/error-utils';
import { Plus, Search, Edit, Trash2, CheckCircle, XCircle, Users as UsersIcon } from 'lucide-react';
import type { User, UserCreate } from '../types';

export default function UsersPage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  
  const queryClient = useQueryClient();

  // Fetch users
  const { data: usersData, isLoading } = useQuery({
    queryKey: ['users', { search, page }],
    queryFn: () => userService.getUsers({ search, page, page_size: 10 }),
  });

  // Fetch roles
  const { data: roles, isLoading: rolesLoading, error: rolesError } = useQuery({
    queryKey: ['roles'],
    queryFn: () => roleService.getRoles(),
    retry: 2,
  });

  // Log roles error for debugging
  if (rolesError) {
    console.error('Error loading roles:', rolesError);
  }

  // Delete user mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => userService.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Xóa người dùng thành công!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Xóa người dùng thất bại!');
    },
  });

  // Activate/Deactivate mutation
  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: number; isActive: boolean }) =>
      isActive ? userService.deactivateUser(id) : userService.activateUser(id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success(variables.isActive ? 'Đã vô hiệu hóa người dùng!' : 'Đã kích hoạt người dùng!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Thao tác thất bại!');
    },
  });

  // Create/Update user mutation
  const createUpdateMutation = useMutation({
    mutationFn: (data: any) => {
      if (selectedUser) {
        return userService.updateUser(selectedUser.id, data);
      } else {
        return userService.createUser(data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success(selectedUser ? 'Cập nhật người dùng thành công!' : 'Thêm người dùng thành công!');
      setIsCreateModalOpen(false);
      setSelectedUser(null);
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });

  const handleDelete = (user: User) => {
    setUserToDelete(user);
  };

  const confirmDelete = () => {
    if (userToDelete) {
      deleteMutation.mutate(userToDelete.id);
      setUserToDelete(null);
    }
  };

  const handleToggleActive = (user: User) => {
    toggleActiveMutation.mutate({ id: user.id, isActive: user.is_active });
  };

  const handleEdit = (user: User) => {
    setSelectedUser(user);
    setIsCreateModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsCreateModalOpen(false);
    setSelectedUser(null);
  };

  const handleSubmitModal = (data: any) => {
    createUpdateMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Quản lý người dùng</h1>
          <p className="text-muted-foreground mt-2">
            Quản lý tài khoản và quyền hạn người dùng
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Thêm người dùng
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Tìm kiếm theo tên đăng nhập, email hoặc họ tên..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            Người dùng ({usersData?.total || 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <TableRowSkeleton key={i} />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 px-4 py-2 bg-muted rounded-lg text-sm font-medium">
                <div className="col-span-3">Tên đăng nhập</div>
                <div className="col-span-3">Email</div>
                <div className="col-span-2">Vai trò</div>
                <div className="col-span-1">Trạng thái</div>
                <div className="col-span-1">Loại</div>
                <div className="col-span-2 text-right">Thao tác</div>
              </div>

              {/* Table Rows */}
              {usersData?.users.map((user) => (
                <div
                  key={user.id}
                  className="grid grid-cols-12 gap-4 px-4 py-3 border rounded-lg items-center hover:bg-accent/50 transition-colors"
                >
                  <div className="col-span-3">
                    <div className="font-medium">{user.username}</div>
                    <div className="text-sm text-muted-foreground">
                      {user.full_name || 'Chưa có tên'}
                    </div>
                  </div>
                  <div className="col-span-3 text-sm">{user.email}</div>
                  <div className="col-span-2">
                    <div className="flex flex-wrap gap-1">
                      {user.roles.map((role) => (
                        <span
                          key={role}
                          className="text-xs px-2 py-1 bg-primary/10 text-primary rounded"
                        >
                          {role}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="col-span-1">
                    {user.is_active ? (
                      <span className="flex items-center gap-1 text-xs text-green-600">
                        <CheckCircle className="h-3 w-3" />
                        Hoạt động
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-orange-600">
                        <XCircle className="h-3 w-3" />
                        Vô hiệu
                      </span>
                    )}
                  </div>
                  <div className="col-span-1">
                    {user.is_superuser && (
                      <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                        Quản trị
                      </span>
                    )}
                  </div>
                  <div className="col-span-2 flex items-center justify-end gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleActive(user)}
                    >
                      {user.is_active ? 'Vô hiệu hóa' : 'Kích hoạt'}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEdit(user)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(user)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && usersData?.users.length === 0 && (
            <EmptyState
              icon={UsersIcon}
              title="Không tìm thấy người dùng"
              description={
                search
                  ? `Không có kết quả phù hợp với "${search}". Thử tìm kiếm với từ khóa khác.`
                  : "Chưa có người dùng nào trong hệ thống. Hãy thêm người dùng đầu tiên."
              }
              action={
                !search
                  ? {
                      label: "Thêm người dùng đầu tiên",
                      onClick: () => setIsCreateModalOpen(true),
                    }
                  : undefined
              }
            />
          )}

          {/* Pagination */}
          {usersData && usersData.total_pages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-6 border-t">
              <div className="text-sm text-muted-foreground">
                Trang {usersData.page} / {usersData.total_pages}
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={usersData.page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Trước
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={usersData.page === usersData.total_pages}
                  onClick={() => setPage(page + 1)}
                >
                  Sau
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Modal */}
      <UserModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSubmitModal}
        user={selectedUser}
        roles={roles || []}
        isLoading={createUpdateMutation.isPending || rolesLoading}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!userToDelete}
        onClose={() => setUserToDelete(null)}
        onConfirm={confirmDelete}
        title="Xóa người dùng"
        message={`Bạn có chắc chắn muốn xóa người dùng "${userToDelete?.username}"? Hành động này không thể hoàn tác.`}
        confirmText="Xóa"
        cancelText="Hủy"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
}
