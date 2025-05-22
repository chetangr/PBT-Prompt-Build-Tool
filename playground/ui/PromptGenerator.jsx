import React, { useState } from 'react';
import yaml from 'js-yaml';

export default function PromptGenerator({ onGenerated }) {
  const [goal, setGoal] = useState('');
  const [model, setModel] = useState('claude');
  const [style, setStyle] = useState('professional');
  const [variables, setVariables] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedPrompt, setGeneratedPrompt] = useState(null);
  const [yamlContent, setYamlContent] = useState('');

  const styles = [
    { id: 'professional', name: 'Professional' },
    { id: 'casual', name: 'Casual' },
    { id: 'technical', name: 'Technical' },
    { id: 'creative', name: 'Creative' },
    { id: 'concise', name: 'Concise' },
    { id: 'detailed', name: 'Detailed' }
  ];

  const models = [
    { id: 'claude', name: 'Claude 3 Sonnet' },
    { id: 'openai', name: 'GPT-4' }
  ];

  const handleGenerate = async () => {
    if (!goal.trim()) return;

    setIsLoading(true);
    try {
      const variableList = variables.split(',').map(v => v.trim()).filter(v => v);
      
      const response = await fetch('/api/promptgen/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal,
          model,
          style,
          variables: variableList
        })
      });

      const data = await response.json();
      
      if (data.success && data.prompt_yaml) {
        setGeneratedPrompt(data.prompt_yaml);
        setYamlContent(yaml.dump(data.prompt_yaml, { indent: 2 }));
        if (onGenerated) {
          onGenerated(data.prompt_yaml);
        }
      } else {
        setYamlContent(data.raw_content || 'Error generating prompt');
      }
    } catch (error) {
      console.error('Error generating prompt:', error);
      setYamlContent('Error: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSavePrompt = async () => {
    if (!generatedPrompt) return;

    try {
      // Here you would typically save to your backend
      const response = await fetch('/api/promptpacks/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: generatedPrompt.name,
          version: generatedPrompt.version,
          content: yamlContent,
          description: generatedPrompt.description,
          tags: generatedPrompt.tags || []
        })
      });

      if (response.ok) {
        alert('Prompt saved successfully!');
      }
    } catch (error) {
      console.error('Error saving prompt:', error);
      alert('Error saving prompt');
    }
  };

  const downloadYaml = () => {
    if (!yamlContent) return;

    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${generatedPrompt?.name || 'prompt'}.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Prompt Generator</h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Goal Description
              </label>
              <textarea
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="Describe what you want your prompt to accomplish. E.g., 'Summarize sarcastic tweets into clear meaning'"
                className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  {models.map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Style
                </label>
                <select
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  {styles.map(s => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Variables (comma-separated)
              </label>
              <input
                type="text"
                value={variables}
                onChange={(e) => setVariables(e.target.value)}
                placeholder="tweet, user_context, tone"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Specify input variables your prompt should accept
              </p>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isLoading || !goal.trim()}
              className="w-full px-4 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Generating...' : 'Generate Prompt'}
            </button>

            {/* Example Goals */}
            <div className="mt-4 p-4 bg-gray-50 rounded-md">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Example Goals:</h4>
              <ul className="text-xs text-gray-600 space-y-1">
                <li>• "Generate product descriptions from features"</li>
                <li>• "Translate technical docs to user-friendly language"</li>
                <li>• "Create social media posts from blog content"</li>
                <li>• "Extract key insights from customer feedback"</li>
              </ul>
            </div>
          </div>

          {/* Generated Output */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                Generated Prompt YAML
              </label>
              {yamlContent && (
                <div className="flex gap-2">
                  <button
                    onClick={downloadYaml}
                    className="px-3 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
                  >
                    Download
                  </button>
                  <button
                    onClick={handleSavePrompt}
                    className="px-3 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    Save
                  </button>
                </div>
              )}
            </div>

            <div className="h-96 border border-gray-300 rounded-md overflow-auto">
              {yamlContent ? (
                <pre className="p-4 text-xs bg-gray-50 h-full">{yamlContent}</pre>
              ) : (
                <div className="p-4 text-gray-500 text-center">
                  Generated prompt will appear here...
                </div>
              )}
            </div>

            {/* Prompt Preview */}
            {generatedPrompt && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                <h4 className="text-sm font-medium text-blue-800 mb-2">Quick Preview:</h4>
                <div className="text-xs text-blue-700">
                  <p><strong>Name:</strong> {generatedPrompt.name}</p>
                  <p><strong>Description:</strong> {generatedPrompt.description}</p>
                  {generatedPrompt.variables && (
                    <p><strong>Variables:</strong> {generatedPrompt.variables.join(', ')}</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}