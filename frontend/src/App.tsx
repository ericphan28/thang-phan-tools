import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { TooltipProvider } from './components/ui/tooltip';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/layout/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import RolesPage from './pages/RolesPage';
import ActivityLogsPage from './pages/ActivityLogsPage';
import ToolsPage from './pages/ToolsPage';
import AdobePdfPage from './pages/AdobePdfPage';
import Mau2CPage from './pages/Mau2CPage';
import OCRDemoPage from './pages/OCRDemoPage';
import AIAdminDashboardPage from './pages/AIAdminDashboardPage';
import AIKeysManagementPage from './pages/AIKeysManagementPage';
import TextToWordPage from './pages/TextToWordPage';
import DataVisualizationPage from './pages/DataVisualizationPage';
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
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="roles" element={<RolesPage />} />
              <Route path="logs" element={<ActivityLogsPage />} />
              <Route path="tools" element={<ToolsPage />} />
              <Route path="adobe-pdf" element={<AdobePdfPage />} />
              <Route path="mau-2c" element={<Mau2CPage />} />
              <Route path="ocr-demo" element={<OCRDemoPage />} />
              <Route path="text-to-word" element={<TextToWordPage />} />
              <Route path="data-visualization" element={<DataVisualizationPage />} />
              <Route path="ai-admin" element={<AIAdminDashboardPage />} />
              <Route path="ai-keys" element={<AIKeysManagementPage />} />
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
