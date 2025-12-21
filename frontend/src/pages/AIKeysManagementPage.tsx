import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import * as Tooltip from '@radix-ui/react-tooltip';
import { 
  getAPIKeys, 
  getProviders, 
  createAPIKey, 
  updateAPIKey, 
  deleteAPIKey, 
  testAPIKey,
  type AIProviderKey,
  type AIProvider 
} from '../services/aiAdminService';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Key, 
  AlertCircle, 
  Check, 
  X,
  TestTube
} from 'lucide-react';

export default function AIKeysManagementPage() {
  const [keys, setKeys] = useState<AIProviderKey[]>([]);
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingKey, setEditingKey] = useState<AIProviderKey | null>(null);
  const [testingKey, setTestingKey] = useState<number | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [keysRes, providersRes] = await Promise.all([
        getAPIKeys(),
        getProviders()
      ]);
      setKeys(keysRes.data);
      setProviders(providersRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTestKey = async (keyId: number) => {
    setTestingKey(keyId);
    try {
      const res = await testAPIKey(keyId);
      alert(`Test result: ${res.data.status}\n${res.data.message || ''}`);
    } catch (err: any) {
      alert(`Test failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setTestingKey(null);
    }
  };

  const handleDeleteKey = async (keyId: number, keyName: string) => {
    if (!confirm(`Xóa API key "${keyName}"?`)) return;
    
    try {
      await deleteAPIKey(keyId);
      await fetchData();
    } catch (err: any) {
      alert(`Delete failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">API Keys Management</h1>
          <p className="text-gray-600 mt-1">Quản lý API keys cho Gemini, Claude, và Adobe</p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add API Key
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* API Keys List */}
      <div className="grid gap-4">
        {keys.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <Key className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-600 mb-4">Chưa có API keys nào</p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add First API Key
              </Button>
            </CardContent>
          </Card>
        ) : (
          keys.map((key) => (
            <Card key={key.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${key.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <span className="capitalize">{key.provider}</span>
                        {key.is_primary && (
                          <Badge variant="default" className="bg-blue-500">Primary</Badge>
                        )}
                      </CardTitle>
                      <CardDescription>{key.key_name}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleTestKey(key.id)}
                      disabled={testingKey === key.id}
                    >
                      <TestTube className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditingKey(key)}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteKey(key.id, key.key_name)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600 w-24">API Key:</span>
                    <code className="flex-1 bg-gray-100 px-3 py-1 rounded text-sm font-mono">
                      {key.api_key_masked || '•••••••••'}
                    </code>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Status</p>
                      <Badge variant={key.is_active ? "default" : "secondary"}>
                        {key.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-gray-600 cursor-help" title="Giới hạn chi phí tối đa hàng tháng (USD)">Monthly Limit ℹ️</p>
                      <p className="font-semibold">
                        {key.monthly_limit ? `$${key.monthly_limit.toFixed(2)}` : 'No limit'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600 cursor-help" title="Số requests tối đa mỗi phút">Rate Limit ℹ️</p>
                      <p className="font-semibold">
                        {key.rate_limit_rpm ? `${key.rate_limit_rpm} RPM` : 'No limit'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600 cursor-help" title="Số lần gọi API bị lỗi">Errors ℹ️</p>
                      <p className="font-semibold text-red-600">{key.error_count}</p>
                    </div>
                  </div>

                  <div className="text-xs text-gray-500">
                    Created: {new Date(key.created_at).toLocaleString()}
                    {key.last_used_at && ` • Last used: ${new Date(key.last_used_at).toLocaleString()}`}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || editingKey) && (
        <AddEditKeyModal
          providers={providers}
          existingKey={editingKey}
          onClose={() => {
            setShowAddModal(false);
            setEditingKey(null);
          }}
          onSuccess={() => {
            setShowAddModal(false);
            setEditingKey(null);
            fetchData();
          }}
        />
      )}
    </div>
  );
}

// Add/Edit Modal Component
function AddEditKeyModal({ 
  providers, 
  existingKey, 
  onClose, 
  onSuccess 
}: { 
  providers: AIProvider[];
  existingKey: AIProviderKey | null;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [formData, setFormData] = useState({
    provider: existingKey?.provider || 'gemini',
    key_name: existingKey?.key_name || '',
    api_key: existingKey?.api_key || '',
    is_primary: existingKey?.is_primary || false,
    is_active: existingKey?.is_active ?? true,
    monthly_limit: existingKey?.monthly_limit || '',
    rate_limit_rpm: existingKey?.rate_limit_rpm || '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      if (existingKey) {
        await updateAPIKey(existingKey.id, {
          key_name: formData.key_name,
          is_primary: formData.is_primary,
          is_active: formData.is_active,
          monthly_limit: formData.monthly_limit ? Number(formData.monthly_limit) : undefined,
          rate_limit_rpm: formData.rate_limit_rpm ? Number(formData.rate_limit_rpm) : undefined,
        });
      } else {
        await createAPIKey({
          ...formData,
          monthly_limit: formData.monthly_limit ? Number(formData.monthly_limit) : undefined,
          rate_limit_rpm: formData.rate_limit_rpm ? Number(formData.rate_limit_rpm) : undefined,
        });
      }
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Operation failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle>{existingKey ? 'Edit API Key' : 'Add New API Key'}</CardTitle>
          <CardDescription>
            {existingKey ? 'Update API key configuration' : 'Add a new API key for AI provider'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded p-3 text-red-700 text-sm">
                {error}
              </div>
            )}

            {!existingKey && (
              <div>
                <label className="block text-sm font-medium mb-2">Provider</label>
                <select
                  className="w-full border rounded-lg px-3 py-2"
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  required
                >
                  {providers.map(p => (
                    <option key={p.name} value={p.name}>{p.name}</option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">Key Name</label>
              <Input
                placeholder="e.g., Production Key, Test Key"
                value={formData.key_name}
                onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
                required
              />
            </div>

            {!existingKey && (
              <div>
                <label className="block text-sm font-medium mb-2">API Key</label>
                <Input
                  type="password"
                  placeholder="Your API key"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  required
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Monthly Limit ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="No limit"
                  value={formData.monthly_limit}
                  onChange={(e) => setFormData({ ...formData, monthly_limit: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Rate Limit (RPM)</label>
                <Input
                  type="number"
                  placeholder="No limit"
                  value={formData.rate_limit_rpm}
                  onChange={(e) => setFormData({ ...formData, rate_limit_rpm: e.target.value })}
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_primary}
                  onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                  className="w-4 h-4"
                />
                <span className="text-sm">Set as primary key</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4"
                />
                <span className="text-sm">Active</span>
              </label>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Saving...' : existingKey ? 'Update' : 'Create'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
