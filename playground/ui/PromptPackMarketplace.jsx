import React, { useEffect, useState } from 'react';

export default function PromptPackMarketplace() {
  const [packs, setPacks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('popularity');
  const [cart, setCart] = useState([]);

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'content', name: 'Content Generation' },
    { id: 'analysis', name: 'Analysis' },
    { id: 'creative', name: 'Creative Writing' },
    { id: 'business', name: 'Business' },
    { id: 'technical', name: 'Technical' }
  ];

  useEffect(() => {
    fetchMarketplacePacks();
  }, []);

  const fetchMarketplacePacks = async () => {
    try {
      const response = await fetch('/api/promptpacks/marketplace');
      const data = await response.json();
      setPacks(data.packs || []);
    } catch (error) {
      console.error('Error fetching marketplace packs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredPacks = packs
    .filter(pack => {
      const matchesSearch = pack.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           pack.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || pack.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'price':
          return (a.price || 0) - (b.price || 0);
        case 'popularity':
          return (b.downloads || 0) - (a.downloads || 0);
        case 'rating':
          return (b.rating || 0) - (a.rating || 0);
        default:
          return 0;
      }
    });

  const handlePurchase = async (pack) => {
    try {
      const response = await fetch('/api/payment/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ price_id: pack.stripe_price_id })
      });
      const data = await response.json();
      
      if (data.checkout_url) {
        window.open(data.checkout_url, '_blank');
      }
    } catch (error) {
      console.error('Error initiating purchase:', error);
      alert('Error processing purchase');
    }
  };

  const addToCart = (pack) => {
    setCart(prev => [...prev, pack]);
  };

  const removeFromCart = (packId) => {
    setCart(prev => prev.filter(p => p.id !== packId));
  };

  const isInCart = (packId) => {
    return cart.some(p => p.id === packId);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">PromptPack Marketplace</h2>
          <div className="flex items-center gap-4">
            <div className="relative">
              <span className="text-sm text-gray-600">Cart ({cart.length})</span>
              {cart.length > 0 && (
                <button className="ml-2 px-3 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600">
                  Checkout
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="md:col-span-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search prompt packs..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="popularity">Most Popular</option>
              <option value="rating">Highest Rated</option>
              <option value="price">Price: Low to High</option>
              <option value="name">Name A-Z</option>
            </select>
          </div>
        </div>

        {/* Featured Packs */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Featured Packs</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {filteredPacks.filter(p => p.featured).slice(0, 3).map(pack => (
              <div key={pack.id} className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-6">
                <div className="flex justify-between items-start mb-3">
                  <h4 className="text-lg font-semibold">{pack.name}</h4>
                  <span className="bg-yellow-400 text-yellow-900 px-2 py-1 text-xs rounded-full">Featured</span>
                </div>
                <p className="text-blue-100 text-sm mb-4">{pack.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-xl font-bold">${pack.price || 'Free'}</span>
                  <button
                    onClick={() => handlePurchase(pack)}
                    className="px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-medium"
                  >
                    Get Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* All Packs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredPacks.map(pack => (
            <div key={pack.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-800 truncate">{pack.name}</h3>
                <div className="flex items-center">
                  {pack.rating && (
                    <div className="flex items-center text-yellow-400 text-sm">
                      ★ {pack.rating.toFixed(1)}
                    </div>
                  )}
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-3 line-clamp-2">{pack.description}</p>

              <div className="flex flex-wrap gap-1 mb-3">
                {pack.tags?.slice(0, 2).map(tag => (
                  <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                    {tag}
                  </span>
                ))}
              </div>

              <div className="flex justify-between items-center text-xs text-gray-500 mb-3">
                <span>{pack.downloads || 0} downloads</span>
                <span>by {pack.author || 'Anonymous'}</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-lg font-bold text-gray-800">
                  {pack.price ? `$${pack.price}` : 'Free'}
                </span>
                <div className="flex gap-2">
                  {!isInCart(pack.id) ? (
                    <button
                      onClick={() => addToCart(pack)}
                      className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200"
                    >
                      Add to Cart
                    </button>
                  ) : (
                    <button
                      onClick={() => removeFromCart(pack.id)}
                      className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200"
                    >
                      Remove
                    </button>
                  )}
                  <button
                    onClick={() => handlePurchase(pack)}
                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                  >
                    {pack.price ? 'Buy Now' : 'Download'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredPacks.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🛍️</div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">No packs found</h3>
            <p className="text-gray-500">Try adjusting your search or filter criteria</p>
          </div>
        )}
      </div>
    </div>
  );
}
