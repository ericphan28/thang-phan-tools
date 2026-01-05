/**
 * Gemini Keys Management Page (Admin Only)
 * Dashboard + Keys Management + Usage Logs + Rotation History
 */
import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Key, BarChart3, Activity, RotateCw } from 'lucide-react';

// Import tab components
import DashboardTab from '../components/gemini-keys/DashboardTab';
import KeysManagementTab from '../components/gemini-keys/KeysManagementTab';
import UsageLogsTab from '../components/gemini-keys/UsageLogsTab';
import RotationLogsTab from '../components/gemini-keys/RotationLogsTab';

export default function GeminiKeysManagementPage() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
            <Key className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Gemini Keys Management</h1>
            <p className="text-muted-foreground">
              Quản lý API keys, quota, usage tracking & auto-rotation
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid">
          <TabsTrigger value="dashboard" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            <span className="hidden sm:inline">Dashboard</span>
          </TabsTrigger>
          <TabsTrigger value="keys" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            <span className="hidden sm:inline">Keys</span>
          </TabsTrigger>
          <TabsTrigger value="usage" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            <span className="hidden sm:inline">Usage</span>
          </TabsTrigger>
          <TabsTrigger value="rotations" className="flex items-center gap-2">
            <RotateCw className="h-4 w-4" />
            <span className="hidden sm:inline">Rotations</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-4">
          <DashboardTab />
        </TabsContent>

        <TabsContent value="keys" className="space-y-4">
          <KeysManagementTab />
        </TabsContent>

        <TabsContent value="usage" className="space-y-4">
          <UsageLogsTab />
        </TabsContent>

        <TabsContent value="rotations" className="space-y-4">
          <RotationLogsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
