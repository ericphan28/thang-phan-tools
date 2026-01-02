import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LandingPage from './public/LandingPage';

/**
 * Home page that redirects based on auth status
 * - Not logged in: Show landing page
 * - Admin user: Redirect to /admin
 * - Regular user: Redirect to /user
 */
export default function HomePage() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg">Đang tải...</div>
      </div>
    );
  }

  // If logged in, redirect based on role
  if (isAuthenticated && user) {
    if (user.is_superuser) {
      return <Navigate to="/admin" replace />;
    } else {
      return <Navigate to="/user" replace />;
    }
  }

  // Not logged in - show public landing page
  return <LandingPage />;
}
