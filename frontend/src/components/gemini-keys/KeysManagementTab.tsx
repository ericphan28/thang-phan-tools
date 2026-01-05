/**
 * Keys Management Tab - CRUD Operations
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { 
  Plus, 
  MoreVertical, 
  Edit, 
  Trash2, 
  RotateCw, 
  Eye,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock
} from 'lucide-react';
import { geminiKeysService, type GeminiAPIKey, type GeminiAPIKeyCreate } from '../../services/geminiKeysService';
import toast from 'react-hot-toast';
import { Skeleton } from '../ui/skeleton';

export default function KeysManagementTab() {
  const queryClient = useQueryClient();
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editingKey, setEditingKey] = useState<GeminiAPIKey | null>(null);
  const [includeInactive, setIncludeInactive] = useState(false);

  // Form state
  const [formData, setFormData] = useState<GeminiAPIKeyCreate>({
    key_name: '',
    api_key: '',
    priority: 10,
    monthly_quota_limit: 1_500_000,
    notes: '',
  });

  // Query
  const { data: keys, isLoading } = useQuery({
    queryKey: ['gemini-keys', includeInactive],
    queryFn: () => geminiKeysService.getAllKeys(includeInactive),
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: geminiKeysService.createKey,
    onSuccess: () => {
      toast.success('✅ Đã tạo key thành công');
      queryClient.invalidateQueries({ queryKey: ['gemini-keys'] });
      queryClient.invalidateQueries({ queryKey: ['gemini-dashboard'] });
      setShowAddDialog(false);
      resetForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Không thể tạo key');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => 
      geminiKeysService.updateKey(id, data),
    onSuccess: () => {
      toast.success('✅ Đã cập nhật key');
      queryClient.invalidateQueries({ queryKey: ['gemini-keys'] });
      setShowEditDialog(false);
      setEditingKey(null);
      resetForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Không thể cập nhật key');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: geminiKeysService.deleteKey,
    onSuccess: () => {
      toast.success('🗑️ Đã xóa key');
      queryClient.invalidateQueries({ queryKey: ['gemini-keys'] });
      queryClient.invalidateQueries({ queryKey: ['gemini-dashboard'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Không thể xóa key');
    },
  });

  const rotateMutation = useMutation({
    mutationFn: (keyId: number) => geminiKeysService.rotateKey(keyId, 'manual_rotation'),
    onSuccess: (data) => {
      toast.success(`🔄 ${data.message}`);
      queryClient.invalidateQueries({ queryKey: ['gemini-keys'] });
      queryClient.invalidateQueries({ queryKey: ['gemini-dashboard'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Không thể rotate key');
    },
  });

  const resetForm = () => {
    setFormData({
      key_name: '',
      api_key: '',
      priority: 10,
      monthly_quota_limit: 1_500_000,
      notes: '',
    });
  };

  const handleCreate = () => {
    if (!formData.key_name || !formData.api_key) {
      toast.error('Vui lòng nhập đầy đủ thông tin');
      return;
    }
    createMutation.mutate(formData);
  };

  const handleOpenEdit = (key: GeminiAPIKey) => {
    console.log('🔍 handleOpenEdit called with key:', key);
    setEditingKey(key);
    setFormData({
      key_name: key.key_name,
      account_email: key.account_email || '',
      api_key: '', // Không hiển thị key cũ
      priority: key.priority,
      monthly_quota_limit: key.monthly_quota_limit || 1_500_000,
      notes: key.notes || '',
    });
    setShowEditDialog(true);
    console.log('✅ setShowEditDialog(true) called');
  };

  const handleUpdate = () => {
    if (!editingKey) return;
    if (!formData.key_name) {
      toast.error('Key name là bắt buộc');
      return;
    }

    // Chỉ gửi các field đã thay đổi
    const updateData: any = {
      key_name: formData.key_name,
      account_email: formData.account_email || null,
      priority: formData.priority,
      notes: formData.notes || null,
    };

    // Nếu có nhập API key mới thì update
    if (formData.api_key) {
      updateData.api_key = formData.api_key;
    }

    updateMutation.mutate({ id: editingKey.id, data: updateData });
  };

  const handleCloseEdit = () => {
    setShowEditDialog(false);
    setEditingKey(null);
    resetForm();
  };

  const handleDelete = (keyId: number, keyName: string) => {
    if (confirm(`Xác nhận xóa key "${keyName}"?\n\nToàn bộ quota & usage logs sẽ bị xóa.`)) {
      deleteMutation.mutate(keyId);
    }
  };

  const handleRotate = (keyId: number, keyName: string) => {
    if (confirm(`Xác nhận rotate key "${keyName}"?\n\nHệ thống sẽ chuyển sang key khác ngay lập tức.`)) {
      rotateMutation.mutate(keyId);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; icon: any; label: string }> = {
      active: { variant: 'default', icon: CheckCircle2, label: 'Active' },
      inactive: { variant: 'secondary', icon: Clock, label: 'Inactive' },
      revoked: { variant: 'destructive', icon: XCircle, label: 'Revoked' },
      quota_exceeded: { variant: 'outline', icon: AlertTriangle, label: 'Quota Exceeded' },
    };
    const config = variants[status] || variants.inactive;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    );
  };

  const formatNumber = (num: number | null) => {
    if (num === null) return 'N/A';
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(0)}k`;
    return num.toString();
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header Actions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>Quản lý Gemini API keys với encryption & auto-rotation</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIncludeInactive(!includeInactive)}
            >
              {includeInactive ? 'Hide' : 'Show'} Inactive
            </Button>
            <Button onClick={() => setShowAddDialog(true)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Key
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Keys Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Account Email</TableHead>
                  <TableHead>API Key</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Priority</TableHead>
                  <TableHead className="text-right">Quota</TableHead>
                  <TableHead className="text-right">Used</TableHead>
                  <TableHead className="text-right">Remaining</TableHead>
                  <TableHead>Last Used</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {keys?.map((key) => (
                  <TableRow key={key.id}>
                    <TableCell className="font-medium">{key.key_name}</TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">
                        {key.account_email || '-'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <code className="text-xs bg-muted px-2 py-1 rounded">
                        {key.api_key_masked}
                      </code>
                    </TableCell>
                    <TableCell>{getStatusBadge(key.status)}</TableCell>
                    <TableCell className="text-right">
                      <Badge variant="outline">{key.priority}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {formatNumber(key.monthly_quota_limit)}
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={key.is_near_limit ? 'text-orange-600 font-semibold' : ''}>
                        {formatNumber(key.monthly_quota_used)}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex flex-col items-end gap-1">
                        <span>{formatNumber(key.monthly_quota_remaining)}</span>
                        {key.monthly_usage_percentage !== null && (
                          <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full transition-all ${
                                key.monthly_usage_percentage > 80
                                  ? 'bg-red-500'
                                  : key.monthly_usage_percentage > 50
                                  ? 'bg-yellow-500'
                                  : 'bg-green-500'
                              }`}
                              style={{ width: `${key.monthly_usage_percentage}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {key.last_used_at ? (
                        <span className="text-xs text-muted-foreground">
                          {new Date(key.last_used_at).toLocaleString('vi-VN')}
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">Never</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => handleOpenEdit(key)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleRotate(key.id, key.key_name)}>
                            <RotateCw className="h-4 w-4 mr-2" />
                            Rotate Key
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => handleDelete(key.id, key.key_name)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
                {(!keys || keys.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      Chưa có API keys. Click "Add Key" để thêm key đầu tiên.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Add Key Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add New Gemini API Key</DialogTitle>
            <DialogDescription>
              Thêm key mới từ Google AI Studio. Key sẽ được mã hóa trước khi lưu.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="key_name">Key Name *</Label>
              <Input
                id="key_name"
                placeholder="Production Key 1"
                value={formData.key_name}
                onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="account_email">Email Tài Khoản Google</Label>
              <Input
                id="account_email"
                type="email"
                placeholder="ericphan28@gmail.com"
                value={formData.account_email || ''}
                onChange={(e) => setFormData({ ...formData, account_email: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">
                Email tài khoản Google dùng để tạo API key này
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="api_key">API Key *</Label>
              <Input
                id="api_key"
                type="password"
                placeholder="AIzaSy..."
                value={formData.api_key}
                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">
                Get from{' '}
                <a
                  href="https://aistudio.google.com/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline"
                >
                  Google AI Studio
                </a>
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Input
                  id="priority"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 10 })}
                />
                <p className="text-xs text-muted-foreground">1 = cao nhất</p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="quota">Monthly Quota</Label>
                <Input
                  id="quota"
                  type="number"
                  min="0"
                  value={formData.monthly_quota_limit}
                  onChange={(e) => setFormData({ ...formData, monthly_quota_limit: parseInt(e.target.value) || 0 })}
                />
                <p className="text-xs text-muted-foreground">tokens</p>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="notes">Notes (optional)</Label>
              <Textarea
                id="notes"
                placeholder="Key này dùng cho production..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Key'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Key Dialog */}
      <Dialog open={showEditDialog} onOpenChange={handleCloseEdit}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Gemini API Key</DialogTitle>
            <DialogDescription>
              Cập nhật thông tin key. Để trống API Key nếu không muốn thay đổi.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit_key_name">Key Name *</Label>
              <Input
                id="edit_key_name"
                placeholder="Production Key 1"
                value={formData.key_name}
                onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit_account_email">Email Tài Khoản Google</Label>
              <Input
                id="edit_account_email"
                type="email"
                placeholder="ericphan28@gmail.com"
                value={formData.account_email || ''}
                onChange={(e) => setFormData({ ...formData, account_email: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit_api_key">API Key (để trống nếu không đổi)</Label>
              <Input
                id="edit_api_key"
                type="password"
                placeholder="Để trống nếu không muốn thay đổi"
                value={formData.api_key}
                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
              />
              <p className="text-xs text-yellow-600">
                ⚠️ Chỉ nhập key mới nếu muốn thay thế key hiện tại
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit_priority">Priority</Label>
                <Input
                  id="edit_priority"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 10 })}
                />
                <p className="text-xs text-muted-foreground">1 = cao nhất</p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit_quota">Monthly Quota</Label>
                <Input
                  id="edit_quota"
                  type="number"
                  min="0"
                  value={formData.monthly_quota_limit}
                  onChange={(e) => setFormData({ ...formData, monthly_quota_limit: parseInt(e.target.value) || 0 })}
                />
                <p className="text-xs text-muted-foreground">tokens</p>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit_notes">Notes</Label>
              <Textarea
                id="edit_notes"
                placeholder="Key này dùng cho production..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleCloseEdit}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Updating...' : 'Update Key'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
