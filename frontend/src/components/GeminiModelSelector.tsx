import React, { useState, useEffect } from 'react';
import { Check, Info, Zap, DollarSign, Star, Loader2 } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";

interface GeminiModel {
  model_id: string;
  name: string;
  series: string;
  description: string;
  features: string[];
  use_cases: string[];
  quality: number;
  speed: number;
  pricing: {
    input: number;
    output: number;
  };
  status: 'stable' | 'preview' | 'experimental' | 'legacy';
  badge?: string;
  is_default?: boolean;
  recommended_for: string[];
}

interface GeminiModelsResponse {
  models: GeminiModel[];
  default_model: string;
  total_count: number;
}

interface GeminiModelSelectorProps {
  value?: string;
  onChange: (modelId: string) => void;
  onModelInfoChange?: (model: GeminiModel | null) => void;
  showDetails?: boolean;
  disabled?: boolean;
}

export function GeminiModelSelector({ 
  value, 
  onChange, 
  onModelInfoChange,
  showDetails = true,
  disabled = false 
}: GeminiModelSelectorProps) {
  const [models, setModels] = useState<GeminiModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState<GeminiModel | null>(null);

  // Fetch available models
  useEffect(() => {
    async function fetchModels() {
      try {
        const response = await fetch('http://localhost:8000/api/v1/documents/gemini/models');
        const data: GeminiModelsResponse = await response.json();
        
        setModels(data.models);
        
        // Set default or initial value
        const initial = value || data.default_model;
        const initialModel = data.models.find(m => m.model_id === initial);
        if (initialModel) {
          setSelectedModel(initialModel);
          if (!value) {
            onChange(initial);
          }
        }
      } catch (error) {
        console.error('Failed to fetch Gemini models:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchModels();
  }, []);

  // Update selected model when value changes
  useEffect(() => {
    if (value && models.length > 0) {
      const model = models.find(m => m.model_id === value);
      setSelectedModel(model || null);
      if (onModelInfoChange) {
        onModelInfoChange(model || null);
      }
    }
  }, [value, models, onModelInfoChange]);

  const handleChange = (modelId: string) => {
    const model = models.find(m => m.model_id === modelId);
    setSelectedModel(model || null);
    onChange(modelId);
    if (onModelInfoChange) {
      onModelInfoChange(model || null);
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'stable': return 'bg-green-100 text-green-800';
      case 'preview': return 'bg-blue-100 text-blue-800';
      case 'experimental': return 'bg-yellow-100 text-yellow-800';
      case 'legacy': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const renderQualityStars = (quality: number) => {
    return (
      <div className="flex items-center gap-0.5">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-3 h-3 ${
              i < quality / 2 ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-xs text-gray-600">{quality}/10</span>
      </div>
    );
  };

  const renderSpeedIndicator = (speed: number) => {
    return (
      <div className="flex items-center gap-1">
        {[...Array(5)].map((_, i) => (
          <Zap
            key={i}
            className={`w-3 h-3 ${
              i < speed / 2 ? 'fill-blue-400 text-blue-400' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-xs text-gray-600">{speed}/10</span>
      </div>
    );
  };

  const calculateCostPer10kPages = (pricing: { input: number; output: number }) => {
    // Assume 2000 tokens input + 500 tokens output per page
    const inputCost = (2000 * 10000 / 1_000_000) * pricing.input;
    const outputCost = (500 * 10000 / 1_000_000) * pricing.output;
    return (inputCost + outputCost).toFixed(2);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-500">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm">Loading models...</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Model Selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Gemini Model
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className="inline w-4 h-4 ml-1 text-gray-400 cursor-help" />
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">
                <p>Choose the AI model for PDF conversion. Higher quality models cost more but provide better results.</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </label>

        <Select value={value} onValueChange={handleChange} disabled={disabled}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a model" />
          </SelectTrigger>
          <SelectContent className="max-h-96">
            {models.map((model) => (
              <SelectItem key={model.model_id} value={model.model_id}>
                <div className="flex items-center justify-between gap-3 py-1">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{model.name}</span>
                      {model.is_default && (
                        <Badge variant="secondary" className="text-xs">Default</Badge>
                      )}
                      {model.badge && (
                        <span className="text-xs">{model.badge}</span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5 truncate">
                      {model.description}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${getStatusBadgeColor(model.status)}`}>
                      {model.status}
                    </span>
                  </div>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Model Details */}
      {showDetails && selectedModel && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-3 border border-gray-200">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-gray-900">{selectedModel.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{selectedModel.description}</p>
            </div>
            <Badge variant={selectedModel.status === 'stable' ? 'default' : 'secondary'}>
              {selectedModel.status}
            </Badge>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white rounded p-3 border border-gray-200">
              <div className="text-xs text-gray-500 mb-1">Quality</div>
              {renderQualityStars(selectedModel.quality)}
            </div>
            <div className="bg-white rounded p-3 border border-gray-200">
              <div className="text-xs text-gray-500 mb-1">Speed</div>
              {renderSpeedIndicator(selectedModel.speed)}
            </div>
          </div>

          {/* Pricing */}
          <div className="bg-white rounded p-3 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Pricing</span>
            </div>
            <div className="space-y-1 text-xs text-gray-600">
              <div>Input: ${selectedModel.pricing.input} per 1M tokens</div>
              <div>Output: ${selectedModel.pricing.output} per 1M tokens</div>
              <div className="pt-1 border-t border-gray-200 mt-2">
                <span className="font-medium">~${calculateCostPer10kPages(selectedModel.pricing)}</span> for 10,000 pages
              </div>
            </div>
          </div>

          {/* Features */}
          {selectedModel.features && selectedModel.features.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-700 mb-2">Key Features:</div>
              <div className="flex flex-wrap gap-1.5">
                {selectedModel.features.map((feature, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs">
                    {feature}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Use Cases */}
          {selectedModel.use_cases && selectedModel.use_cases.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-700 mb-2">Best For:</div>
              <ul className="text-xs text-gray-600 space-y-1">
                {selectedModel.use_cases.slice(0, 3).map((useCase, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{useCase}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
