import { useState, useEffect } from 'react';
import { 
  Settings, 
  Cpu, 
  Cloud, 
  CheckCircle, 
  AlertCircle,
  RefreshCw,
  Info
} from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface TechnologyPriority {
  operation: string;
  priority: string[];
  available_technologies: string[];
}

interface SettingsData {
  adobe_enabled: boolean;
  adobe_quota_info?: {
    monthly_limit: number;
    note: string;
  } | null;
  technology_priorities: {
    compress: string[];
    watermark: string[];
    pdf_info: string[];
  };
}

interface Technology {
  name: string;
  display_name: string;
  type: 'cloud' | 'local';
  capabilities: string[];
  quality_rating: string;
}

const SettingsPanel = () => {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [technologies, setTechnologies] = useState<Technology[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load current settings
  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/settings`);
      setSettings(response.data);
    } catch (error) {
      console.error('Failed to load settings:', error);
      showMessage('error', 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  // Load available technologies
  const loadTechnologies = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/settings/available-technologies`);
      setTechnologies(response.data);
    } catch (error) {
      console.error('Failed to load technologies:', error);
    }
  };

  useEffect(() => {
    loadSettings();
    loadTechnologies();
  }, []);

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  // Update technology priority
  const updatePriority = async (operation: string, priority: string[]) => {
    try {
      setSaving(true);
      await axios.post(`${API_BASE_URL}/settings/technology-priority`, {
        operation,
        priority: priority.join(','), // Convert array to string
      });
      
      // Reload settings
      await loadSettings();
      showMessage('success', `Updated ${operation} priority successfully`);
    } catch (error) {
      console.error('Failed to update priority:', error);
      showMessage('error', `Failed to update ${operation} priority`);
    } finally {
      setSaving(false);
    }
  };

  // Reset priorities to defaults
  const resetPriorities = async () => {
    if (!confirm('Reset all priorities to defaults (Adobe first)?')) {
      return;
    }

    try {
      setSaving(true);
      await axios.post(`${API_BASE_URL}/settings/reset-priorities`);
      await loadSettings();
      showMessage('success', 'All priorities reset to defaults');
    } catch (error) {
      console.error('Failed to reset priorities:', error);
      showMessage('error', 'Failed to reset priorities');
    } finally {
      setSaving(false);
    }
  };

  // Swap priority (move tech up/down)
  const swapPriority = (operation: string, currentPriority: string[], index: number) => {
    if (index === 0) return; // Can't move first item up

    const newPriority = [...currentPriority];
    [newPriority[index - 1], newPriority[index]] = [newPriority[index], newPriority[index - 1]];
    
    updatePriority(operation, newPriority);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        <AlertCircle className="w-6 h-6 mr-2" />
        Failed to load settings
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl p-8 shadow-xl">
        <div className="flex items-center gap-4">
          <Settings className="w-12 h-12" />
          <div>
            <h1 className="text-3xl font-bold">Technology Settings</h1>
            <p className="text-blue-100 mt-2">
              Configure processing priority and manage Adobe PDF Services integration
            </p>
          </div>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'success'
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-red-100 text-red-800 border border-red-300'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          {message.text}
        </div>
      )}

      {/* Adobe Status */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Cloud className="w-8 h-8 text-blue-500" />
            <div>
              <h2 className="text-xl font-bold text-gray-800">Adobe PDF Services</h2>
              <p className="text-gray-600">Cloud-based PDF processing with AI</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
              settings.adobe_enabled
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {settings.adobe_enabled ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Enabled</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5" />
                  <span className="font-semibold">Disabled</span>
                </>
              )}
            </div>
            
            {settings.adobe_enabled && settings.adobe_quota_info && (
              <div className="mt-2 text-sm text-gray-600">
                Monthly Limit: <span className="font-semibold">{settings.adobe_quota_info.monthly_limit}</span> transactions
                <div className="text-xs text-gray-500 mt-1">{settings.adobe_quota_info.note}</div>
              </div>
            )}
          </div>
        </div>

        {!settings.adobe_enabled && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-semibold mb-1">Adobe API is not configured</p>
                <p>To enable Adobe features, set <code className="bg-yellow-100 px-1 rounded">USE_ADOBE_PDF_API=true</code> in backend/.env</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Technology Priorities */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Processing Priorities</h2>
          <button
            onClick={resetPriorities}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${saving ? 'animate-spin' : ''}`} />
            Reset to Defaults
          </button>
        </div>

        <div className="space-y-6">
          {/* Compress Priority */}
          <PriorityControl
            label="PDF Compression"
            operation="compress"
            priority={settings.technology_priorities.compress}
            technologies={technologies}
            onUpdate={(newPriority) => updatePriority('compress', newPriority)}
            onSwap={(index) => swapPriority('compress', settings.technology_priorities.compress, index)}
            saving={saving}
          />

          {/* Watermark Priority */}
          <PriorityControl
            label="PDF Watermark"
            operation="watermark"
            priority={settings.technology_priorities.watermark}
            technologies={technologies}
            onUpdate={(newPriority) => updatePriority('watermark', newPriority)}
            onSwap={(index) => swapPriority('watermark', settings.technology_priorities.watermark, index)}
            saving={saving}
          />

          {/* PDF Info Priority */}
          <PriorityControl
            label="PDF Information"
            operation="pdf_info"
            priority={settings.technology_priorities.pdf_info}
            technologies={technologies}
            onUpdate={(newPriority) => updatePriority('pdf_info', newPriority)}
            onSwap={(index) => swapPriority('pdf_info', settings.technology_priorities.pdf_info, index)}
            saving={saving}
          />
        </div>
      </div>

      {/* Available Technologies */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Available Technologies</h2>
        
        <div className="grid md:grid-cols-2 gap-4">
          {technologies.map((tech) => (
            <TechnologyCard key={tech.name} technology={tech} />
          ))}
        </div>
      </div>
    </div>
  );
};

// Priority Control Component
interface PriorityControlProps {
  label: string;
  operation: string;
  priority: string[];
  technologies: Technology[];
  onUpdate: (newPriority: string[]) => void;
  onSwap: (index: number) => void;
  saving: boolean;
}

const PriorityControl = ({ label, priority, technologies, onSwap, saving }: PriorityControlProps) => {
  const getTechInfo = (techName: string) => {
    return technologies.find((t) => t.name === techName);
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h3 className="font-semibold text-lg text-gray-800 mb-3">{label}</h3>
      
      <div className="space-y-2">
        {priority.map((tech, index) => {
          const techInfo = getTechInfo(tech);
          
          return (
            <div
              key={tech}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className="text-gray-400 font-semibold">#{index + 1}</div>
                
                {techInfo?.type === 'cloud' ? (
                  <Cloud className="w-5 h-5 text-blue-500" />
                ) : (
                  <Cpu className="w-5 h-5 text-green-500" />
                )}
                
                <div>
                  <div className="font-semibold text-gray-800">
                    {techInfo?.display_name || tech}
                  </div>
                  <div className="text-xs text-gray-500">
                    {techInfo?.type === 'cloud' ? 'Cloud Service' : 'Local Processing'} • 
                    Quality: {techInfo?.quality_rating || 'N/A'}
                  </div>
                </div>
              </div>

              {index > 0 && (
                <button
                  onClick={() => onSwap(index)}
                  disabled={saving}
                  className="p-2 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
                  title="Move up"
                >
                  ↑
                </button>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <Info className="w-4 h-4 inline mr-1" />
          System will try <strong>{priority[0]}</strong> first, then fallback to <strong>{priority[1]}</strong> if it fails.
        </p>
      </div>
    </div>
  );
};

// Technology Card Component
interface TechnologyCardProps {
  technology: Technology;
}

const TechnologyCard = ({ technology }: TechnologyCardProps) => {
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        {technology.type === 'cloud' ? (
          <Cloud className="w-8 h-8 text-blue-500" />
        ) : (
          <Cpu className="w-8 h-8 text-green-500" />
        )}
        
        <div className="flex-1">
          <h3 className="font-bold text-gray-800">{technology.display_name}</h3>
          
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs px-2 py-1 rounded-full ${
              technology.type === 'cloud'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-green-100 text-green-700'
            }`}>
              {technology.type === 'cloud' ? 'Cloud' : 'Local'}
            </span>
            
            <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
              {technology.quality_rating}
            </span>
          </div>

          <div className="mt-2">
            <p className="text-xs text-gray-600 font-semibold mb-1">Capabilities:</p>
            <div className="flex flex-wrap gap-1">
              {technology.capabilities.map((cap) => (
                <span
                  key={cap}
                  className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded"
                >
                  {cap}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
