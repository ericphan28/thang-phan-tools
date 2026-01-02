import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { userService } from '../../services';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { ArrowLeft, User, Lock, Save, LogOut } from 'lucide-react';
import toast from 'react-hot-toast';

export default function UserProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    address: user?.address || '',
  });

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [showPasswordForm, setShowPasswordForm] = useState(false);

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data: { full_name: string; email: string; phone: string; address: string }) =>
      userService.updateProfile(data),
    onSuccess: () => {
      toast.success('Cập nhật thông tin thành công!');
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
      
      // Update user in localStorage
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        userData.full_name = profileForm.full_name;
        userData.email = profileForm.email;
        userData.phone = profileForm.phone;
        userData.address = profileForm.address;
        localStorage.setItem('user', JSON.stringify(userData));
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Cập nhật thất bại');
    },
  });

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: (data: { old_password: string; new_password: string }) =>
      userService.changePassword(data),
    onSuccess: () => {
      toast.success('Đổi mật khẩu thành công!');
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
      setShowPasswordForm(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Đổi mật khẩu thất bại');
    },
  });

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate(profileForm);
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Mật khẩu xác nhận không khớp');
      return;
    }

    if (passwordForm.new_password.length < 6) {
      toast.error('Mật khẩu mới phải có ít nhất 6 ký tự');
      return;
    }

    changePasswordMutation.mutate({
      old_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    });
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Đăng xuất thành công');
      navigate('/login');
    } catch (error) {
      toast.error('Đăng xuất thất bại');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/user">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Quay lại Dashboard
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-primary">Thông tin cá nhân</h1>
          </div>
          <Button variant="destructive" onClick={handleLogout}>
            <LogOut className="h-4 w-4 mr-2" />
            Đăng xuất
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="grid gap-6">
          {/* User Info Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Thông tin tài khoản
              </CardTitle>
              <CardDescription>
                Cập nhật thông tin cá nhân của bạn
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tên đăng nhập</label>
                    <Input value={user?.username || ''} disabled />
                    <p className="text-xs text-muted-foreground">
                      Không thể thay đổi tên đăng nhập
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Email</label>
                    <Input
                      type="email"
                      value={profileForm.email}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, email: e.target.value })
                      }
                      placeholder="your@email.com"
                      required
                    />
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium">Họ và tên</label>
                    <Input
                      value={profileForm.full_name}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, full_name: e.target.value })
                      }
                      placeholder="Nhập họ và tên"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Số điện thoại</label>
                    <Input
                      type="tel"
                      value={profileForm.phone}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, phone: e.target.value })
                      }
                      placeholder="0909123456"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">&nbsp;</label>
                    <div className="h-10"></div>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium">Địa chỉ</label>
                    <Input
                      value={profileForm.address}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, address: e.target.value })
                      }
                      placeholder="Nhập địa chỉ"
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    type="submit"
                    disabled={updateProfileMutation.isPending}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {updateProfileMutation.isPending ? 'Đang lưu...' : 'Lưu thay đổi'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Change Password Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Đổi mật khẩu
              </CardTitle>
              <CardDescription>
                Cập nhật mật khẩu để bảo mật tài khoản
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!showPasswordForm ? (
                <Button
                  variant="outline"
                  onClick={() => setShowPasswordForm(true)}
                >
                  Đổi mật khẩu
                </Button>
              ) : (
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Mật khẩu hiện tại</label>
                    <Input
                      type="password"
                      value={passwordForm.current_password}
                      onChange={(e) =>
                        setPasswordForm({
                          ...passwordForm,
                          current_password: e.target.value,
                        })
                      }
                      placeholder="Nhập mật khẩu hiện tại"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Mật khẩu mới</label>
                    <Input
                      type="password"
                      value={passwordForm.new_password}
                      onChange={(e) =>
                        setPasswordForm({
                          ...passwordForm,
                          new_password: e.target.value,
                        })
                      }
                      placeholder="Nhập mật khẩu mới (tối thiểu 6 ký tự)"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">
                      Xác nhận mật khẩu mới
                    </label>
                    <Input
                      type="password"
                      value={passwordForm.confirm_password}
                      onChange={(e) =>
                        setPasswordForm({
                          ...passwordForm,
                          confirm_password: e.target.value,
                        })
                      }
                      placeholder="Nhập lại mật khẩu mới"
                      required
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      disabled={changePasswordMutation.isPending}
                    >
                      {changePasswordMutation.isPending
                        ? 'Đang đổi...'
                        : 'Xác nhận đổi mật khẩu'}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowPasswordForm(false);
                        setPasswordForm({
                          current_password: '',
                          new_password: '',
                          confirm_password: '',
                        });
                      }}
                    >
                      Hủy
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>

          {/* Account Info */}
          <Card>
            <CardHeader>
              <CardTitle>Thông tin tài khoản</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">ID:</span>
                <span className="font-mono">{user?.id}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Tài khoản:</span>
                <span>{user?.username}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Loại tài khoản:</span>
                <span>
                  {user?.is_superuser ? (
                    <span className="text-purple-600 font-semibold">👑 Admin</span>
                  ) : (
                    <span className="text-blue-600">👤 User</span>
                  )}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Trạng thái:</span>
                <span>
                  {user?.is_active ? (
                    <span className="text-green-600">✓ Hoạt động</span>
                  ) : (
                    <span className="text-red-600">✗ Không hoạt động</span>
                  )}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Logout Section */}
          <Card className="border-destructive/50">
            <CardHeader>
              <CardTitle className="text-destructive">Đăng xuất</CardTitle>
              <CardDescription>
                Kết thúc phiên làm việc hiện tại
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="destructive" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Đăng xuất khỏi tài khoản
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
