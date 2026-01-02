import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export default function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg">Đang kiểm tra quyền truy cập...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!user?.is_superuser) {
    // Regular users should go to their own dashboard
    return <Navigate to="/user" replace />;
  }

  return <>{children}</>;
}
