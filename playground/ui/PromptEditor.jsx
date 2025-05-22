import React, { useState, useEffect } from 'react';
import { Diff2Html } from 'diff2html';
import 'diff2html/bundles/css/diff2html.min.css';

export default function PromptEditor({ initialPrompt = '', onSave, onTest }) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [variables, setVariables] = useState({});
  const [renderedPrompt, setRenderedPrompt] = useState('');
  const [isComparing, setIsComparing] = useState(false);
  const [originalPrompt, setOriginalPrompt] = useState(initialPrompt);
  const [selectedModels, setSelectedModels] = useState(['claude', 'gpt-4']);
  const [modelOutputs, setModelOutputs] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const models = [
    { id: 'claude', name: 'Claude 3 Sonnet' },
    { id: 'gpt-4', name: 'GPT-4' },
    { id: 'mistral', name: 'Mistral' },
    { id: 'ollama', name: 'Ollama (Local)' }
  ];

  useEffect(() => {
    renderPrompt();
  }, [prompt, variables]);

  const extractVariables = (text) => {
    const matches = text.match(/\{\{([^}]+)\}\}/g);
    if (!matches) return [];
    return [...new Set(matches.map(match => match.slice(2, -2).trim()))];
  };

  const renderPrompt = async () => {
    try {
      const response = await fetch('/api/promptgen/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template: prompt, variables })
      });
      const data = await response.json();
      setRenderedPrompt(data.rendered || prompt);
    } catch (error) {
      console.error('Error rendering prompt:', error);
      setRenderedPrompt(prompt);
    }
  };

  const handleVariableChange = (varName, value) => {
    setVariables(prev => ({ ...prev, [varName]: value }));
  };

  const compareModels = async () => {
    if (!renderedPrompt.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/promptgen/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt: renderedPrompt, 
          models: selectedModels 
        })
      });
      const data = await response.json();
      setModelOutputs(data.results || {});
    } catch (error) {
      console.error('Error comparing models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateDiff = () => {
    if (!isComparing) return '';
    
    const createFile = (content, filename) => `--- a/${filename}\n+++ b/${filename}\n@@ -1,1 +1,1 @@\n-${originalPrompt}\n+${prompt}`;
    const diffString = createFile(prompt, 'prompt.txt');
    
    return Diff2Html.html(diffString, {
      drawFileList: false,
      matching: 'lines',
      outputFormat: 'side-by-side'
    });
  };

  const detectedVars = extractVariables(prompt);

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Prompt Editor</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setIsComparing(!isComparing)}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              {isComparing ? 'Hide Diff' : 'Show Diff'}
            </button>
            {onSave && (
              <button
                onClick={() => onSave(prompt)}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Save
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Editor */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prompt Template
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your prompt template here. Use {{variable}} for dynamic values."
                className="w-full h-64 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Variables */}
            {detectedVars.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Variables
                </label>
                <div className="space-y-2">
                  {detectedVars.map(varName => (
                    <div key={varName}>
                      <label className="block text-xs text-gray-600">{varName}</label>
                      <input
                        type="text"
                        value={variables[varName] || ''}
                        onChange={(e) => handleVariableChange(varName, e.target.value)}
                        placeholder={`Enter value for ${varName}`}
                        className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Preview */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rendered Preview
              </label>
              <div className="h-64 p-3 bg-gray-50 border border-gray-300 rounded-md overflow-auto">
                <pre className="whitespace-pre-wrap text-sm">{renderedPrompt}</pre>
              </div>
            </div>

            {/* Model Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Compare Models
              </label>
              <div className="grid grid-cols-2 gap-2 mb-3">
                {models.map(model => (
                  <label key={model.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedModels.includes(model.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedModels(prev => [...prev, model.id]);
                        } else {
                          setSelectedModels(prev => prev.filter(id => id !== model.id));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">{model.name}</span>
                  </label>
                ))}
              </div>
              <button
                onClick={compareModels}
                disabled={isLoading || selectedModels.length === 0}
                className="w-full px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
              >
                {isLoading ? 'Comparing...' : 'Compare Models'}
              </button>
            </div>
          </div>
        </div>

        {/* Diff View */}
        {isComparing && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Diff View</h3>
            <div 
              className="border border-gray-300 rounded-md overflow-auto"
              dangerouslySetInnerHTML={{ __html: generateDiff() }}
            />
          </div>
        )}

        {/* Model Outputs */}
        {Object.keys(modelOutputs).length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-4">Model Comparison Results</h3>
            <div className="grid gap-4">
              {Object.entries(modelOutputs).map(([model, output]) => (
                <div key={model} className="border border-gray-300 rounded-lg p-4">
                  <h4 className="font-medium text-gray-800 mb-2">{model}</h4>
                  <div className="bg-gray-50 p-3 rounded text-sm">
                    <pre className="whitespace-pre-wrap">{output}</pre>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}