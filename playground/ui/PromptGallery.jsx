import React, { useState, useEffect } from 'react';

export default function PromptGallery({ onSelectPrompt }) {
  const [prompts, setPrompts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('name');

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'content', name: 'Content Generation' },
    { id: 'analysis', name: 'Analysis & Insights' },
    { id: 'translation', name: 'Translation' },
    { id: 'summarization', name: 'Summarization' },
    { id: 'creative', name: 'Creative Writing' },
    { id: 'technical', name: 'Technical' },
    { id: 'business', name: 'Business' }
  ];

  const sortOptions = [
    { id: 'name', name: 'Name' },
    { id: 'created_at', name: 'Date Created' },
    { id: 'updated_at', name: 'Last Updated' },
    { id: 'popularity', name: 'Popularity' }
  ];

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      const response = await fetch('/api/promptpacks/list');
      const data = await response.json();
      setPrompts(data.prompts || []);
    } catch (error) {
      console.error('Error fetching prompts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredPrompts = prompts
    .filter(prompt => {
      const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           prompt.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || 
                             prompt.tags?.includes(selectedCategory) ||
                             prompt.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created_at':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'updated_at':
          return new Date(b.updated_at) - new Date(a.updated_at);
        case 'popularity':
          return (b.stars || 0) - (a.stars || 0);
        default:
          return 0;
      }
    });

  const handleStarPrompt = async (promptId) => {
    try {
      await fetch(`/api/star/${promptId}`, { method: 'POST' });
      fetchPrompts(); // Refresh to show updated star count
    } catch (error) {
      console.error('Error starring prompt:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Prompt Gallery</h2>
          <div className="text-sm text-gray-600">
            {filteredPrompts.length} of {prompts.length} prompts
          </div>
        </div>

        {/* Filters and Search */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search prompts..."
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              {sortOptions.map(opt => (
                <option key={opt.id} value={opt.id}>{opt.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Prompt Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPrompts.map(prompt => (
            <div key={prompt.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-800 truncate">{prompt.name}</h3>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleStarPrompt(prompt.id)}
                    className="text-yellow-400 hover:text-yellow-500"
                  >
                    ⭐
                  </button>
                  <span className="text-xs text-gray-500">{prompt.stars || 0}</span>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-3 line-clamp-2">{prompt.description}</p>

              <div className="flex flex-wrap gap-1 mb-3">
                {prompt.tags?.slice(0, 3).map(tag => (
                  <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                    {tag}
                  </span>
                ))}
                {prompt.tags?.length > 3 && (
                  <span className="text-xs text-gray-500">+{prompt.tags.length - 3} more</span>
                )}
              </div>

              <div className="flex justify-between items-center text-xs text-gray-500 mb-3">
                <span>v{prompt.version}</span>
                <span>{new Date(prompt.updated_at).toLocaleDateString()}</span>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => onSelectPrompt && onSelectPrompt(prompt)}
                  className="flex-1 px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                >
                  Open
                </button>
                <button className="px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200">
                  Preview
                </button>
              </div>

              {/* Preview Modal would go here */}
            </div>
          ))}
        </div>

        {filteredPrompts.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📝</div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">No prompts found</h3>
            <p className="text-gray-500">Try adjusting your search or filter criteria</p>
          </div>
        )}

        {/* Pagination would go here for large datasets */}
      </div>
    </div>
  );
}