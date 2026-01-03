import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { TooltipProvider } from './components/ui/tooltip';
import Layout from './components/layout/Layout';
import AdminRoute from './components/layout/AdminRoute';
import ProtectedRoute from './components/layout/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import PublicPricingPage from './pages/public/PublicPricingPage';
import UserDashboard from './pages/user/UserDashboard';
import UserProfilePage from './pages/user/UserProfilePage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import RolesPage from './pages/RolesPage';
import ActivityLogsPage from './pages/ActivityLogsPage';
import ToolsPage from './pages/ToolsPage';
import AdobePdfPage from './pages/AdobePdfPage';
import Mau2CPage from './pages/Mau2CPage';
import OCRDemoPage from './pages/OCRDemoPage';
import OCRToWordPage from './pages/OCRToWordPage';
import AIAdminDashboardPage from './pages/AIAdminDashboardPage';
import AIKeysManagementPage from './pages/AIKeysManagementPage';
import TextToWordPage from './pages/TextToWordPage';
import DataVisualizationPage from './pages/DataVisualizationPage';
import DeploymentMonitor from './pages/DeploymentMonitor';
import UserSubscriptionPage from './pages/UserSubscriptionPage';
import PricingPage from './pages/PricingPage';
import BillingHistoryPage from './pages/BillingHistoryPage';
import WorkflowReviewPage from './pages/WorkflowReviewPage';
import KiemTraTheThuPage from './pages/KiemTraTheThuPage';
import DocumentToolsPage from './pages/DocumentToolsPage';
import DocumentToolsPageV2 from './pages/DocumentToolsPageV2';
import AdobeOnlyTestPage from './pages/AdobeOnlyTestPage';
import AdobeUsagePage from './pages/AdobeUsagePage';
import UserLayout from './components/layout/UserLayout';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider delayDuration={300}>
          <BrowserRouter>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 3000,
                style: {
                  background: '#363636',
                  color: '#fff',
                  padding: '16px',
                  borderRadius: '8px',
                },
                success: {
                  duration: 3000,
                  style: {
                    background: '#10b981',
                    color: '#fff',
                  },
                  iconTheme: {
                    primary: '#fff',
                    secondary: '#10b981',
                  },
                },
                error: {
                  duration: 5000,
                  style: {
                    background: '#ef4444',
                    color: '#fff',
                  },
                  iconTheme: {
                    primary: '#fff',
                    secondary: '#ef4444',
                  },
                },
                loading: {
                  style: {
                    background: '#3b82f6',
                    color: '#fff',
                  },
                },
              }}
            />
            <Routes>
              {/* Public Routes - No authentication required */}
              <Route path="/" element={<HomePage />} />
              <Route path="/pricing" element={<PublicPricingPage />} />
              <Route path="/workflow-review" element={<WorkflowReviewPage />} />
              <Route path="/demo/ocr" element={<OCRToWordPage />} />
              <Route path="/demo/adobe-test" element={<AdobeOnlyTestPage />} />
              <Route path="/login" element={<LoginPage />} />
              
              {/* User Routes - Requires authentication with shared layout */}
              <Route
                path="/user"
                element={
                  <ProtectedRoute>
                    <UserLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<UserDashboard />} />
                <Route path="profile" element={<UserProfilePage />} />
                <Route path="subscription" element={<UserSubscriptionPage />} />
                <Route path="pricing" element={<PricingPage />} />
                <Route path="billing" element={<BillingHistoryPage />} />
                <Route path="ocr-to-word" element={<OCRToWordPage />} />
                <Route path="kiem-tra-the-thuc" element={<KiemTraTheThuPage />} />
                <Route path="document-tools" element={<DocumentToolsPageV2 />} />
                <Route path="adobe-test" element={<AdobeOnlyTestPage />} />
              </Route>
              
              {/* Admin Routes - Requires superuser */}
              <Route
                path="/admin"
                element={
                  <AdminRoute>
                    <Layout />
                  </AdminRoute>
                }
              >
                <Route index element={<DashboardPage />} />
                <Route path="users" element={<UsersPage />} />
                <Route path="roles" element={<RolesPage />} />
                <Route path="logs" element={<ActivityLogsPage />} />
                <Route path="tools" element={<ToolsPage />} />
                <Route path="adobe-pdf" element={<AdobePdfPage />} />
                <Route path="mau-2c" element={<Mau2CPage />} />
                <Route path="kiem-tra-the-thuc" element={<KiemTraTheThuPage />} />
                <Route path="ocr-demo" element={<OCRDemoPage />} />
                <Route path="ocr-to-word" element={<OCRToWordPage />} />
                <Route path="text-to-word" element={<TextToWordPage />} />
                <Route path="data-visualization" element={<DataVisualizationPage />} />
                <Route path="ai-admin" element={<AIAdminDashboardPage />} />
                <Route path="ai-keys" element={<AIKeysManagementPage />} />
                <Route path="deployment" element={<DeploymentMonitor />} />
                <Route path="subscription" element={<UserSubscriptionPage />} />
                <Route path="pricing" element={<PricingPage />} />
                <Route path="billing" element={<BillingHistoryPage />} />
                <Route path="adobe-test" element={<AdobeOnlyTestPage />} />
                <Route path="adobe-usage" element={<AdobeUsagePage />} />
              </Route>
              
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
