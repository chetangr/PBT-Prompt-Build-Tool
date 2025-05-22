import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import PromptEditor from './PromptEditor';
import PromptGenerator from './PromptGenerator';
import PromptGallery from './PromptGallery';
import PromptPackMarketplace from './PromptPackMarketplace';
import EvalChart from './EvalChart';

export default function Dashboard() {
  const { user, signOut } = useAuth();
  const [activeTab, setActiveTab] = useState('gallery');
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [stats, setStats] = useState({
    totalPrompts: 0,
    totalEvaluations: 0,
    avgScore: 0,
    recentActivity: []
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('/api/stats/dashboard');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const tabs = [
    { id: 'gallery', name: 'Gallery', icon: '📚' },
    { id: 'editor', name: 'Editor', icon: '✏️' },
    { id: 'generator', name: 'Generator', icon: '🤖' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
    { id: 'marketplace', name: 'Marketplace', icon: '🛒' }
  ];

  const handlePromptSelect = (prompt) => {
    setSelectedPrompt(prompt);
    setActiveTab('editor');
  };

  const handleGeneratedPrompt = (prompt) => {
    setSelectedPrompt(prompt);
    setActiveTab('editor');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-8">
            Welcome to PBT
          </h2>
          <p className="text-gray-600 text-center mb-6">
            Please sign in to access the Prompt Build Tool dashboard.
          </p>
          <button
            onClick={() => window.location.href = '/login'}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Prompt Build Tool
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Welcome, {user.email}
              </div>
              <button
                onClick={signOut}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl">📝</div>
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.totalPrompts}
                </div>
                <div className="text-sm text-gray-600">Total Prompts</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl">🧪</div>
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.totalEvaluations}
                </div>
                <div className="text-sm text-gray-600">Evaluations</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl">⭐</div>
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.avgScore.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Avg Score</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl">🚀</div>
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.recentActivity?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Recent Activities</div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'gallery' && (
              <PromptGallery onSelectPrompt={handlePromptSelect} />
            )}

            {activeTab === 'editor' && (
              <PromptEditor
                initialPrompt={selectedPrompt?.yaml_content || ''}
                onSave={(content) => {
                  console.log('Saving prompt:', content);
                  // Handle save logic
                }}
              />
            )}

            {activeTab === 'generator' && (
              <PromptGenerator onGenerated={handleGeneratedPrompt} />
            )}

            {activeTab === 'analytics' && (
              <EvalChart />
            )}

            {activeTab === 'marketplace' && (
              <PromptPackMarketplace />
            )}
          </div>
        </div>

        {/* Recent Activity */}
        {stats.recentActivity && stats.recentActivity.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Recent Activity
            </h3>
            <div className="space-y-3">
              {stats.recentActivity.slice(0, 5).map((activity, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <div className="flex items-center">
                    <div className="text-sm text-gray-600">
                      {activity.description || 'Activity recorded'}
                    </div>
                  </div>
                  <div className="text-xs text-gray-400">
                    {new Date(activity.created_at).toLocaleDateString()}
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